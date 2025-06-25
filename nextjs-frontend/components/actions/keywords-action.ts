"use server";

import { cookies } from "next/headers";
import { getKeywords, deleteKeyword, createKeyword, updateKeyword, toggleKeywordStatus } from "@/app/clientService";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { keywordSchema } from "@/lib/definitions";

export async function fetchKeywords(
  skip: number = 0,
  limit: number = 100,
  category?: string,
  active_only: boolean = true,
  search?: string
) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { data, error } = await getKeywords({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    query: {
      skip,
      limit,
      category,
      active_only,
      search,
    },
  });

  if (error) {
    return { message: error };
  }

  return data;
}

export async function removeKeyword(id: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { error } = await deleteKeyword({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    path: {
      keyword_id: id,
    },
  });

  if (error) {
    return { message: error };
  }
  revalidatePath("/keywords");
}

export async function addKeyword(prevState: {}, formData: FormData) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const validatedFields = keywordSchema.safeParse({
    keyword: formData.get("keyword"),
    category: formData.get("category"),
    weight: formData.get("weight"),
    is_active: formData.get("is_active") === "true",
    description: formData.get("description"),
  });

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors };
  }

  const { keyword, category, weight, is_active, description } = validatedFields.data;

  const input = {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: {
      keyword,
      category,
      weight,
      is_active,
      description,
    },
  };
  const { error } = await createKeyword(input);
  if (error) {
    return { message: `${error.detail}` };
  }
  redirect(`/keywords`);
}

export async function editKeyword(id: string, prevState: {}, formData: FormData) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const validatedFields = keywordSchema.safeParse({
    keyword: formData.get("keyword"),
    category: formData.get("category"),
    weight: formData.get("weight"),
    is_active: formData.get("is_active") === "true",
    description: formData.get("description"),
  });

  if (!validatedFields.success) {
    return { errors: validatedFields.error.flatten().fieldErrors };
  }

  const { keyword, category, weight, is_active, description } = validatedFields.data;

  const input = {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    path: {
      keyword_id: id,
    },
    body: {
      keyword,
      category,
      weight,
      is_active,
      description,
    },
  };
  const { error } = await updateKeyword(input);
  if (error) {
    return { message: `${error.detail}` };
  }
  revalidatePath("/keywords");
  redirect(`/keywords`);
}

export async function toggleKeyword(id: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken")?.value;

  if (!token) {
    return { message: "No access token found" };
  }

  const { error } = await toggleKeywordStatus({
    headers: {
      Authorization: `Bearer ${token}`,
    },
    path: {
      keyword_id: id,
    },
  });

  if (error) {
    return { message: error };
  }
  revalidatePath("/keywords");
} 