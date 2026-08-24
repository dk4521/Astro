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
| Astrology engine (ephemeris, chart, dasha, panchang) | Built, 216 tests passing |
| REST API (FastAPI) | Built, running locally |
| Mobile app (Expo, TypeScript) | Sidebar over today, chart, reading/chat, course and settings; driven end to end on an Android device |
| Learning course | 30 chapters, English and Hindi, served from the backend |
| Today | Panchang for this moment plus the active dasha — no model, no quota |
| Tarot | 78-card deck in two languages, seeded shuffle, three-card spread; the written meanings are free, the reading costs a credit. 36 tests |
| AI interpretation layer | Built on Gemini, verified against the live API |
| Crisis-support path | Checked live, one breach found and closed; re-check pending on two models |
| Accounts | Email sign-in/sign-up, optional |
| Sync | Chart, course progress and chat history mirrored to Supabase; checked end to end against a live project |
| Caching | Two layers, device and server; measured 14.0s → 0.075s on a live repeat |
| Credits | Schema, server-side enforcement and Razorpay checkout built and unit-tested. **Not yet run against a live Supabase project or a Razorpay test account** |

## Layout

```
supabase/         schema.sql and setup notes for the Postgres side
backend/          FastAPI service and the deterministic engine
  app/astro/      The engine. No I/O, no AI, no randomness.
  app/api/        HTTP surface
  app/ai/         Interpretation layer. Translates engine output; never computes.
  app/billing/    plans (prices), gateway (Razorpay), store (Supabase service role)
  app/auth.py     verifies the Supabase token — who is spending the credit
  tests/          252 tests, including known-chart, grounding, cache, billing and tarot
  app/tarot/      the deck (written, not generated), the seeded shuffle, the card check
  app/course/     the course — 30 chapters of prose, in two languages
  app/places_data.py  ~3,000 places, India tier-1 to tier-3; built by scripts/
mobile/           Expo app (React Native + TypeScript)
  app/            expo-router screens; (app)/ sits behind the drawer
  src/            theme, API client, components
  src/sync/       the account mirror — see supabase/README.md
  src/api/billing.ts  opens Razorpay's hosted page; nothing native
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
./.venv/bin/python -m pytest          # 153 tests
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
| `GET /v1/tarot/deck` | All 78 cards, both languages. Static, cacheable, free |
| `POST /v1/tarot/draw` | Three cards and the seed they came from. Free, no model |
| `POST /v1/tarot/reading` | The spread read as one piece. Costs one credit |
| `POST /v1/interpret` | Plain-language reading of a chart |
| `POST /v1/chat` | Question about a chart, streamed as server-sent events. Costs one credit |
| `GET /v1/billing/plans` | What credits cost. Public, so the price list opens signed out |
| `POST /v1/billing/checkout` | Plan id in, Razorpay page out. Session required |
| `POST /v1/billing/cancel` | Stop a subscription at the end of the paid period |
| `POST /v1/billing/webhook` | Razorpay reporting a payment. HMAC-verified, idempotent |

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
separate daily allowances, not one. This limit is why caching exists here at all;
see **Caching** below. A 400 propagates immediately,
since a malformed request fails identically everywhere. Streaming fails over only
*before* the first token — once text has reached the reader, another model cannot
continue mid-sentence, so a mid-stream capacity drop surfaces as an `error` event
after partial text.

## Caching

Two layers, for two different failures.

**On the device** (`mobile/src/api/reading.ts`) the opening reading is kept for
the day, keyed by chart, language and UTC date. This is the layer that protects
a real user: it survives cold starts, redeploys and a backend that spun down
overnight, and without it one person opening the app four times would spend a
fifth of a model's daily allowance re-reading text they already have.

**On the server** (`backend/app/ai/cache.py`) answers are keyed by a SHA-256 of
the entire request — every message, the system instruction, the language
directive, the model chain and the sampling settings. That key is what makes the
cache honest: it cannot serve an answer produced from different facts or a
different prompt, because those hash differently, so editing `prompts.py` or
swapping the model invalidates everything without anyone remembering to. It is
in-process, so a free-tier cold start starts cold — that is the reason the device
layer exists rather than a reason to skip this one, which is the only place two
requests that are identical across users can be served for free.

The lifetime falls out of the key rather than being configured. The fact brief
carries `as of:` at day precision, so tomorrow's request for the same chart
hashes differently and misses on its own; `ASTRO_CACHE_TTL` is a memory bound,
not a correctness device. `ASTRO_CACHE_SIZE=0` disables the whole thing, which is
the switch to reach for when a reading looks wrong and you need to know whether
you are debugging the model or a stored answer.

**Nothing that failed grounding is ever stored**, in either layer. Caching bets
that the same request deserves the same reply, and that bet is off for a reply
already known to contradict the chart it describes — storing it would turn one
bad reading into the same bad reading all day. The retry costs a request the
reader was going to spend anyway. For the same reason a stream that was
interrupted or abandoned is not stored: half an answer must never be served as
a whole one.

Measured against the live API, same chart and language, back to back:

| | Wall time | `X-Cache` | Model requests spent |
| --- | --- | --- | --- |
| First call | 13.98 s | `miss` | 1 |
| Second call | 0.075 s | `hit` | 0 |

`/health` reports `hits`, `misses`, `entries` and `ratio`, which is worth
watching rather than assuming — on 20 requests a day, the hit ratio is the number
that says whether the service can survive its own users.

`/v1/places` and `/v1/course` carry ordinary `Cache-Control` headers too
(a day and an hour): both are pure lookups, and onboarding fires a place search
every 250 ms while someone types a city name.

## Safety categories

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


## Tarot

The one place in this product where something is genuinely random, and the
interesting part is what happens to that randomness rather than the cards.

**The seed is the shuffle.** `POST /v1/tarot/draw` returns the twelve hex
characters it dealt from, and `spread.draw(seed)` deals the same three cards the
same way round on any machine, in any process, next year. Nothing is stored
anywhere and a spread is still reproducible — the same property a chart has, and
the app prints the seed under the cards rather than hiding it.

That also closes a hole. `POST /v1/tarot/reading` costs a credit and takes a
*seed*, not a list of cards: the server deals them again and reads what it dealt.
A modified client cannot assemble a flattering spread and buy words for it.

**Two layers, one price.** Turning the cards over and reading what each one means
is free, works signed out, and calls no model — those seventy-eight cards were
written by a person, in English and Hindi, and are the same for everyone. Only
having the three read together as one piece spends anything, and it is a
deliberate tap with the cost stated next to it.

**Situation, obstacle, advice — not past, present, future.** The timeline spread
is the one every other app sells, and a timeline is a forecast. These three ask
the same questions without claiming to know what happens next, and the last card
lands on something the reader can act on. Same choice `meanings.py` makes for a
dasha lord: name what the period asks of you, never how it turns out.

**Reversed is another angle, not bad news.** Every reversed line is written as
the theme held back, overdone, or starting to loosen. Death is an ending you can
name, the Tower is a weak foundation giving way, the Ten of Swords is the bottom
of something — which means the direction from there is up. `test_tarot.py` fails
if the word "beware" ever appears in a card.

**It is grounded twice.** `tarot/grounding.py` reads the generated text back and
flags any card named that the shuffle did not deal — the same check as a
fabricated placement, in a different deck. And `ai.grounding.mentions_chart`
catches the failure specific to *this* codebase: the shared system prompt opens
by calling itself the interpretation layer of a Vedic astrology app, so a model
handed three cards will reach for a dasha to explain them. Both checks are
deliberately narrow, because half the major arcana are ordinary words — English
names are matched case-sensitively so "The Sun" is a card and "the sun" is the
sky, and names that survive no case distinction at all (मृत्यु, संसार, तारा) are
not matched in Hindi.

The deck's order and the order of the random calls in `draw()` are a contract:
change either and every seed anyone saved deals different cards. A pinned seed
in `test_tarot.py` makes that a loud decision rather than a quiet diff.

## Credits

A message costs one credit. Credits arrive from three places that differ only
in how long they last, which is the whole reason there is one currency rather
than a limit and a separate balance:

| Where from | How many | Expires |
| --- | --- | --- |
| Free | 6 | at the next Indian midnight |
| Subscription | 1,500 a month | with the period that granted them |
| Pack | what was bought | in a year |

The spend order falls out of the data: **soonest expiry first**. So the free six
are always used before anything paid for, and nobody has to be told which pocket
a message came out of.

`credit_lots` stores grants rather than a balance column. A balance is one
number and cannot answer the two questions that matter — when do these expire,
and where did they come from. `credit_spends` records each credit as it goes,
which the balance does not need and a paying person is entitled to.

**Grants are lazy, and there is no scheduled job anywhere in this product.**
Reading the balance calls `ensure_grants()`, which mints today's free six and
this month's subscription credits if they are missing. That matters most for a
yearly subscription: Razorpay charges it once, so a webhook-driven grant would
hand someone eighteen thousand credits to spend in a week. The month's grant
instead happens the next time they open the app — and someone who does not open
the app does not need the credits.

### It is enforced on the server now

This is the part that changed. Previously the app decided whether to send, the
backend had never been told who was asking, and `/v1/chat` answered anyone who
could reach it. The allowance was a request, not a rule.

Now `/v1/chat` verifies the Supabase token, spends the credit through
`consume_credit()` and only then calls the model:

- **The token is checked by asking Supabase**, not by verifying the JWT here.
  Supabase issues asymmetric signing keys and rotates them, so local
  verification means fetching a JWKS and handling rotation that happens without
  warning. One HTTP call is correct under every key type, and it is cached for
  a minute per token — against a model request measured in seconds, it does not
  register.
- **The credit is taken before the generator starts.** A `StreamingResponse`
  has already sent 200 by the time its body runs, so a refusal raised in there
  would arrive as an `error` event on a successful response rather than as the
  402 the app needs to act on.
- **401 and 402 are different answers.** Not signed in sends someone to sign
  in; out of credits sends them to the price list. Collapsing them is the kind
  of bug that reads fine and strands a paying user.
- **It fails closed.** Supabase unreachable is a 503, not a free message —
  otherwise the paywall is optional for anyone who can cause a timeout. The
  device-side reader still falls open, because it is a display now rather than
  a gate.
- **A dropped stream is not charged twice.** Every question carries a
  `request_id`, and `credit_spends` has a unique index on it.
- **An answer that never arrived is refunded.** Model capacity is the service's
  problem, and free-tier 503s are common enough that charging for them would
  make a bad day for the service into a bad day for the person paying.

### What is for sale

Prices live in [plans.py](backend/app/billing/plans.py) and are fetched by the
app rather than bundled, so a store build from six months ago draws today's
numbers — and cannot draw one this server would refuse to charge. The client
sends a plan id and nothing else; the amount, the credit count and the account
are all decided on the server.

| | Price | Credits | Per message |
| --- | --- | --- | --- |
| Free | — | 6 a day | — |
| Pack | ₹19 / ₹49 / ₹149 | 20 / 60 / 200 | ~₹0.80 |
| Monthly | ₹99 | 1,500 a month | ~₹0.07 |
| Yearly | ₹799 | 1,500 a month | ~₹0.07 |

The gap between a pack and a plan is roughly tenfold, and it is the product's
advice rather than an accident: a pack buys occasional use without a
commitment, and the pricing screen says exactly that instead of hiding the
arithmetic. `test_billing.py` asserts the gap, so a future price edit cannot
quietly close it.

Yearly is a third off, not the sixteen percent that ₹999 would have been. Below
about a quarter off, an annual plan in this market is decoration — people read
it, do the division, and stay on monthly.

### Razorpay, and the thing to know about it

**Payments go through Razorpay directly, not through in-app purchase.** Google
Play and the App Store both require IAP for digital content consumed in the
app, and this does not use it. That is a deliberate choice with a real
consequence: it is grounds for rejection or removal, and it is the first thing
to revisit if a store review goes badly.

**No native module.** Razorpay's usual React Native integration is one, which
would mean the app can no longer be opened in Expo Go. The backend creates a
hosted Payment Link (packs) or subscription page, and the app opens the URL.

**Credits come from the webhook, never from the browser coming back.** The
redirect is a convenience for the person watching; it can be lost to a closed
tab or a dead battery. `/v1/billing/webhook` is HMAC-verified over the raw
bytes — which is why the route reads `await request.body()` and parses the JSON
itself, since re-serialising a parsed body produces different bytes and a
signature that never matches. Razorpay retries until it gets a 2xx, so a
Supabase failure answers 500 rather than swallowing a paid-for credit, and
every grant is keyed on the payment id so the retry that follows grants
nothing.

### Two decisions in the UI worth keeping

- **The counter is silent until three remain.** A permanent countdown over a
  chat where people bring the worst of their week makes them ration what they
  say at exactly the wrong moment.
- **The exhausted screen always carries the helplines**, and leads with them
  when the refused message looked like distress. That check is keyword matching
  and will miss phrasings it was not taught — which is why the numbers are
  there either way, and why a miss costs nothing. Someone who has hit the wall
  while saying they want to die does not meet an upgrade prompt.

## Accounts

`mobile/src/auth/` plus `app/(auth)/` is email sign-in and sign-up against
Supabase, and [supabase/schema.sql](supabase/schema.sql) is the Postgres side —
charts, course progress, conversations and messages, each locked to its owner by
row-level security. See [supabase/README.md](supabase/README.md) to point a
project at it.

Two decisions worth keeping:

- **Optional everywhere except chat.** The chart, the panchang, matching and the
  course all work signed out. Chat does not: the conversation is stored in the
  account, and so is the credit balance it spends, so there is nowhere else to
  put either. The account screen is still offered once rather than demanded, and
  "Continue without an account" is a real answer for the rest of the app.
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

Vercel is no longer needed — this is a mobile app, not a website. The backend goes
to Render, the app goes through EAS Build to the Play Store and App Store.

### Backend

[render.yaml](backend/render.yaml) is a Render blueprint. It fetches the ephemeris
kernel during the build, so cold starts do not pay for a 32 MB download.

`GEMINI_API_KEY` is declared `sync: false`: Render asks for it once in the
dashboard rather than keeping it in a committed file. A deploy without it still
serves every deterministic endpoint and fails only the two that call a model, with
a 503 that names the variable — so the symptom is an app whose readings are broken,
not an app that is down.

Narrow `CORS_ORIGINS` before launch. The app sends no credentials, so a wide value
is not a session risk, but every request from a web origin spends this project's
model quota.

The free instance spins down when idle. That is what the device-side half of
**Caching** above is for; the server-side half starts cold on every wake.

### App

[eas.json](mobile/eas.json) has three profiles: `development` (dev client),
`preview` (an internal APK for putting on a real phone) and `production`.

**`mobile/.env` does not reach an EAS build.** It is gitignored — correctly, it
holds the Supabase project keys — and EAS builds from git in the cloud, so
anything only in that file is simply absent. Three variables have to exist as EAS
environment variables in each environment you build:

| Variable | Absent in a build means |
| --- | --- |
| `EXPO_PUBLIC_API_URL` | The app points at `localhost` — the phone talking to itself |
| `EXPO_PUBLIC_SUPABASE_URL` | Accounts and sync silently disappear; the app runs device-only |
| `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Same |

