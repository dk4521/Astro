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

export type Placement = {
  longitude: number;
  rashi: string;
  rashi_en: string;
  rashi_lord: string;
  degree: number;
  degree_dms: string;
  nakshatra: string;
  nakshatra_lord: string;
  pada: number;
  navamsa: string;
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
  janma_nakshatra: string;
};

export type Panchang = {
  tithi: string;
  tithi_number: number;
  paksha: string;
  tithi_percent: number;
  nakshatra: string;
  nakshatra_pada: number;
  yoga: string;
  karana: string;
  vara: string;
  vara_lord: string;
};

export type DashaPeriod = {
  lord: string;
  lord_hi: string;
  start: string;
  end: string;
  level: number;
  years: number;
  children: DashaPeriod[];
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
