/**
 * Course fetching, with the device as a cache.
 *
 * The content is downloaded rather than bundled, which keeps the app small but
 * means a chapter needs the network the first time it is opened. Everything
 * fetched is kept, so re-reading works offline and switching back to a chapter
 * is instant.
 *
 * Two things are cached separately because they expire differently: the index
 * is small and worth refreshing on every visit, while a chapter's prose changes
 * rarely. The personalised line inside a chapter is chart-derived, so the cache
 * key carries the birth details it was computed for — a chart change must not
 * be answered from a stale entry.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

import { fetchChapter, fetchCourseIndex } from './client';
import type { BirthDetails, CourseChapter, CourseIndex, CourseLanguage } from './types';

const INDEX_KEY = (language: string) => `kosmiq.course.index.${language}.v1`;
const CHAPTER_KEY = (slug: string, language: string, birth: string) =>
  `kosmiq.course.chapter.${slug}.${language}.${birth}.v1`;

/** Enough of the birth details to notice a different chart, and nothing more. */
function birthKey(birth: BirthDetails | null): string {
  if (!birth) return 'none';
  return `${birth.date}T${birth.time}@${birth.latitude.toFixed(3)},${birth.longitude.toFixed(3)}`;
}

async function readCache<T>(key: string): Promise<T | null> {
  try {
    const raw = await AsyncStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

async function writeCache(key: string, value: unknown): Promise<void> {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  } catch {
    // A full disk should not stop someone reading; the network copy still works.
  }
}

/**
 * The index, network first.
 *
 * Fresh whenever the phone is online, and readable when it is not. Returning a
 * stale index offline is right: chapter titles do not go wrong, and an empty
 * screen would be worse than an old one.
 */
export async function loadCourseIndex(language: CourseLanguage): Promise<CourseIndex> {
  try {
    const index = await fetchCourseIndex(language);
    await writeCache(INDEX_KEY(language), index);
    return index;
  } catch (error) {
    const cached = await readCache<CourseIndex>(INDEX_KEY(language));
    if (cached) return cached;
    throw error;
  }
}

/**
 * One chapter, cache first.
 *
 * The opposite policy to the index, and for the reader's sake: a chapter they
 * have already opened should appear instantly and work on a train. Content this
 * static does not need re-fetching on every visit.
 */
export async function loadChapter(
  slug: string,
  language: CourseLanguage,
  birth: BirthDetails | null,
): Promise<CourseChapter> {
  const key = CHAPTER_KEY(slug, language, birthKey(birth));

  const cached = await readCache<CourseChapter>(key);
  if (cached) return cached;

  const chapter = await fetchChapter(slug, language, birth);
  await writeCache(key, chapter);
  return chapter;
}

/** Drop every cached chapter and index. Used when birth details change. */
export async function clearCourseCache(): Promise<void> {
  const keys = await AsyncStorage.getAllKeys();
  const ours = keys.filter((key) => key.startsWith('kosmiq.course.'));
  if (ours.length) await AsyncStorage.multiRemove(ours);
}
