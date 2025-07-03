import {
  createSearchParamsCache,
  parseAsArrayOf,
  parseAsInteger,
} from "nuqs/server";
import * as z from "zod";
import { getFiltersStateParser } from "@/lib/parsers";
// import { TaskStatusEnum } from "@/app/openapi-client/types.gen";

export const searchParamsCache = createSearchParamsCache({
  page: parseAsInteger.withDefault(1),
  perPage: parseAsInteger.withDefault(10),
  filters: getFiltersStateParser().withDefault([]),
  status: parseAsArrayOf(z.enum(["pending", "running", "completed", "failed"])).withDefault([]),
});

// export const createTaskSchema = z.object({
//   title: z.string(),
//   label: z.enum(tasks.label.enumValues),
//   status: z.enum(tasks.status.enumValues),
//   priority: z.enum(tasks.priority.enumValues),
//   estimatedHours: z.coerce.number().optional(),
// });

// export const updateTaskSchema = z.object({
//   title: z.string().optional(),
//   label: z.enum(tasks.label.enumValues).optional(),
//   status: z.enum(tasks.status.enumValues).optional(),
//   priority: z.enum(tasks.priority.enumValues).optional(),
//   estimatedHours: z.coerce.number().optional(),
// });

// export type GetTasksSchema = Awaited<
//   ReturnType<typeof searchParamsCache.parse>
// >;
// export type CreateTaskSchema = z.infer<typeof createTaskSchema>;
// export type UpdateTaskSchema = z.infer<typeof updateTaskSchema>;