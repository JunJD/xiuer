import {
  createSearchParamsCache,
  parseAsBoolean,
  parseAsInteger,
  parseAsString,
} from "nuqs/server";
import { getFiltersStateParser, getSortingStateParser } from "@/lib/parsers";

// 定义 notes 的列 ID
const notesColumnIds = new Set([
  "title",
  "author_nickname", 
  "liked_count",
  "comment_count",
  "is_new",
  "is_changed",
  "is_important",
  "last_crawl_time",
]);

export const searchParamsCache = createSearchParamsCache({
  page: parseAsInteger.withDefault(1),
  perPage: parseAsInteger.withDefault(10),
  filters: getFiltersStateParser(notesColumnIds).withDefault([]),
  sort: getSortingStateParser(notesColumnIds).withDefault([]),
  keyword: parseAsString.withDefault(""),
  is_new: parseAsBoolean,
  is_changed: parseAsBoolean,
  is_important: parseAsBoolean,
  today_only: parseAsBoolean.withDefault(true),
});

export type GetNotesSchema = Awaited<
  ReturnType<typeof searchParamsCache.parse>
>; 