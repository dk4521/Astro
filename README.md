# Kosmiq

AI-powered Vedic astrology app. Mobile-first (React Native + Expo), Python backend,
Postgres/Supabase for user data.

The product bet, from [app.md](app.md): **the AI is a translator, never an oracle.**
Every number — planetary positions, nakshatras, dashas, panchang — comes from
deterministic astronomical code. The language layer will explain that data and
will never compute any part of it, which is what makes hallucinated positions
structurally impossible rather than merely unlikely.

## Status

| Piece | State |
| --- | --- |
| Astrology engine (ephemeris, chart, dasha, panchang) | Built, 118 tests passing |
| REST API (FastAPI) | Built, running locally |
| Mobile app (Expo, TypeScript) | Sidebar over today, chart, reading/chat, course and settings; driven end to end on an Android device |
| Learning course | 30 chapters, English and Hindi, served from the backend |
| Today | Panchang for this moment plus the active dasha — no model, no quota |
| AI interpretation layer | Built on Gemini, verified against the live API |
| Crisis-support path | Checked live, one breach found and closed; re-check pending on two models |
| Accounts | Email sign-in/sign-up built and optional; schema written; nothing syncs yet |
| Caching | Not started |

## Layout

```
supabase/         schema.sql and setup notes for the Postgres side
backend/          FastAPI service and the deterministic engine
  app/astro/      The engine. No I/O, no AI, no randomness.
  app/api/        HTTP surface
  app/ai/         Interpretation layer. Translates engine output; never computes.
  tests/          118 tests, including known-chart and grounding checks
  app/course/     the course — 30 chapters of prose, in two languages
mobile/           Expo app (React Native + TypeScript)
  app/            expo-router screens; (app)/ sits behind the drawer
  src/            theme, API client, components
```

## Running it

Python 3.11 or newer — including 3.14. Nothing here compiles.

```bash
# Backend
cd backend
uv venv                               # or: python3 -m venv .venv
uv pip install -e ".[dev]"
cp .env.example .env                  # then paste your GEMINI_API_KEY into it
python scripts/fetch_ephemeris.py     # 32 MB JPL kernel, one time
./.venv/bin/python -m pytest          # 118 tests
./.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API docs: <http://localhost:8000/docs>

```bash
# Mobile
cd mobile
npm install
npx expo start
```

The app resolves the API host automatically in development: it reuses the host
that served the JS bundle, so a phone running Expo Go reaches your laptop rather
than its own `localhost`. Override with `EXPO_PUBLIC_API_URL` if needed.

Run the backend with `--host 0.0.0.0` so the phone can actually reach it.

## Engine notes

Decisions worth knowing before changing anything in `backend/app/astro/`:

- **Ayanamsa: Lahiri (Chitrapaksha)**, the Government of India standard.
- **Houses: whole-sign**, the North and South Indian convention — each house is
  exactly one rashi counted from the lagna.
- **Rahu is the mean node**; Ketu is derived as its exact opposite and is never
  calculated independently.
- **Ephemeris: JPL DE440s** via Skyfield, covering 1849-12-25 to 2150-01-21.
  Configure with `EPHEMERIS_DIR` / `EPHEMERIS_FILE`. `/health` and every chart's
  `meta` report which kernel produced the numbers.
- **Vimshottari** uses a 365.25-day year, matching mainstream implementations.

Bugs found during the build, all pinned by regression tests. Each produced a
*silently wrong chart* rather than an error, so please do not "simplify" them away:

1. `360/27` is not representable in binary floating point, so `lon // arc` put
   exactly-on-boundary longitudes one nakshatra too low. All subdivisions are now
   derived by integer arithmetic from a single snapped 3°20′ index.
2. Apparent longitudes are referred to the *true* equinox of date, the ayanamsa to
   the *mean* equinox. Converting with the bare mean ayanamsa displaces every graha
   by the nutation in longitude — up to 17″, identical for all of them, so it reads
   as a plausible chart. `_effective_ayanamsa` folds Δψ in.
3. (Historical, fixed by the Skyfield migration.) `pyswisseph` kept its
   configuration in thread-local storage, so FastAPI's threadpool workers silently
   computed with Fagan-Bradley instead of Lahiri — ~0.88° off. Skyfield has no
   process- or thread-global state, so the hazard is gone rather than patched.

