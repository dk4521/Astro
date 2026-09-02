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

import { COURSE_NAMESPACE, birthKey, readCache, writeCache } from './cache';
import { fetchChapter, fetchCourseIndex } from './client';
import type { BirthDetails, CourseChapter, CourseIndex, CourseLanguage } from './types';

const INDEX_KEY = (language: string) => `${COURSE_NAMESPACE}index.${language}.v1`;
const CHAPTER_KEY = (slug: string, language: string, birth: string) =>
  `${COURSE_NAMESPACE}chapter.${slug}.${language}.${birth}.v1`;

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
 * The index if it is already on the device, and null otherwise.
 *
 * For callers that want the chapter count but must not cause a request to get
 * it — the home card, which paints before anything has been asked for. Someone
 * who has never opened the course has no cached index and no progress to show,
 * which is the right answer for them anyway.
 */
export async function loadCachedCourseIndex(
  language: CourseLanguage,
): Promise<CourseIndex | null> {
  return readCache<CourseIndex>(INDEX_KEY(language));
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


