/**
 * Wire types mirroring the backend's pydantic schemas.
 *
 * Kept hand-written rather than generated so the app compiles standalone; if
 * they drift from `backend/app/schemas.py` the API tests there are the source
 * of truth.
 */

export type BirthDetails = {
  date: string; // YYYY-MM-DD
  time: string; // HH:MM
  latitude: number;
  longitude: number;
  place?: string | null;
  timezone?: string | null;
};

/**
 * Every `_hi` field arrives beside its Latin twin, never instead of it, so
 * switching language is a re-render rather than a refetch.
 */
export type Placement = {
  longitude: number;
  rashi: string;
  rashi_en: string;
  rashi_hi: string;
  rashi_lord: string;
  rashi_lord_hi: string;
  degree: number;
  degree_dms: string;
  nakshatra: string;
  nakshatra_hi: string;
  nakshatra_lord: string;
  nakshatra_lord_hi: string;
  pada: number;
  navamsa: string;
  navamsa_hi: string;
};

export type Graha = {
  graha: string;
  graha_hi: string;
  house: number;
  retrograde: boolean;
  combust: boolean;
  speed: number;
  placement: Placement;
};

export type ChartMeta = {
  birth_local: string;
  birth_utc: string;
  timezone: string;
  latitude: number;
  longitude: number;
  place: string | null;
  julian_day: number;
  ayanamsa: number;
  ayanamsa_name: string;
  ayanamsa_name_hi: string;
  ephemeris_mode: string;
  house_system: string;
};

export type Chart = {
  meta: ChartMeta;
  lagna: Placement;
  grahas: Graha[];
  houses: Record<string, string>;
  house_lords: Record<string, string>;
  navamsa: Record<string, string>;
  moon_rashi: string;
  moon_rashi_hi: string;
  janma_nakshatra: string;
  janma_nakshatra_hi: string;
};

export type Panchang = {
  tithi: string;
  tithi_hi: string;
  tithi_number: number;
  paksha: string;
  paksha_hi: string;
  tithi_percent: number;
  nakshatra: string;
  nakshatra_hi: string;
  nakshatra_pada: number;
  yoga: string;
  yoga_hi: string;
  karana: string;
  karana_hi: string;
  vara: string;
  vara_hi: string;
  vara_lord: string;
  vara_lord_hi: string;
  masa: string;
  masa_hi: string;
  /** Chaitradi reckoning: the year turns at Chaitra Shukla Pratipada. */
  vikram_samvat: number;
  shaka_samvat: number;
  /**
   * ISO instants, or null. Null is a real answer rather than a failure: the
   * Moon skips a rise once a month, and a polar Sun skips both for months —
   * so these render as a dash, never as a guess.
   */
  sunrise: string | null;
  sunset: string | null;
  moonrise: string | null;
  moonset: string | null;
};

export type DashaPeriod = {
  lord: string;
  lord_hi: string;
  start: string;
  end: string;
  level: number;
  years: number;
  children: DashaPeriod[];
  /**
   * What the tradition associates with this lord — written by a person, never
   * generated. Null on every period except the ones actually running: a full
   * timeline is several hundred entries, and the same nine sentences repeated
   * through it would be a hundred kilobytes of nothing.
   */
  meaning: string | null;
  meaning_hi: string | null;
};

export type Dasha = {
  janma_nakshatra: string;
  janma_nakshatra_lord: string;
  balance_years: number;
  as_of: string;
  active: DashaPeriod[];
  periods: DashaPeriod[];
};

export type Reading = {
  chart: Chart;
  panchang: Panchang;
  dasha: Dasha;
};

export type Place = {
  name: string;
  admin: string;
  country: string;
  latitude: number;
  longitude: number;
};

/**
 * Hinglish is the backend's default because it is how the target users talk.
 */
export type Language = 'en' | 'hi' | 'hinglish';

export type Interpretation = {
  text: string;
  language: Language;
  /**
   * False when the text contradicts the computed chart. Checked after
   * generation rather than requested of the model, so it is a measurement and
   * the app should show it rather than assume it.
   */
  grounded: boolean;
  contradictions: string[];
};

/** One of the eight koots, with the values it was computed from. */
export type Koot = {
  name: string;
  points: number;
  maximum: number;
  bride: string;
  bride_hi: string;
  groom: string;
  groom_hi: string;
};

/**
 * Ashtakoot Milan.
 *
 * Note what is absent and stays absent: no verdict, no threshold, no label. A
 * score out of 36 is not a fact about two people — the course says so in
 * chapter 30 — and the shape of this type is where that position is kept
 * honest.
 */
export type Match = {
  koots: Koot[];
  total: number;
  maximum: number;
  bride_nakshatra: string;
  bride_nakshatra_hi: string;
  bride_rashi: string;
  bride_rashi_hi: string;
  groom_nakshatra: string;
  groom_nakshatra_hi: string;
  groom_rashi: string;
  groom_rashi_hi: string;
};

/** The home screen's daily line, in the companion's voice. */
export type Tip = {
  text: string;
  language: Language;
  companion: string | null;
  /** False when the line named a placement it was told not to name. */
  grounded: boolean;
};

export type ChatTurn = {
  role: 'user' | 'assistant';
  content: string;
};

// --- Course ----------------------------------------------------------------
//
// Chapters live on the server. The app holds an index and whatever chapters the
// reader has opened, cached on the device — see `src/api/course.ts`.

export type CourseLanguage = 'en' | 'hi';

export type CourseEntry = {
  slug: string;
  number: number;
  part: string;
  title: string;
  summary: string;
  minutes: number;
  level: 'basic' | 'intermediate';
};

export type CourseIndex = {
  language: CourseLanguage;
  chapters: CourseEntry[];
  total_minutes: number;
};

export type ChapterSection = {
  heading: string;
  body: string[];
  aside: string | null;
};

export type CourseChapter = {
  slug: string;
  number: number;
  part: string;
  title: string;
  summary: string;
  minutes: number;
  level: 'basic' | 'intermediate';
  language: CourseLanguage;
  sections: ChapterSection[];
  next_slug: string | null;
  /** Computed from the chart by the engine. Null when there was no example. */
  in_your_chart: string | null;
};

// --- Today -----------------------------------------------------------------

export type Today = {
  as_of: string;
  timezone: string;
  place: string | null;
  panchang: Panchang;
  moon_rashi: string;
  moon_rashi_hi: string;
  moon_nakshatra: string;
  moon_nakshatra_hi: string;
  sun_rashi: string;
  sun_rashi_hi: string;
  active: DashaPeriod[];
  birth_moon_rashi: string;
  birth_moon_rashi_hi: string;
  birth_nakshatra: string;
  birth_nakshatra_hi: string;
};
