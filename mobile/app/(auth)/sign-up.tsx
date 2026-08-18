/**
 * Create an account.
 *
 * If the Supabase project has email confirmation on — it is on by default — a
 * successful sign-up returns a user and no session. The screen says so instead
 * of appearing to do nothing, which is the single most confusing state in this
 * flow.
 */

import { useRouter } from 'expo-router';
import { useCallback, useState } from 'react';

import { markAccountsSeen } from '../../src/api/storage';
import { AuthForm } from '../../src/components/AuthForm';
import { useAuth } from '../../src/auth/context';

export default function SignUp() {
  const router = useRouter();
  const { signUp, available } = useAuth();
  const [notice, setNotice] = useState<string | null>(null);

  const submit = useCallback(
    async (email: string, password: string) => {
      const { error, needsConfirmation } = await signUp(email, password);
      if (error) return error;

      if (needsConfirmation) {
        setNotice(
          `Check ${email.trim()} for a confirmation link, then come back and sign in.`,
        );
        return null;
      }

      await markAccountsSeen();
      router.replace('/');
      return null;
    },
    [signUp, router],
  );

  return (
    <AuthForm
      title={'Make an account.'}
      subtitle="Your birth details stay yours. An account only means they follow you to a new phone."
      action="Create account"
      onSubmit={submit}
      footer={{
        text: 'Already have one?',
        link: 'Sign in',
        onPress: () => router.replace('/sign-in'),
      }}
      onSkip={async () => {
        await markAccountsSeen();
        router.replace('/');
      }}
      notice={
        notice ??
        (available
          ? null
          : 'Accounts are not configured in this build yet. You can keep using the app without one — everything stays on this device.')
      }
    />
  );
}