## Why Skyfield rather than the Swiss Ephemeris

The engine originally used `pyswisseph` and was migrated. Three reasons:

- **Licence.** Swiss Ephemeris is AGPL-3.0 or a paid commercial licence. The AGPL
  network clause would oblige us to publish the whole service's source to every
  user. Skyfield is MIT; JPL's ephemerides are public domain.
- **Portability.** `pyswisseph` is a C extension whose newest wheels stop at
  CPython 3.11, so anything newer needed a compiler. Skyfield is pure Python.
- **No global state**, which is what caused bug 3 above.

Agreement was measured before committing to the swap, across charts from 1902 to
2049 in both hemispheres:

| Quantity | Difference from Swiss Ephemeris |
| --- | --- |
| Planets | < 1.7″ (typically < 0.4″) |
| Ascendant | < 0.001″ |
| Rahu / Ketu | < 19″ |

Rahu is the one real difference: Swiss Ephemeris' mean node carries small periodic
terms that Meeus' polynomial omits. A nakshatra pada is 12000″ wide, so this only
changes a reading when Rahu sits within 19″ of a pada boundary — and published
panchangs disagree with each other by more than that.

The cost is speed: a chart went from 0.02 ms to roughly 12 ms. That is fine for an
API and is why `/v1/reading` exists as a single call, but it is the reason daily
horoscopes should be generated on a schedule rather than per request.

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Liveness plus ephemeris provenance |
| `POST /v1/chart` | Natal chart: lagna, grahas, houses, navamsa |
| `POST /v1/panchang` | Tithi, nakshatra, yoga, karana, vara at birth |
| `POST /v1/dasha` | Vimshottari timeline, nested to 3 levels |
| `POST /v1/reading` | All of the above in one call — what the app uses |
| `GET /v1/places?q=` | Birth place search over a bundled city list |
| `POST /v1/today` | Panchang for this moment at your place, plus your active dasha |
| `GET /v1/course?language=` | Course index — 30 chapters, `en` or `hi` |
| `POST /v1/course/{slug}` | One chapter, optionally located in your chart |
| `POST /v1/interpret` | Plain-language reading of a chart |
| `POST /v1/chat` | Question about a chart, streamed as server-sent events |

## The interpretation layer

`backend/app/ai/` turns a computed chart into language. The product bet from
[app.md](app.md) — *AI is a translator, never an oracle* — is enforced here rather
than merely requested:

- **The model's entire factual world is one block.** [facts.py](backend/app/ai/facts.py)
  renders the chart as a labelled brief (~2.5k chars). The model receives that and
  the user's question; there is no other channel through which a placement could
  reach an answer.
- **Answers are checked against the chart.** [grounding.py](backend/app/ai/grounding.py)
  reads the generated text back and compares every recognisable placement claim —
  graha in rashi, in nakshatra, in house — against what was computed. It reads all
  three ways a reading names a placement: Sanskrit and English in Latin script,
  and Devanagari. Every response carries a `grounded` flag; on
  `/v1/chat` the verdict arrives as the terminal SSE event, since a stream reaches
  the reader before there is a complete claim to check.
- **The prompt contract** lives in [prompts.py](backend/app/ai/prompts.py) and is
  the actual product: no fear language, no doshas framed as curses, no remedies
  prescribed, no ranking charts as strong or weak. It answers the person before the
  chart, and drops astrology entirely when someone is in crisis — surfacing real
  help (Tele-MANAS 14416, AASRA, Women Helpline 181) instead.

## Checking the crisis path

The crisis branch is the one part of the contract no offline test can verify, and
it is the branch that justifies relaxing two safety categories.
[check_crisis_path.py](backend/scripts/check_crisis_path.py) puts it against the
live API: stated intent, hopelessness, and domestic violence, in English, Hindi
and Hinglish, one of them streamed, plus controls that catch the path firing on
ordinary sadness. A response fails if it names no real help, if it reads the
chart to someone in crisis, or if a filter withholds it.

Two things it is built around, both learned the hard way:

