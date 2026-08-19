/**
 * Chat history, stored in the account.
 *
 * This is the one thing the app holds that cannot be recomputed. A chart falls
 * out of five numbers and the panchang falls out of a timestamp, but a
 * conversation happened once — so unlike everything else here, losing it loses
 * something.
 *
 * Two decisions worth stating, because both are easy to get wrong later:
 *
 * - **The opening reading is not stored.** It is generated fresh from the chart
 *   each time the screen opens, in whichever language is selected, so a stored
 *   copy would be a stale duplicate. It is also why `history` sent to `/v1/chat`
 *   must stay the conversation alone — the backend folds the chart brief into
 *   the first turn whatever its role, and an assistant turn in position zero
 *   comes back replayed as if the user had written it.
 * - **The grounding verdict is stored with the message it describes.** A reading
 *   that disagreed with the chart has to still say so when it is read back
 *   months later; a warning that survives only until you leave the screen is a
 *   warning the product does not really mean.
 */

import { supabase } from '../auth/client';
import type { Language } from '../api/types';

/** How many turns to read back. Older ones stay in the account, unread. */
const HISTORY_LIMIT = 100;

export type StoredTurn = {
  role: 'user' | 'assistant';
  content: string;
  grounded?: boolean;
  contradictions?: string[];
};

type MessageRow = {
  role: 'user' | 'assistant';
  content: string;
  grounded: boolean | null;
  contradictions: string[] | null;
};

export type Conversation = { id: string; language: Language };

/** One row in the history list. */
export type ConversationSummary = {
  id: string;
  persona: string | null;
  language: Language;
  createdAt: string;
  turns: number;
};

/**
 * The conversation about this chart, if there is one.
 *
 * Finding and creating are separate calls because opening the reading screen
 * must not write anything: a lookup that creates on miss would leave an empty
 * conversation behind every time someone glanced at a reading without asking a
 * question.
 *
 * One conversation per chart rather than one per session — the screen has no
 * thread list and no way to choose between threads, so a second one would be a
 * thread the user could never get back to.
 */
export async function findConversation(
  userId: string,
  chartId: string,
  persona: string | null,
): Promise<Conversation | null> {
  if (!supabase) return null;

  // Scoped to the companion as well as the chart. Without this, picking a new
  // companion would resume the previous one's thread — which is the opposite of
  // what switching is for, and would file its turns under the wrong name in the
  // history list.
  let query = supabase
    .from('conversations')
    .select('id, language')
    .eq('user_id', userId)
    .eq('chart_id', chartId);
  query = persona ? query.eq('persona', persona) : query.is('persona', null);

  const { data, error } = await query
    .order('created_at', { ascending: false })
    .limit(1)
    .maybeSingle<Conversation>();

  if (error) throw new Error(error.message);
  return data ?? null;
}

export async function createConversation(
  userId: string,
  chartId: string,
  language: Language,
  persona: string | null,
): Promise<Conversation | null> {
  if (!supabase) return null;

  const { data, error } = await supabase
    .from('conversations')
    .insert({ user_id: userId, chart_id: chartId, language, persona })
    .select('id, language')
    .single<Conversation>();

  if (error) throw new Error(error.message);
  return data;
}

/**
 * Every conversation in the account, newest first, with how many turns each
 * holds.
 *
 * The count comes from a second query rather than a join: PostgREST can return
 * an aggregate, but only by making `messages` the selected table, which would
 * mean paging through every message in the account to count them.
 */
export async function listConversations(userId: string): Promise<ConversationSummary[]> {
  if (!supabase) return [];

  const { data, error } = await supabase
    .from('conversations')
    .select('id, persona, language, created_at')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
    .limit(100);

  if (error) throw new Error(error.message);
  const rows = data ?? [];
  if (rows.length === 0) return [];

  const counts = await Promise.all(
    rows.map(async (row) => {
      const { count } = await supabase!
        .from('messages')
        .select('id', { count: 'exact', head: true })
        .eq('conversation_id', row.id);
      return count ?? 0;
    }),
  );

  return rows
    .map((row, i) => ({
      id: row.id as string,
      persona: (row.persona as string | null) ?? null,
      language: row.language as Language,
      createdAt: row.created_at as string,
      turns: counts[i],
    }))
    // An empty conversation is a row that was opened and never used. It is not
    // history and listing it would only ever confuse.
    .filter((row) => row.turns > 0);
}

/** The stored turns, oldest first — the order the screen renders them in. */
export async function fetchTurns(conversationId: string): Promise<StoredTurn[]> {
  if (!supabase) return [];

  // Newest first with a limit, then reversed: ordering ascending and limiting
  // would return the *start* of a long conversation rather than where it left off.
  const { data, error } = await supabase
    .from('messages')
    .select('role, content, grounded, contradictions')
    .eq('conversation_id', conversationId)
    .order('created_at', { ascending: false })
    .limit(HISTORY_LIMIT);

  if (error) throw new Error(error.message);

  return (data ?? [])
    .reverse()
    .map((row: MessageRow) => ({
      role: row.role,
      content: row.content,
      grounded: row.grounded ?? undefined,
      contradictions: row.contradictions ?? undefined,
    }));
}

export async function appendTurn(
  userId: string,
  conversationId: string,
  turn: StoredTurn,
): Promise<void> {
  if (!supabase) return;

  const { error } = await supabase.from('messages').insert({
    conversation_id: conversationId,
    user_id: userId,
    role: turn.role,
    content: turn.content,
    grounded: turn.grounded ?? null,
    contradictions: turn.contradictions ?? null,
  });

  if (error) throw new Error(error.message);
}

/**
 * Record the language the conversation is being held in.
 *
 * The pills on the reading screen switch language mid-thread, so the value set
 * at creation stops being true the moment someone uses them.
 */
export async function setConversationLanguage(
  conversationId: string,
  language: Language,
): Promise<void> {
  if (!supabase) return;

  const { error } = await supabase
    .from('conversations')
    .update({ language })
    .eq('id', conversationId);

  if (error) throw new Error(error.message);
}

/** Delete a conversation and, by cascade, every message in it. */
export async function deleteConversation(conversationId: string): Promise<void> {
  if (!supabase) return;

  const { error } = await supabase.from('conversations').delete().eq('id', conversationId);
  if (error) throw new Error(error.message);
}

/**
 * Every conversation in the account.
 *
 * The settings screen promises "every question and answer stored in your
 * account is removed". Once history accumulates across companions, deleting
 * only the open thread would leave that promise false. `messages` cascades on
 * the conversation row, so this is one delete.
 */
export async function deleteAllConversations(userId: string): Promise<void> {
  if (!supabase) return;
  const { error } = await supabase.from('conversations').delete().eq('user_id', userId);
  if (error) throw new Error(error.message);
}
