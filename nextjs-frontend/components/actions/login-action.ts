"use server";

import { cookies } from "next/headers";

import { authJwtLogin } from "@/app/clientService";
import { redirect } from "next/navigation";
import { loginSchema } from "@/lib/definitions";
import { getErrorMessage } from "@/lib/utils";

export async function login(prevState: unknown, formData: FormData) {
  const validatedFields = loginSchema.safeParse({
    username: formData.get("username") as string,
    password: formData.get("password") as string,
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    };
  }

  const { username, password } = validatedFields.data;
  
  // 获取重定向URL
  const redirectUrl = formData.get("redirect") as string;

  const input = {
    body: {
      username,
      password,
    },
  };

  try {
    const { data, error } = await authJwtLogin(input);
    if (error) {
      return { server_validation_error: getErrorMessage(error) };
    }
    (await cookies()).set("accessToken", data.access_token);
  } catch (err) {
    console.error("Login error:", err);
    return {
      server_error: "An unexpected error occurred. Please try again later.",
    };
  }
  
  // 如果有重定向URL，则重定向到该URL，否则重定向到dashboard
  const targetUrl = redirectUrl ? decodeURIComponent(redirectUrl) : "/dashboard";
  redirect(targetUrl);
}