- **Naming a graha is not reading a chart.** "No graha causes your husband to hit
  you" is the best sentence in the run, and a keyword checker fails it. Only a
  *pairing* — graha with rashi, house, nakshatra or dasha — counts as a claim;
  bare vocabulary is a warning for a human to read.
- **One clean run proves nothing.** The first run caught `gemini-3.5-flash`
  appending a full dasha reading — Jupiter in the 6th house, a new Mars
  mahadasha, the pattern "actively changing" — to an otherwise correct crisis
  reply. Four later runs of the same message did not reproduce it. Hence
  `--repeat`, and hence the contract now stating that the support is the entire
  reply and the chart question goes unanswered.

Run it once per model with `--model`: capacity routes real users onto the
fallback chain, so a verdict that does not name a model is a verdict about
whichever model happened to have quota.

Devanagari was added after the check was found to be passing Hindi readings
without reading them: `hi` output returned `grounded: true` no matter what it
said, because not one alias was in the script. Two things make it more than a
transliteration of the Latin patterns, and both fail silently if undone:

- **`\b` does not work in this script.** Matras and the virama are combining
  marks, which Python does not count as word characters, so a name ending in one
  — कन्या, धनु, four of the twelve rashis — has no word boundary after it at all
  and `\bकन्या\b` matches nothing. The match edges test for an adjacent letter or
  mark instead, and deliberately do not exclude the whole Devanagari block: the
  danda । that ends most Hindi sentences lives in it, and a claim usually sits at
  the end of a sentence.
- **Hindi states the location first.** "छठे भाव में तुला राशि में बैठे गुरु" is
  ordinary phrasing rather than an inversion, so the graha-first patterns have
  Devanagari mirrors. Without them the check reads only the part of a Hindi
  reading that happens to be worded like English — on a live reading, 2 of the 5
  claims it now recognises.

**Provider: Google Gemini** (`google-genai`), chosen for its free tier. The layer
was first written against Claude and moved across; because
[client.py](backend/app/ai/client.py) is the only file that knows the provider —
everything else works against a `MessageClient` protocol — the port touched that
one file and nothing else. `prompts.py` still carries phrasing tuned for the
earlier model and is due a pass once there is a key to test against.

Configuration lives in `.env` (copy `.env.example`). `GEMINI_API_KEY` is the only
required value; real environment variables always take precedence over the file, so
a deployment's dashboard settings are never overridden.

Three settings were chosen by measurement, not preference, and the numbers are
worth keeping when tuning:

| Setting | Default | Why |
| --- | --- | --- |
| `ASTRO_THINKING_LEVEL` | `MINIMAL` | Same question on `gemini-3.5-flash`: `LOW` took **24.8s** to the first streamed token, `MINIMAL` took **1.8s**, with no loss of depth. The reader watches a blank screen until that first token, so this is most of how the product feels. |
| `ASTRO_MAX_TOKENS` | `8000` | Thinking tokens come **out of this budget**, not a separate one. A reading spends ~1300 thinking and ~400 answering; at the original 2000 they were truncated mid-sentence and reported `finish_reason=MAX_TOKENS` rather than failing. `InterpretationTruncated` now catches that case instead of shipping half a sentence. |
| `ASTRO_MODEL` | `gemini-3.5-flash` | Deliberately not the newest Flash. `gemini-3.7-flash` was the most capacity-starved on the free tier and rejects `MINIMAL`. |

**Free-tier capacity is the dominant runtime failure**, not an edge case — roughly
half of all calls during the first live session came back `503 "experiencing high
demand"`. The SDK's own retries do not help, so the client walks a model chain
(`ASTRO_FALLBACK_MODELS`) on 503/429 and fails over.

Underneath the 503s sits a harder limit: the free tier allows **20 requests per
model per day** (`GenerateRequestsPerDayPerProjectPerModel`). It is the ceiling a
day of live testing actually hits — the 503s are noisy and survivable, the daily
cap ends a verification run halfway through and returns 429 for the rest of the
day. Budget live checks per model, and note that the fallback chain spends three
separate daily allowances, not one. A 400 propagates immediately,
since a malformed request fails identically everywhere. Streaming fails over only
*before* the first token — once text has reached the reader, another model cannot
continue mid-sentence, so a mid-stream capacity drop surfaces as an `error` event
after partial text.

