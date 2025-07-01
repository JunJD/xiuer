"use server";

import { cookies } from "next/headers";
import { getNotesStats, searchNotes, getNoteDetail } from "@/app/clientService";
import { noteQuerySchema } from "@/lib/definitions";

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

export async function fetchNotes(
  keyword?: string,
  is_new?: boolean,
  is_changed?: boolean,
  is_important?: boolean,
  author_user_id?: string,
  limit: number = 500,
  offset: number = 0,
) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const queryParams: Record<string, unknown> = {
    limit,
    offset,
  };

  if (keyword) queryParams.keyword = keyword;
  if (is_new !== undefined) queryParams.is_new = is_new;
  if (is_changed !== undefined) queryParams.is_changed = is_changed;
  if (is_important !== undefined) queryParams.is_important = is_important;
  if (author_user_id) queryParams.author_user_id = author_user_id;

  const { data, error } = await searchNotes({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    query: queryParams,
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
