import {
  createSearchParamsCache,
  parseAsBoolean,
  parseAsInteger,
  parseAsString,
} from "nuqs/server";
import { getFiltersStateParser } from "@/lib/parsers";

export const searchParamsCache = createSearchParamsCache({
  page: parseAsInteger.withDefault(1),
  perPage: parseAsInteger.withDefault(10),
  filters: getFiltersStateParser().withDefault([]),
  keyword: parseAsString.withDefault(""),
  is_new: parseAsBoolean,
  is_changed: parseAsBoolean,
  is_important: parseAsBoolean,
  today_only: parseAsBoolean.withDefault(true),
});

export type GetNotesSchema = Awaited<
  ReturnType<typeof searchParamsCache.parse>
>; 