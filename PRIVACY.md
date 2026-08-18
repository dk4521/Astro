# Privacy Policy — Kosmiq

**Last updated: 18 August 2026**

Kosmiq is a Vedic astrology app. This policy describes exactly what the app
collects, where it goes, and how to remove it. It describes what the app
actually does today, not what it might do later.

---

## The short version

| | |
| --- | --- |
| **Do we sell your data?** | No. Never, to anyone, for any purpose. |
| **Do we track you or show ads?** | No. There is no analytics, advertising or tracking code in the app at all. |
| **Do we ask for location, contacts, camera or storage?** | No. The app never shows a permission prompt — it asks for no location, contacts, camera, microphone or file access. Your birth place is one you type and pick from a list; it is not read from your phone's location. |
| **Do you need an account?** | No. The app works fully without one. |
| **What leaves your phone?** | Your birth date, time and coordinates, so our server can compute your chart. Plus your questions, when you ask one. |

---

## What we collect, and why

### Birth details — date, time and place

These three facts are the entire basis of the app. Every number it shows — the
planetary positions, the nakshatras, the dasha periods, the panchang — is
computed from them.

- **On your phone.** They are saved on your device so you do not have to type
  them again.
- **Sent to our server** each time a chart is calculated. The server computes
  the answer and returns it. **It does not store your birth details.**
- **In your account,** only if you create one. See *Accounts* below.

### Your questions and the readings you receive

If you ask a question on the reading screen, the question and the answer are:

- **Not stored anywhere** if you are not signed in. They exist only while the
  screen is open.
- **Stored in your account** if you are signed in, so your conversation is
  still there on your next phone.

### Course progress

Which chapters you have read. Kept on your phone, and in your account if you
have one.

### Account details — only if you create an account

An email address and a password. Creating an account is optional and the app
does not ask you to. We never see your password: it is handled and stored,
hashed, by our authentication provider.

---

## Who else your data reaches

Three services are involved. Each receives only what it needs.

### Google (Gemini API) — writes the readings

To turn your computed chart into readable language, we send Google's Gemini API:

- your **computed chart** — planetary positions, nakshatras, dasha periods
- your **birth date, local time and coordinates**, as part of that chart data
- the **question you asked**, if you asked one

It never receives your name, your email address, or anything identifying you as
a person. It receives astronomical data and a question.

Google processes this under its own API terms. We do not use your data to train
any model, and we have not enabled any feature that would.

### Supabase — stores your account

If you create an account, your email address, birth details, course progress and
conversations are stored in a Supabase database. Every table is protected by
row-level security: the rules are written so that a request can only ever read
or write rows belonging to the account that made it.

### Render — runs our server

Our API runs on Render. As with any web service, their infrastructure handles
the network requests. Our server does not write your birth details to any log or
database.

---

## One thing we do keep for a short time

To avoid asking the AI the same question twice — which is both slow and costly —
a generated reading is held **in the server's memory for up to about a day**, and
a copy is kept **on your phone for the day it was generated**. Both are dropped
after that.

The server's copy is filed under a one-way fingerprint of the request rather than
under anything that names you, and it disappears whenever the server restarts.

---

## What we never do

- Sell, rent or share your data with advertisers or data brokers
- Show advertising
- Include analytics, crash-tracking or any other telemetry
- Read your location, contacts, photos, files or any other app's data
- Use your birth details or your conversations to train an AI model

---

## Your choices

**Use the app without an account.** Everything except cross-device sync works,
and nothing is stored outside your phone except the calculation requests
described above.

**Change or remove your birth details.** Settings → *Change birth details*.

**Delete your conversation history.** Settings → *Delete chat history*. This
removes every stored question and answer from your account permanently.

**Reset your course progress.** Settings → *Reset progress*.

**Sign out.** Your data stays in your account and on your phone; nothing is
deleted.

**Delete your account and everything in it.** Write to us at the address below
and we will delete the account together with all of its charts, conversations and
progress. Deletion is permanent and we will confirm when it is done.

**Uninstalling the app** removes everything held on the phone. If you have an
account, that data remains until you ask us to delete it.

---

## Crisis support

If a conversation touches on self-harm or serious distress, the app stops
interpreting charts and shows Indian helpline numbers instead. That happens
entirely within the response you see. Nothing about it is recorded, flagged or
reported to anyone.

---

## Children

Kosmiq is not directed at children under 13, and we do not knowingly collect
data from them.

---

## Changes to this policy

If this policy changes, the date at the top changes with it. Material changes
will be announced in the app before they take effect.

---

## Contact

Questions about this policy, or a request to delete your account:

**<CONTACT_EMAIL>**

We aim to reply within seven days.
