/**
 * Who is signed in, for the whole app.
 *
 * The provider mounts above every route so a screen never has to ask twice, and
 * it resolves to a definite answer — signed in, or not — before anything routes
 * on it. `ready` exists for that: routing on a session that has not loaded yet
 * bounces a returning user through the sign-in screen for a frame, which reads
 * as the app having forgotten them.
 *
 * When Supabase is not configured the provider still works. It simply reports
 * nobody signed in and `available: false`, and the app behaves as it did before
 * accounts existed.
 */

import type { Session, User } from '@supabase/supabase-js';
import { ReactNode, createContext, useContext, useEffect, useMemo, useState } from 'react';

import { authErrorMessage, isConfigured, supabase } from './client';

type AuthState = {
  /** False when this build has no Supabase project configured. */
  available: boolean;
  /** True once the stored session has been read, whatever the answer. */
  ready: boolean;
  session: Session | null;
  user: User | null;
  signIn: (email: string, password: string) => Promise<string | null>;
  signUp: (email: string, password: string) => Promise<{ error: string | null; needsConfirmation: boolean }>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(!isConfigured());

  useEffect(() => {
    if (!supabase) return;

    let cancelled = false;

    supabase.auth.getSession().then(({ data }) => {
      if (cancelled) return;
      setSession(data.session);
      setReady(true);
    });

    // Covers sign-in, sign-out, token refresh and a session expiring while the
    // app was closed — all of which should move the UI without a reload.
    const { data: subscription } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next);
      setReady(true);
    });

    return () => {
      cancelled = true;
      subscription.subscription.unsubscribe();
    };
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      available: isConfigured(),
      ready,
      session,
      user: session?.user ?? null,

      async signIn(email, password) {
        if (!supabase) return 'Accounts are not configured in this build.';
        const { error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        return error ? authErrorMessage(error) : null;
      },

      async signUp(email, password) {
        if (!supabase) {
          return { error: 'Accounts are not configured in this build.', needsConfirmation: false };
        }
        const { data, error } = await supabase.auth.signUp({
          email: email.trim(),
          password,
        });
        if (error) return { error: authErrorMessage(error), needsConfirmation: false };

        // With email confirmation on, Supabase returns a user but no session.
        // Saying so is better than a screen that looks like nothing happened.
        return { error: null, needsConfirmation: data.session === null };
      },

      async signOut() {
        await supabase?.auth.signOut();
      },
    }),
    [ready, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside AuthProvider');
  return value;
}
