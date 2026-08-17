/**
 * Backend client.
 *
 * The base URL is resolved rather than hard-coded: a phone running Expo Go
 * cannot reach the laptop's `localhost`, so in development we fall back to the
 * host that served the JS bundle, which is the laptop's LAN address.
 */

import Constants from 'expo-constants';

import type { BirthDetails, Place, Reading } from './types';

const DEFAULT_PORT = 8000;

function resolveBaseUrl(): string {
  const configured = process.env.EXPO_PUBLIC_API_URL?.trim();
  if (configured) return configured.replace(/\/$/, '');

  const fromExtra = (Constants.expoConfig?.extra as { apiBaseUrl?: string } | undefined)
    ?.apiBaseUrl;

  // In dev, rewrite a localhost default to the packager's host so a physical
  // device on the same network reaches the laptop instead of itself.
  const hostUri = Constants.expoConfig?.hostUri;
  if (__DEV__ && hostUri) {
    const host = hostUri.split(':')[0];
    if (host) return `http://${host}:${DEFAULT_PORT}`;
  }

  return (fromExtra ?? `http://localhost:${DEFAULT_PORT}`).replace(/\/$/, '');
}

export const API_BASE_URL = resolveBaseUrl();

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const TIMEOUT_MS = 15_000;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    });
  } catch (error) {
    // A failed fetch here is almost always the backend not running or the
    // device being unable to see it, so say that rather than "Network request
    // failed".
    const reason =
      error instanceof Error && error.name === 'AbortError'
        ? 'Request timed out'
        : 'Could not reach the server';
    throw new ApiError(`${reason} (${API_BASE_URL})`);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body?.detail === 'string') detail = body.detail;
    } catch {
      // Response body was not JSON; the status-based message stands.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export function fetchReading(details: BirthDetails, levels = 2): Promise<Reading> {
  return request<Reading>(`/v1/reading?levels=${levels}`, {
    method: 'POST',
    body: JSON.stringify(details),
  });
}

export function searchPlaces(query: string, limit = 8): Promise<Place[]> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return request<Place[]>(`/v1/places?${params.toString()}`);
}
