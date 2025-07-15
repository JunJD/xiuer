"use server";

import { cookies } from "next/headers";
import { getNotesStats, searchNotes, getNoteDetail } from "@/app/clientService";
import { noteQuerySchema, NotesQueryParams } from "@/lib/definitions";

export async function fetchNotesStats() {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await getNotesStats({
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (error) {
    return { message: error };
  }

  return data;
}

export async function fetchNotes(queryParams: Partial<NotesQueryParams> = {}) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  // 使用默认值并合并用户提供的参数
  const params: NotesQueryParams = {
    limit: 500,
    offset: 0,
    today_only: true,
    ...queryParams,
  };

  // 构建查询参数，只包含有效值
  const searchParams: Record<string, unknown> = {
    limit: params.limit,
    offset: params.offset,
  };

  if (params.keyword) searchParams.keyword = params.keyword;
  if (params.is_new !== undefined) searchParams.is_new = params.is_new;
  if (params.is_changed !== undefined) searchParams.is_changed = params.is_changed;
  if (params.is_important !== undefined) searchParams.is_important = params.is_important;
  if (params.author_user_id) searchParams.author_user_id = params.author_user_id;
  if (params.today_only !== undefined) searchParams.today_only = params.today_only;

  const { data, error } = await searchNotes({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    query: searchParams,
  });

  if (error) {
    return { message: error };
  }

  return data;
}

export async function fetchNoteDetail(noteId: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await getNoteDetail({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    path: {
      note_id: noteId,
    },
  });

  if (error) {
    return { message: error };
  }

  return data;
}

export async function searchNotesByQuery(prevState: {}, formData: FormData) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const validatedFields = noteQuerySchema.safeParse({
    keyword: formData.get("keyword") || undefined,
    is_new:
      formData.get("is_new") === "true"
        ? true
        : formData.get("is_new") === "false"
          ? false
          : undefined,
    is_changed:
      formData.get("is_changed") === "true"
        ? true
        : formData.get("is_changed") === "false"
          ? false
          : undefined,
    is_important:
      formData.get("is_important") === "true"
        ? true
        : formData.get("is_important") === "false"
          ? false
          : undefined,
    author_user_id: formData.get("author_user_id") || undefined,
    limit: parseInt(formData.get("limit")?.toString() || "50"),
    offset: parseInt(formData.get("offset")?.toString() || "0"),
    today_only:
      formData.get("today_only") === "true"
        ? true
        : formData.get("today_only") === "false"
          ? false
          : undefined,
  });

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors };
  }

  const {
    keyword,
    is_new,
    is_changed,
    is_important,
    author_user_id,
    limit,
    offset,
    today_only,
  } = validatedFields.data;

  const queryParams: Record<string, unknown> = {
    limit,
    offset,
  };

  if (keyword) queryParams.keyword = keyword;
  if (is_new !== undefined) queryParams.is_new = is_new;
  if (is_changed !== undefined) queryParams.is_changed = is_changed;
  if (is_important !== undefined) queryParams.is_important = is_important;
  if (author_user_id) queryParams.author_user_id = author_user_id;
  if (today_only !== undefined) queryParams.today_only = today_only;
  const { data, error } = await searchNotes({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    query: queryParams,
  });

  if (error) {
    return { message: error };
  }

  return { data };
}