```bash
eas env:create --environment production --name EXPO_PUBLIC_API_URL --value https://your-service.onrender.com
```

All three are `EXPO_PUBLIC_`, which means they are inlined into the JS bundle and
readable by anyone who unzips it. That is correct for all three — a backend URL is
public by definition and the Supabase publishable key is designed to be shipped,
which is exactly why the RLS policies in [supabase/schema.sql](supabase/schema.sql)
are not optional. Do not mark them secret; there is nothing secret to protect, and
`GEMINI_API_KEY` — the one real secret — lives on the server and is never sent to
the app.

The first two of those failures used to be silent. The `EXPO_PUBLIC_API_URL` one
still installs and opens and then fails every screen with an ordinary network
error, so `API_NOT_CONFIGURED` in [client.ts](mobile/src/api/client.ts) detects a
release build resolving to a loopback address and the settings screen says so
under **API** rather than leaving someone reading timeouts.

Before the first store build: turn Supabase email confirmation back on
(see [supabase/README.md](supabase/README.md)), and run the pending
`update own conversations` policy if that project predates the sync layer.

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
3. **Move off the Gemini free tier before selling anything.** Twenty requests
   a day across the whole service cannot deliver 1,500 credits to one person,
   let alone to a hundred. Everything else in the billing path is built; this
   is the one thing that makes it sellable, and the margin on ₹99 for 1,500
   messages has not been checked against paid Gemini pricing.
4. **Decide the store question.** Payments go through Razorpay directly, which
   Play and the App Store both consider grounds for removal for in-app digital
   content. Either accept it knowingly, or add IAP alongside.
5. Replace the bundled city list with a real geocoder if coverage becomes a problem.
6. Divisional charts beyond D9 (D10 and friends need per-sign starting rules that
   `divisional_sign` deliberately does not encode yet).
