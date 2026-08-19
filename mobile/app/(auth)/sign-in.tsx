/**
 * Sign in.
 *
 * Reachable, never forced. An account will carry saved charts and history once
 * there are tables behind it; until then the app works exactly as well without
 * one, and pretending otherwise would be a lie told by a paywall's grammar.
 */

import { useRouter } from 'expo-router';
import { useCallback } from 'react';

import { markAccountsSeen } from '../../src/api/storage';
import { AuthForm } from '../../src/components/AuthForm';
import { useAuth } from '../../src/auth/context';

export default function SignIn() {
  const router = useRouter();
  const { signIn, available } = useAuth();

  const submit = useCallback(
    async (email: string, password: string) => {
      const error = await signIn(email, password);
      if (!error) {
        await markAccountsSeen();
        router.replace('/');
      }
      return error;
    },
    [signIn, router],
  );

  return (
    <AuthForm
      title={'Welcome back.'}
      action="Sign in"
      tone="signIn"
      onSubmit={submit}
      footer={{
        text: 'No account yet?',
        link: 'Create one',
        onPress: () => router.replace('/sign-up'),
      }}
      onSkip={async () => {
        await markAccountsSeen();
        router.replace('/');
      }}
      notice={
        available
          ? null
          : 'Accounts are not configured in this build yet. You can keep using the app without one — everything stays on this device.'
      }
    />
  );
}