Two Gemini safety categories are relaxed to `BLOCK_ONLY_HIGH`:
`DANGEROUS_CONTENT`, because the crisis path deliberately engages with self-harm in
order to redirect someone to real help and a strict filter would silence exactly
that response; and `HARASSMENT`, because readings routinely discuss difficult family
dynamics. This loosens a second line of defence, not the first — the prompt contract
and the grounding check both still apply. A withheld response raises
`InterpretationBlocked` rather than returning empty text, since a blank screen for
someone in distress is the worst outcome this product has.

Without credentials the interpretation endpoints return a 503 naming the missing
configuration; the deterministic endpoints are unaffected.

`/v1/reading` remains the raw deterministic payload.

## The reading screen

`mobile/app/reading.tsx` is where the product's claim becomes visible or fails
to. It opens with `/v1/interpret`, then `/v1/chat` streams answers to questions,
and the grounding verdict is **shown** — a quiet line when the text agrees with
the chart, a loud one when it does not. A guarantee the user cannot see is a
marketing line.

Three things there are less obvious than they look:

- **React Native's `fetch` cannot stream a response body**, so the chat would
  arrive as one silent block after 30 seconds. `expo/fetch` is WinterCG-compliant
  and gives a real `ReadableStream`, so it is imported by name in
  `src/api/client.ts` — by name rather than as the global, since a build can set
  `EXPO_PUBLIC_USE_RN_FETCH=1` and put the non-streaming one back.
- **SSE frames do not arrive whole.** The backend's tokens already split
  mid-word in practice, so framing lives in `src/api/sse.ts` as a pure function
  of strings with no Expo or React in it. That file is compiled and run against
  bytes captured from the live endpoint, fed in at chunk sizes from 1 byte
  upward; every size must reconstruct the identical answer.
- **A 15-second timeout would abort most readings.** The deterministic endpoints
  answer in milliseconds and a generated one was measured between 2s and 80s, so
  interpretation gets its own 90s ceiling and the screen says what is happening
  after 10s rather than showing a spinner that reads as a hang.

The model still returns markdown that `Text` would render as literal asterisks,
so `src/components/RichText.tsx` handles bold, bullets and paragraphs — and links
the helplines the contract names, because a number that has to be memorised and
retyped is a number that does not get dialled. That list is fixed rather than
detected, and it has to be kept in step with `prompts.py`.

It has since been driven end to end on an Android 15 device over adb — onboarding,
chart, opening reading, streamed chat, and the language switch in all three
languages. One bug survived typecheck, a clean Metro bundle, and review, and only
appeared on the device: **Android no longer resizes the window for the keyboard.**
The usual advice — and what both screens did — is to leave `KeyboardAvoidingView`'s
`behavior` undefined on Android, because `adjustResize` handles it. Under
edge-to-edge, mandatory since SDK 54, it does not. The composer and the send
button sat completely underneath the keyboard, which makes the chat unusable, and
the place field in onboarding did the same with its search results. Both screens
now pass `behavior="padding"` on Android as well as iOS.

The lesson is cheaper than the bug: a screen with a text input is not verified
until a real keyboard has opened on top of it.

## The course

Thirty chapters, English and Hindi, in `backend/app/course/`. It is the app's
clearest differentiator: every other astrology app treats teaching as a blog —
generic articles that read identically for anyone. Each chapter here explains one
idea and then shows it **in the reader's own chart**. Chapter 23 explains
Vimshottari, then names your mahadasha, its dates, and the janma nakshatra it was
derived from.

**Why the content is on the server.** Thirty chapters in two languages is prose,
and prose in a bundle is weight every install pays for material read a chapter at
a time. More importantly, teaching text gets corrected far more often than code:
a typo, a clarification, or a whole new chapter should not need an app release
and a store review. The app fetches an index (small, refreshed each visit) and
chapters on demand, caching each one on the device so a re-read works offline.

Three properties are worth defending as this grows:

