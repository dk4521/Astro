/**
 * Birth date and time, as a person types them and as the API wants them.
 *
 * The two are not the same string. India writes 15-11-2001; the backend takes
 * ISO 8601, 2001-11-15. Keeping the display form in state and converting once
 * at the edge means the field never fights the typist, and the wire format is
 * decided in exactly one place instead of at each call site.
 */

/** `15112001` → `15-11-2001`, with the dashes appearing as the digits arrive. */
export function formatDateInput(next: string, previous: string): string {
  // Backspacing onto a separator must delete the digit before it. Without this
  // the formatter puts the dash straight back and the caret cannot move left.
  const text =
    next.length < previous.length && previous.endsWith('-') ? next.slice(0, -1) : next;

  const digits = text.replace(/\D/g, '').slice(0, 8);
  let out = digits.slice(0, 2);
  if (digits.length >= 2) out += `-${digits.slice(2, 4)}`;
  if (digits.length >= 4) out += `-${digits.slice(4, 8)}`;
  return out;
}

/** `0742` → `07:42`, same rules. */
export function formatTimeInput(next: string, previous: string): string {
  const text =
    next.length < previous.length && previous.endsWith(':') ? next.slice(0, -1) : next;

  const digits = text.replace(/\D/g, '').slice(0, 4);
  let out = digits.slice(0, 2);
  if (digits.length >= 2) out += `:${digits.slice(2, 4)}`;
  return out;
}

const DISPLAY_DATE = /^(\d{2})-(\d{2})-(\d{4})$/;
const DISPLAY_TIME = /^(\d{2}):(\d{2})$/;

/**
 * `15-11-2001` → `2001-11-15`, or null if that is not a day that existed.
 * Rejects 31-02, year zero, and anything still in the future — a birth date
 * the calendar disagrees with would otherwise reach the ephemeris and come
 * back as an opaque server error.
 */
export function toIsoDate(display: string): string | null {
  const match = DISPLAY_DATE.exec(display);
  if (!match) return null;

  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  if (month < 1 || month > 12 || day < 1 || year < 1800) return null;

  const date = new Date(Date.UTC(year, month - 1, day));
  const real =
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day;
  if (!real || date.getTime() > Date.now()) return null;

  return `${match[3]}-${match[2]}-${match[1]}`;
}

/** `07:42` → `07:42`, or null. Separate from the date so the errors can differ. */
export function toIsoTime(display: string): string | null {
  const match = DISPLAY_TIME.exec(display);
  if (!match) return null;
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  if (hours > 23 || minutes > 59) return null;
  return display;
}

/** `2001-11-15` → `15-11-2001`, for showing a stored value back to someone. */
export function toDisplayDate(iso: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return match ? `${match[3]}-${match[2]}-${match[1]}` : iso;
}
