# Enuma Sky

AI-powered Vedic astrology app built to take astrology back from fear and
fatalism. Mobile-first (React Native + Expo), Python backend, Postgres/Supabase
for user data.

**The mission:** to end the fear this trade runs on. People have been sold
"flawed charts", doshas to be cured, and a future already written. Enuma Sky
starts from the opposite position: no chart is wrong, no planet decides or
reveals anyone's future, and astrology is worth having as a lens for reflection
and nerve — not as a verdict. The tagline is the whole product in three words:
**astrology without fear.**

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
| Tarot | 78-card deck in two languages, seeded shuffle, three-card spread; the written meanings and the draw are free, reading the spread together needs Pro. 36 tests |
| AI interpretation layer | Built on Gemini, verified against the live API |
| Crisis-support path | Checked live, one breach found and closed; re-check pending on two models |
| Accounts | Email sign-in/sign-up, optional |
| Sync | Chart, course progress and chat history mirrored to Supabase; checked end to end against a live project |
| Caching | Two layers, device and server; measured 14.0s → 0.075s on a live repeat |
| Subscriptions | Enuma Sky Pro, sold by the App Store and Google Play through RevenueCat; enforced server-side against RevenueCat's API. Unit-tested. **Not yet run against a live store account** |
| Rate limiting | Per-account on everything that calls a model, per-address on everything else. In-process, so it multiplies across instances |

## Layout