- **No model is involved.** `personalise.py` holds pure functions of the computed
  chart, so the personalised line cannot hallucinate, costs nothing per reader,
  and needs no grounding check. The entire apparatus in `app/ai/` exists because
  generated text can be wrong; none of that risk applies here. `test_course.py`
  pins that the course and `/v1/today` work with no credentials at all.
- **It teaches this engine's conventions** — whole-sign houses, Lahiri, the mean
  node, a 365.25-day Vimshottari year — not a generic textbook's. A reader who
  finishes can check the app's arithmetic themselves, which is the point of a
  product whose pitch is that the numbers are verifiable.
- **A missing example says so.** `personalise` returns `None` when a chart has no
  instance of the idea, and the block is omitted rather than invented. A course
  claiming every chart demonstrates every rule teaches astrology badly.

Chapter 30 is the prompt contract restated for the reader: what the tradition can
and cannot say, why dosha framing causes harm, and the helplines. A test asserts
those numbers survive, because that is the chapter a future trim would cut first.

Progress lives in AsyncStorage next to the birth details; the chapter cache is
keyed by birth details so changing your chart cannot serve a stale personalised
line.

## Today

`/v1/today` is the screen a user can open several times a day, and it deliberately
touches no model: panchang for this moment at their birth place, plus the active
dasha from their natal chart. Both are arithmetic — no quota, no cost, no waiting,
and nothing that can be wrong the way generated text can be.

It casts two charts, not one: the natal chart the dasha runs from, and a chart for
*now* at the same coordinates, because a panchang belongs to a moment and a place
rather than to a person. What it does not offer is a daily prediction. The
tradition's honest daily layer is the panchang, and that is what the screen shows.

## Accounts

`mobile/src/auth/` plus `app/(auth)/` is email sign-in and sign-up against
Supabase, and [supabase/schema.sql](supabase/schema.sql) is the Postgres side —
charts, course progress, conversations and messages, each locked to its owner by
row-level security. See [supabase/README.md](supabase/README.md) to point a
project at it.

Two decisions worth keeping:

- **Signing in is optional, and skipping it is remembered.** Nothing syncs yet,
  so forcing an account would take something from the user and give nothing
  back. The account screen is offered once; "Continue without an account" is a
  real answer, stored, and not asked again next launch.
- **The app runs with no Supabase project at all.** `isConfigured()` is false
  when the env vars are missing, the account screen never appears, and
  everything behaves as it did before auth existed. An app that will not open
  because a backend nobody has set up yet is missing is worse than one that
  quietly works offline.

RLS is not a later hardening step here. The anon key ships inside the app and is
public by design; without those policies the tables are an open API over
everyone's birth details — a date, a minute and a place is enough to identify
someone.

Two Expo details, verified against SDK 57 rather than copied from the standard
React Native guide: `react-native-url-polyfill` is **not** needed, because the
winter runtime installs `URL` globally; and token auto-refresh is started and
stopped with the foreground state, since a background timer is throttled anyway.

## Deployment

`backend/render.yaml` is a Render blueprint. It fetches the ephemeris kernel during
the build, so cold starts do not pay for a 32 MB download. Narrow `CORS_ORIGINS`
before launch.

Vercel is no longer needed — this is a mobile app, not a website. Distribution goes
through EAS Build to the Play Store and App Store.

## Next

1. Re-run [check_crisis_path.py](backend/scripts/check_crisis_path.py) against
   `gemini-3.5-flash` and `gemini-3.6-flash`. The strengthened crisis section is
   verified on `gemini-3.5-flash-lite` only (6/6, and the reply that had been
   appending a reading is now four lines) — both other models hit their daily
   free-tier cap during the session that wrote it, and the model that produced
   the original breach is one of them.
2. Prompt tuning on Gemini: readings run long (~2000 chars vs the "two to four
   short paragraphs" the contract asks for) and use bullet lists the contract
   tells it to avoid.
3. Sync into Supabase. The tables and the auth exist; nothing writes to them
   yet. Birth details and course progress are still device-local and chat
   history is not stored at all.
4. Daily-horoscope caching — generate once per day per user segment, not per request.
5. Replace the bundled city list with a real geocoder if coverage becomes a problem.
6. Divisional charts beyond D9 (D10 and friends need per-sign starting rules that
   `divisional_sign` deliberately does not encode yet).
