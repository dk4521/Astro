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
| Astrology engine (ephemeris, chart, dasha, panchang) | Built, 110 tests passing |
| REST API (FastAPI) | Built, running locally |
| Mobile app (Expo, TypeScript) | Onboarding + chart screen, bundles clean |
| AI interpretation layer | Built on Gemini, verified against the live API |
| Supabase / accounts | Not started |
| Caching | Not started |

## Layout

```
backend/          FastAPI service and the deterministic engine
  app/astro/      The engine. No I/O, no AI, no randomness.
  app/api/        HTTP surface
  app/ai/         Interpretation layer. Translates engine output; never computes.
  tests/          110 tests, including known-chart and grounding checks
mobile/           Expo app (React Native + TypeScript)
  app/            expo-router screens
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
./.venv/bin/python -m pytest          # 110 tests
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
  graha in rashi, in nakshatra, in house — against what was computed. It recognises
  both Sanskrit and English sign names and Sanskrit graha names, so Hindi and
  Hinglish replies are checked too. Every response carries a `grounded` flag; on
  `/v1/chat` the verdict arrives as the terminal SSE event, since a stream reaches
  the reader before there is a complete claim to check.
- **The prompt contract** lives in [prompts.py](backend/app/ai/prompts.py) and is
  the actual product: no fear language, no doshas framed as curses, no remedies
  prescribed, no ranking charts as strong or weak. It answers the person before the
  chart, and drops astrology entirely when someone is in crisis — surfacing real
  help (Tele-MANAS 14416, AASRA) instead.

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
(`ASTRO_FALLBACK_MODELS`) on 503/429 and fails over. A 400 propagates immediately,
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

## Deployment

`backend/render.yaml` is a Render blueprint. It fetches the ephemeris kernel during
the build, so cold starts do not pay for a 32 MB download. Narrow `CORS_ORIGINS`
before launch.

Vercel is no longer needed — this is a mobile app, not a website. Distribution goes
through EAS Build to the Play Store and App Store.

## Next

1. Test the crisis-support path against the live API — the one branch of the
   prompt contract still unverified, and the reason two safety categories are
   relaxed.
2. Prompt tuning on Gemini: readings run long (~2000 chars vs the "two to four
   short paragraphs" the contract asks for) and use bullet lists the contract
   tells it to avoid.
3. Wire `/v1/interpret` and `/v1/chat` into the mobile app.
4. Supabase: accounts, saved charts, chat history.
5. Daily-horoscope caching — generate once per day per user segment, not per request.
6. Replace the bundled city list with a real geocoder if coverage becomes a problem.
7. Divisional charts beyond D9 (D10 and friends need per-sign starting rules that
   `divisional_sign` deliberately does not encode yet).
