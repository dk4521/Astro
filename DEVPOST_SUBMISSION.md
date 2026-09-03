# Enuma Sky — Devpost Submission Draft (Shipaton 2026)

> **Instructions:** Use the text below to fill in the Devpost submission fields for **RevenueCat Shipaton 2026**. Everything has been structured exactly as Devpost prompts request.

---

## 1. Project Overview

- **Project Title:** Enuma Sky
- **Tagline (under 140 characters):**  
  *Vedic astrology without fear: precision NASA JPL calculations, grounded AI readings, and instant mental health crisis intervention.*
- **GitHub Repository URL:** [https://github.com/dk4521/Astro](https://github.com/dk4521/Astro)
- **License:** MIT License (Author: Deepak Singh)
- **Tech Stack / Tags:** `react-native`, `expo`, `typescript`, `python`, `fastapi`, `revenuecat`, `supabase`, `gemini-api`, `nasa-jpl`, `skyfield`, `astronomy`

---

## 2. Devpost Story Fields

### Inspiration (Why we built it)
For centuries, Vedic astrology has been dominated by fear-mongering: people are told their birth charts are "cursed" or "flawed", burdened with fabricated *doshas* (like Manglik or Kaal Sarp), and pushed into buying expensive gemstones, rituals, or fatalistic remedies. 

We built **Enuma Sky** to dismantle this fear-based trade once and for all.

Our core premise is simple and uncompromising:
1. **No birth chart is broken:** Every human chart is whole. There are no cursed placements or doomed destinies.
2. **The future is not a predetermined script:** Planets don't decide anyone's life; astrology is a psychological lens for self-reflection and courage, not a verdict.
3. **Astrology without fear:** We offer clarity and scientific grounding instead of anxiety.

---

### What it does
**Enuma Sky** is an AI-powered, bilingual (English & Hindi) Vedic astrology and reflective wellness app built around high-precision astronomical computation and strict ethical safety:

1. **High-Precision Natal Engine:** Computes rising signs (Lagna), 9 Vedic planetary bodies, 27 Nakshatras, Vimshottari Dashas, and Panchang using deterministic ephemerides backed by **NASA JPL DE440s** via Skyfield.
2. **Grounded AI Readings (Zero Hallucination):** The AI operates strictly as an interpreter, never a calculator. Every claim made by the LLM is verified across Sanskrit, English, and Devanagari by a deterministic validator (`grounding.py`). Every verified response displays a visible **Grounded** badge.
3. **Crisis Intervention Safety Net:** If a user expresses hopelessness, self-harm, or despair, astrology immediately stops. The app routes the user to verified government and community mental health hotlines (**Tele-MANAS 14416, AASRA, 112**).
4. **Interactive 30-Chapter Course:** A comprehensive guide to Vedic concepts that teaches principles directly using the user’s own birth chart calculations rather than generic horoscope articles.
5. **Deterministic Seed-Based Tarot:** A 78-card deck using reproducible cryptographic seeds for 3-card spreads (Situation, Obstacle, Advice), reframing inverted cards into constructive insights rather than doom.
6. **RevenueCat Subscriptions (Enuma Sky Pro):** Transparent monetization with Weekly, Monthly, Annual, and Lifetime tiers, verified server-side against RevenueCat's REST API.

---

### How we built it
We built Enuma Sky with a privacy-first, separation-of-concerns architecture:
- **Mobile Client:** Built with React Native & Expo Router in TypeScript, featuring a serene, dark-mode cosmic aesthetic designed to oppose the noisy, ad-cluttered design of traditional astrology apps.
- **Astronomical Backend:** Built in Python using FastAPI. To avoid AGPL licensing traps, we replaced C-based Swiss Ephemeris with pure-Python **Skyfield** and **NASA JPL DE440s** kernels, achieving planetary precision within 1.7 arcseconds across 150 years of benchmarks.
- **AI & Grounding Layer:** Uses Google Gemini with structured system contracts and a custom verification engine (`grounding.py`) that matches AI statements against exact ephemeris values.
- **Accounts & Sync:** Supabase Postgres with row-level security (RLS) for optional chart sync, history, and course progress.
- **Monetization Stack:** Integrated with **RevenueCat SDK** on the client and verified server-side via `backend/app/entitlements.py`.

---

### Challenges we ran into
- **Stopping AI Hallucinations in Astrology:** Language models cannot reliably do spherical trigonometry or calculate degrees. We completely isolated the math into deterministic astronomical code and built a strict multi-script grounding verification system.
- **Ethical Crisis Routing:** Ensuring the LLM never bypasses safety. We implemented strict boundary checks so that when crisis language is detected, the pipeline halts horoscope generation entirely and provides immediate support resources.
- **Clean Licensing:** Ensuring full open-source compliance for the Next Gen category by migrating from AGPL-bound libraries to an MIT-licensed Skyfield + NASA JPL public-domain pipeline.

---

### Accomplishments that we're proud of
- **250+ Passing Automated Tests (`pytest`):** Comprehensive test suite covering astronomical ephemeris accuracy, grounding logic, entitlement checks, and reproducible tarot shuffles.
- **Grounded Badge in the UI:** Giving users total transparency over whether an AI response was verified against physical planetary physics.
- **Crisis Response Pipeline:** Proving that a spiritual/astrological app can take mental health and user safety seriously.
- **Zero Ads, Zero Dark Patterns:** Clean, respectful UX where core charts and daily panchang are free forever.

---

### What we learned
- **LLMs should interpret, never compute:** Separation between deterministic calculations and generative language layers is essential for domain-critical mobile apps.
- **Ethical software stands out:** By rejecting the industry-standard fear tactics, users feel empowered and calm rather than anxious.

---

### What's next for Enuma Sky
- Completing store builds for Google Play Store and Apple App Store.
- Adding global offline geocoding beyond the bundled ~3,000 cities.
- Introducing advanced divisional harmonic charts (D10, D60) with interactive chart visualizers.

---

## 3. Category-Specific Submission Answers

### Next Gen Award (Student Category)
- **Student Verification:** Active student developing under academic domain on Devpost.
- **Open-Source Repository:** [https://github.com/dk4521/Astro](https://github.com/dk4521/Astro)
- **License:** Official open-source [MIT License](https://github.com/dk4521/Astro/blob/main/LICENSE) included in the repository root.
- **How RevenueCat is used:** RevenueCat SDK powers the in-app subscription flow (`mobile/src/purchases/`), with server-side validation in `backend/app/entitlements.py`.

### RevenueCat Peace Prize (Social Good)
- Traditional astrology exploits psychological vulnerabilities to sell unscientific fear remedies. Enuma Sky transforms astrology into an anxiety-free self-reflection tool, reinforces that no human is born with a "bad chart", and incorporates a crisis intervention path that halts predictions to provide direct links to national mental health helplines (Tele-MANAS 14416).

### HAMM Award (Monetization Strategy)
- Enuma Sky implements a clean, ethical monetization model powered by RevenueCat. Free users get their core natal chart, today's panchang, active dasha, and basic tarot card meanings. Enuma Sky Pro unlocks in-depth AI chart dialogues, 3-card integrated tarot synthesis, and unlimited personalized inquiries across weekly, monthly, annual, and lifetime options. All entitlements are securely validated server-side.

### RevenueCat Design Award (Craft & Aesthetics)
- Intentionally designed with a calming, celestial dark palette with high-contrast typography and smooth micro-animations. Replaces the chaotic, aggressive red-and-gold ads typical of legacy astrology apps with a serene, meditative user experience.