```
supabase/         schema.sql and setup notes for the Postgres side
backend/          FastAPI service and the deterministic engine
  app/astro/      The engine. No I/O, no AI, no randomness.
  app/api/        HTTP surface
  app/ai/         Interpretation layer. Translates engine output; never computes.
  app/auth.py     verifies the Supabase token — who is asking
  app/entitlements.py  asks RevenueCat whether they have paid; the only gate
  app/ratelimit.py     fixed-window ceilings, per account and per address
  tests/          251 tests, including known-chart, grounding, cache, entitlement and tarot
  app/tarot/      the deck (written, not generated), the seeded shuffle, the card check
  app/course/     the course — 30 chapters of prose, in two languages
  app/places_data.py  ~3,000 places, India tier-1 to tier-3; built by scripts/
mobile/           Expo app (React Native + TypeScript)
  app/            expo-router screens; (app)/ sits behind the drawer
  src/            theme, API client, components
  src/sync/       the account mirror — see supabase/README.md
  src/purchases/  RevenueCat: the paywall, the entitlement, restore
  src/auth/storage.ts  the session, in the Keychain rather than a plain file
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
| `POST /v1/tarot/reading` | The spread read as one piece. **Pro** |
| `POST /v1/interpret` | Plain-language reading of a chart. **Pro** |
| `POST /v1/tip` | The one line the home screen opens with. **Pro** |
| `POST /v1/chat` | Question about a chart, streamed as server-sent events. **Pro** |
| `GET /v1/billing/status` | Whether the server agrees this account is Pro. Open, so a paywall can draw itself |
| `POST /v1/billing/refresh` | The same, cache dropped first. For the moment after a purchase |

Everything not marked **Pro** is deterministic, free, and needs no account: it
is arithmetic from a birth moment, and the same input gives the same answer
every time. Everything marked **Pro** calls a model, costs real money per
request, and answers 401 signed out, 402 without a subscription, 429 too fast.

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

That also closes a hole. `POST /v1/tarot/reading` takes a *seed*, not a list of
cards: the server deals them again and reads what it dealt. A modified client
cannot assemble a flattering spread and ask for words about it.

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

The reading is held to the same line, and that rule was written after watching
it break. The first live reply on a device opened "नौकरी के मामले में अभी स्थिति
बहुत अच्छी है" — a verdict on the reader's circumstances, from a draw that only
said "recognition". `tarot_directive` now forbids ranking the situation in the
same words `tip_directive` already forbids ranking the day, because it is the
same model reaching for the same reassurance.

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

**The card faces are generated, not drawn by anyone.** Seventy-eight
illustrations is a licensing problem and a forty-megabyte install, so
`TarotCard.tsx` builds a face out of the three fields the API already sends —
arcana, suit, number. What makes it read as a card is the furniture rather than
the picture: a gilt frame with corner marks, the numeral in a band at the top,
the name in a band at the foot, and on a numbered card **the suit mark repeated
as many times as the number says**, in the columns a real pip card uses. Three
of Cups has three cups on it. The four suit grounds are the theme's element
lights — Wands fire, Cups water, Swords air, Pentacles earth — matched by eye
rather than by hex, because a navy at the same numeric lightness as a violet
still reads as black beside it.

`SPREAD_NOTE` is still returned by `/v1/tarot/draw` and is no longer rendered.
The screen used to carry it under the seed alongside a second, shorter note
that said the same thing; both were read once and scrolled past forever. The
seed line stayed because it is the only part of that block anyone can act on.

The deck's order and the order of the random calls in `draw()` are a contract:
change either and every seed anyone saved deals different cards. A pinned seed
in `test_tarot.py` makes that a loud decision rather than a quiet diff.

## Subscriptions

Enuma Sky Pro, one entitlement, sold by the App Store and Google Play through
RevenueCat. The split is by feature, not by count:

| Free, and needs no account | Pro |
| --- | --- |
| Chart, navamsa, house lords | The opening reading |
| Vimshottari dashas to 3 levels | Questions about your chart |
| Panchang, today and at birth | The daily line on the home screen |
| Ashtakoot matching | Reading a tarot spread together |
| Turning the cards over | |
| The whole course | |

The left column is arithmetic — same input, same answer, no model, no marginal
cost. The right column calls Gemini. That is the whole rule, and it is one a
reader can hold in their head.

### What was here before, and why it is not

A credit ledger. A message cost one credit; credits came from a free six a day,
from packs bought outright through Razorpay, and from a subscription that
granted 1,500 a month. Lots, spends, expiries, a lazy grant on every balance
read, and a spend order of soonest-expiry-first so the free ones went before
anything paid for. It was a careful design and it worked.

**It was also optional, and that is why it is gone.** `consume_credit` took an
idempotency key so that a question whose stream died could be re-asked without
paying twice — a good idea — and the key came from the client, and a repeated
key was answered `ok: true, replayed: true`. So one fixed `request_id`, sent
forever, was charged exactly once, ever. A modified app had unlimited paid
messages for ₹19, and nothing in the server's logs would look wrong.

The fix is not a better key. A subscription is not a currency: there is nothing
to meter, so there is nothing to replay. `request_id` is out of the schema,
`app/billing/` is deleted, and
`test_entitlements.py::test_a_client_cannot_replay_its_way_past_the_gate` is the
regression that says the shape of that bug did not survive the rewrite.

Two other things went with it. Razorpay, because Apple and Google both require
that digital goods consumed inside an app are sold through their own billing —
the hosted-page trick was the right answer for a web product and a rejected
build for this one. And the free six a day, replaced by the table above: a
feature line is easier to explain than a number, and it does not make anyone
ration what they say.

To drop the tables from a project that ran the old schema, see
[supabase/migrations/2026-09-01-drop-credits.sql](supabase/migrations/2026-09-01-drop-credits.sql).
Read the warning at the top of it — it takes the Razorpay payment history with
it.

### It is enforced on the server, and only there

`backend/app/entitlements.py` reads the entitlement from RevenueCat's API with
the secret key, caches the answer for a minute, and refuses anything else.

- **The device is not asked.** `usePurchases()` decides what a screen draws; it
  does not decide what the server gives away, because a rooted phone can say
  anything. The app's own check before sending is a courtesy that saves a round
  trip, and the 402 that comes back is what actually decides.
- **Three failures, three statuses.** 401 signed out, 402 signed in without a
  plan, 503 RevenueCat unreachable. One status for all three would leave the app
  guessing which screen to show — and would tell a subscriber, during an outage
  on our side, that their payment did not work.
- **Failure is closed.** An unverifiable entitlement is a refusal. The one
  exception is a deployment with no RevenueCat key, where nothing is for sale
  and nothing is gated, which is how the engine runs locally; the server says so
  in its startup log.
- **`/v1/billing/status` exists so the two answers can be compared.** Nothing
  gates on it. It is there for the case where the store says Pro and the server
  does not — a purchase that never reached RevenueCat, a `logIn` that did not
  attach the receipt — which is invisible from the inside and reads as theft
  from the outside. The plans screen says so plainly when it sees it.

### Two decisions in the UI worth keeping

- **There is no counter, and there was never a good one.** A countdown over a
  chat where people bring the worst of their week makes them ration what they
  say at exactly the wrong moment. The old one was not even honest, since the
  number came from a ledger the app could not enforce.
- **The blocked screen always carries the helplines**, and shows *only* them
  when the refused message looked like distress — no price, no plan, no upgrade
  button. That check is keyword matching and will miss phrasings it was not
  taught, which is why the numbers are there either way and why a miss costs
  nothing. Someone who has hit the wall while saying they want to die is not a
  conversion opportunity.

## Accounts

`mobile/src/auth/` plus `app/(auth)/` is email sign-in and sign-up against
Supabase, and [supabase/schema.sql](supabase/schema.sql) is the Postgres side —
charts, course progress, conversations and messages, each locked to its owner by
row-level security. See [supabase/README.md](supabase/README.md) to point a
project at it.

Two decisions worth keeping:

- **Optional everywhere except chat.** The chart, the panchang, matching and the
  course all work signed out. Chat does not: the conversation is stored in the
  account, and so is the subscription that pays for it, so there is nowhere else
  to put either. The account screen is still offered once rather than demanded, and
  "Continue without an account" is a real answer for the rest of the app.
- **The app runs with no Supabase project at all.** `isConfigured()` is false
  when the env vars are missing, the account screen never appears, and
  everything behaves as it did before auth existed. An app that will not open
  because a backend nobody has set up yet is missing is worse than one that
  quietly works offline.

**Deleting an account is the account's own to do.** Settings → *Delete account*
calls `delete_own_account()`, a `security definer` function in the project, and
every table cascades off the `auth.users` row it removes; the phone's copy is
cleared straight afterwards by `clearDeviceData()`. Both stores require an app
with accounts to offer this from inside the app, and an email address to write
to does not satisfy it. The route deliberately avoids the obvious alternative —
a backend endpoint holding the service-role key — because that key reads and
writes every account's rows, which is a large permission to keep standing so
that one button can work.

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
3. **Move off the Gemini free tier before selling anything.** Twenty requests a
   day across the whole service cannot serve one subscriber, let alone a
   hundred, and "unlimited questions" is now a promise on the plans screen
   rather than a quota to divide up. Everything else in the paid path is built;
   this is the one thing that makes it sellable, and the margin has not been
   checked against paid Gemini pricing.
4. **Run the store path end to end.** RevenueCat is wired on both sides but has
   never seen a live store account: products in App Store Connect and Play
   Console, mapped to the `enuma_sky_pro` entitlement, a sandbox purchase, and a
   check that `/v1/billing/status` agrees with the device afterwards.
5. Replace the bundled city list with a real geocoder if coverage becomes a problem.
6. Divisional charts beyond D9 (D10 and friends need per-sign starting rules that
   `divisional_sign` deliberately does not encode yet).

## Acknowledgments & Credits

- **Astronomical Ephemeris:** Planetary ephemerides courtesy of **NASA JPL (Jet Propulsion Laboratory)** DE440s (Public Domain).
- **Ephemeris Computation:** Powered by [Skyfield](https://rhodesmill.org/skyfield/) (MIT License) by Brandon Rhodes.
- **Subscriptions & In-App Purchases:** Powered by [RevenueCat](https://www.revenuecat.com/).
- **Safety & Mental Health Helplines:** Integrated with Tele-MANAS (14416), AASRA, Women Helpline (181), and National Emergency (112).

## License

This project is open source and licensed under the [MIT License](LICENSE) by Deepak Singh.
