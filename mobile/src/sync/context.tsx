/**
 * Keeping the device and the account in step.
 *
 * The rule the whole module follows: **the device is the source of truth for
 * reading, the account is a mirror.** Every screen reads from AsyncStorage
 * exactly as it did before accounts existed, so the app works signed out,
 * offline, and in a build with no Supabase project configured. Sync fills that
 * local store on a new phone and copies changes upward; it is never in the path
 * of showing someone their own chart.
 *
 * That is also why nothing here keeps a queue of pending writes. Each merge is a
 * union or a comparison of timestamps, so running it twice does what running it
 * once did, and a push that failed while the phone was in a tunnel is simply
 * noticed as missing by the next pass. A retry queue would be a second, harder
 * copy of the same guarantee.
 *
 * The provider resolves to a definite `ready` before anything routes on it, for
 * the reason `app/index.tsx` explains: a signed-in user opening a fresh install
 * must not be shown onboarding for a frame while their chart is still on its way
 * down. Failure counts as settled — a bad network should delay the app, not
 * hold it.
 */

import { ReactNode, createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { AppState } from 'react-native';

import { useAuth } from '../auth/context';
import {
  birthDetailsSavedAt,
  clearSyncIds,
  loadBirthDetails,
  loadProgress,
  loadSyncIds,
  rememberChartId,
  rememberConversationId,
  replaceProgress,
  saveBirthDetailsFromRemote,
} from '../api/storage';
import { clearChartCaches } from '../api/cache';
import type { BirthDetails, Language } from '../api/types';
import { fetchPrimaryChart, pushPrimaryChart, sameChart } from './charts';
import { clearRemoteProgress, fetchProgress, pushProgress } from './progress';
import {
  appendTurn,
  createConversation,
  deleteConversation,
  fetchTurns,
  findConversation,
  setConversationLanguage,
  type StoredTurn,
} from './chat';

/** How stale a sync may be before returning to the app refreshes it. */
const REFRESH_AFTER_MS = 5 * 60 * 1000;

type Status = 'off' | 'syncing' | 'ok' | 'error';

type SyncState = {
  /** Signed in, with a configured project — i.e. there is an account to mirror into. */
  enabled: boolean;
  /** True once the first pass has settled, whatever the outcome. */
  ready: boolean;
  status: Status;
  lastSyncedAt: number | null;
  error: string | null;
  /** The account's row for the chart on this device, when known. */
  chartId: string | null;
  syncNow: () => Promise<void>;
  /** Write-through helpers. Each is a no-op signed out and never throws. */
  pushBirth: (details: BirthDetails) => Promise<void>;
  pushChapterRead: (slug: string) => Promise<void>;
  pushProgressReset: () => Promise<void>;
  /** The stored conversation about this chart, oldest turn first. */
  loadChatHistory: () => Promise<StoredTurn[]>;
  recordTurn: (turn: StoredTurn, language: Language) => Promise<void>;
  clearChatHistory: () => Promise<void>;
};

const SyncContext = createContext<SyncState | null>(null);

function message(error: unknown): string {
  if (error instanceof Error) return error.message;
  return 'Could not reach your account.';
}

export function SyncProvider({ children }: { children: ReactNode }) {
  const { user, available } = useAuth();
  const userId = user?.id ?? null;
  const enabled = available && userId !== null;

  // Which account has had a pass settle. Derived rather than stored as its own
  // `ready` flag so that the instant a session appears, `ready` is already false
  // in the same render — a flag set from an effect is one render too late, and
  // that render is exactly the one where `app/index.tsx` would read an empty
  // local store and send a signed-in user to onboarding.
  const [settledFor, setSettledFor] = useState<string | null>(null);
  const ready = !enabled || settledFor === userId;

  const [status, setStatus] = useState<Status>(enabled ? 'syncing' : 'off');
  const [lastSyncedAt, setLastSyncedAt] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [chartId, setChartId] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Guards a second pass from starting while one is in flight — two merges
  // racing would each see the other's half-finished state.
  const running = useRef(false);
  const lastAttempt = useRef<{ at: number; ok: boolean } | null>(null);

  // The language the conversation was last recorded as being held in, so
  // switching pills mid-thread costs one update rather than one per message.
  const conversationLanguage = useRef<Language | null>(null);
  // Two questions asked before either has an answer would each find no
  // conversation and each create one. The in-flight promise is shared instead.
  const opening = useRef<Promise<string | null> | null>(null);
  // Message inserts run one after another, never in parallel. `created_at` is
  // set by the server as each row lands, so a question whose conversation still
  // had to be created could otherwise be stamped *after* the answer to it and
  // read back in the wrong order.
  const writes = useRef<Promise<unknown>>(Promise.resolve());

  // The rows from the last session, so the reading screen can find its
  // conversation before the first sync of this launch has finished.
  useEffect(() => {
    loadSyncIds().then((ids) => {
      setChartId((current) => current ?? ids.chartId);
      setConversationId((current) => current ?? ids.conversationId);
    });
  }, []);

  const run = useCallback(async (id: string) => {
    if (running.current) return;
    running.current = true;
    setStatus('syncing');

    try {
      const [localBirth, localSavedAt, remote] = await Promise.all([
        loadBirthDetails(),
        birthDetailsSavedAt(),
        fetchPrimaryChart(id),
      ]);

      // --- Birth details: newest edit wins ---------------------------------
      //
      // Not "the account wins" and not "the phone wins". Either of those
      // silently reverts a real edit made on the other device, and birth details
      // are exactly the field someone goes back to correct after noticing their
      // birth time was a digit out.
      //
      // A local copy written before this stamp existed reads as null and yields
      // to the account. That cannot lose an edit: nothing has ever been written
      // upstream, so there is no account copy for it to lose to.
      let resolvedChartId: string | null = null;

      // Pulling a different chart drops the caches computed from the old one,
      // the same as changing birth details in settings does. Their contents were
      // computed for the chart being replaced, and the keys they are filed under
      // can never be asked for again.
      const pull = async (): Promise<string> => {
        if (localBirth) await clearChartCaches();
        await saveBirthDetailsFromRemote(remote!.birth, remote!.savedAt);
        return remote!.id;
      };

      if (localBirth && !remote) {
        resolvedChartId = await pushPrimaryChart(id, localBirth);
      } else if (!localBirth && remote) {
        resolvedChartId = await pull();
      } else if (localBirth && remote) {
        if (sameChart(localBirth, remote.birth)) {
          resolvedChartId = remote.id;
        } else if ((localSavedAt ?? 0) >= remote.savedAt) {
          resolvedChartId = await pushPrimaryChart(id, localBirth);
        } else {
          resolvedChartId = await pull();
        }
      }

      // A different chart drops the conversation with it — see `rememberChartId`.
      const ids = await rememberChartId(resolvedChartId);
      setChartId(ids.chartId);
      setConversationId(ids.conversationId);
      if (!ids.conversationId) conversationLanguage.current = null;

      // --- Course progress: union both ways --------------------------------
      const [localProgress, remoteProgress] = await Promise.all([
        loadProgress(),
        fetchProgress(id),
      ]);

      const missingLocally = remoteProgress.filter((slug) => !localProgress.includes(slug));
      const missingRemotely = localProgress.filter((slug) => !remoteProgress.includes(slug));

      if (missingLocally.length) await replaceProgress([...localProgress, ...missingLocally]);
      if (missingRemotely.length) await pushProgress(id, missingRemotely);

      const at = Date.now();
      lastAttempt.current = { at, ok: true };
      setLastSyncedAt(at);
      setError(null);
      setStatus('ok');
    } catch (err) {
      lastAttempt.current = { at: Date.now(), ok: false };
      setError(message(err));
      setStatus('error');
    } finally {
      running.current = false;
      // Settled, not necessarily succeeded. A phone with no signal should delay
      // the app by one failed round trip, not hold it at a spinner.
      setSettledFor(id);
    }
  }, []);

  // Sign-in starts a pass; sign-out drops the ids, which belong to the account
  // that owned them. Local birth details and progress stay: signing out is not
  // a request to erase the phone, and the app is meant to work without an
  // account at all.
  useEffect(() => {
    if (!enabled || !userId) {
      setStatus('off');
      setError(null);
      setLastSyncedAt(null);
      lastAttempt.current = null;
      if (!userId) {
        // Including the settled marker: signing back into the same account must
        // wait for a fresh pass, not inherit the last session's verdict.
        setSettledFor(null);
        clearSyncIds();
        setChartId(null);
        setConversationId(null);
        conversationLanguage.current = null;
      }
      return;
    }

    run(userId);
  }, [enabled, userId, run]);

  // Coming back to the app is the natural moment to catch up: it is when a
  // failed push gets its second chance, and when edits made on another phone
  // while this one was closed arrive.
  useEffect(() => {
    if (!enabled || !userId) return;

    const subscription = AppState.addEventListener('change', (state) => {
      if (state !== 'active') return;
      const last = lastAttempt.current;
      if (!last || !last.ok || Date.now() - last.at > REFRESH_AFTER_MS) run(userId);
    });

    return () => subscription.remove();
  }, [enabled, userId, run]);

  const value = useMemo<SyncState>(
    () => ({
      enabled,
      ready,
      status,
      lastSyncedAt,
      error,
      chartId,

      async syncNow() {
        if (userId) await run(userId);
      },

      async pushBirth(details) {
        if (!userId) return;
        try {
          const id = await pushPrimaryChart(userId, details);
          const ids = await rememberChartId(id);
          setChartId(ids.chartId);
          const at = Date.now();
          lastAttempt.current = { at, ok: true };
          setLastSyncedAt(at);
          setError(null);
          setStatus('ok');
        } catch (err) {
          // Left for the next pass to notice. The local save already happened,
          // so nothing is lost by failing quietly here.
          lastAttempt.current = { at: Date.now(), ok: false };
          setError(message(err));
          setStatus('error');
        }
      },

      async pushChapterRead(slug) {
        if (!userId) return;
        try {
          await pushProgress(userId, [slug]);
        } catch (err) {
          lastAttempt.current = { at: Date.now(), ok: false };
          setError(message(err));
          setStatus('error');
        }
      },

      async pushProgressReset() {
        if (!userId) return;
        try {
          await clearRemoteProgress(userId);
        } catch (err) {
          // A union merge cannot express a deletion, so a failed reset would be
          // undone by the next sync. Saying so is better than a tick that
          // quietly comes back.
          lastAttempt.current = { at: Date.now(), ok: false };
          setError(message(err));
          setStatus('error');
        }
      },

      async loadChatHistory() {
        if (!userId || !chartId) return [];
        try {
          const known = conversationId ?? (await findConversation(userId, chartId))?.id ?? null;
          if (!known) return [];
          if (known !== conversationId) {
            await rememberConversationId(known);
            setConversationId(known);
          }
          return await fetchTurns(known);
        } catch {
          // An unreachable account should not stop someone reading their chart
          // and asking a fresh question; it costs them the older turns, which
          // are still upstream and appear on the next successful load.
          return [];
        }
      },

      async recordTurn(turn, language) {
        if (!userId || !chartId) return;

        const write = writes.current.then(async () => {
          if (!opening.current) {
            opening.current = (async () => {
              if (conversationId) return conversationId;
              const found = await findConversation(userId, chartId);
              const conversation = found ?? (await createConversation(userId, chartId, language));
              if (!conversation) return null;
              // Only from a row we actually read or wrote. Guessing it here
              // would skip the update below and leave the column lying.
              conversationLanguage.current = conversation.language;
              await rememberConversationId(conversation.id);
              setConversationId(conversation.id);
              return conversation.id;
            })();
          }

          const id = await opening.current;
          opening.current = null;
          if (!id) return;

          if (conversationLanguage.current !== language) {
            await setConversationLanguage(id, language);
            conversationLanguage.current = language;
          }

          await appendTurn(userId, id, turn);
        });

        // The queue must survive a failed write, or one dropped message would
        // reject every insert after it.
        writes.current = write.catch(() => undefined);

        try {
          await write;
        } catch (err) {
          opening.current = null;
          lastAttempt.current = { at: Date.now(), ok: false };
          setError(message(err));
          setStatus('error');
        }
      },

      async clearChatHistory() {
        if (!conversationId) return;
        try {
          await deleteConversation(conversationId);
          await rememberConversationId(null);
          setConversationId(null);
          conversationLanguage.current = null;
        } catch (err) {
          lastAttempt.current = { at: Date.now(), ok: false };
          setError(message(err));
          setStatus('error');
        }
      },
    }),
    [enabled, ready, status, lastSyncedAt, error, chartId, conversationId, userId, run],
  );

  return <SyncContext.Provider value={value}>{children}</SyncContext.Provider>;
}

export function useSync(): SyncState {
  const value = useContext(SyncContext);
  if (!value) throw new Error('useSync must be used inside SyncProvider');
  return value;
}
