import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { usersCurrentUser } from "@/app/clientService";

/**
 * 服务端认证检查函数
 * 在服务端组件中使用，检查用户是否已登录
 * 如果未登录，自动重定向到登录页面
 */
export async function requireAuth(currentPath?: string) {
  const cookieStore = await cookies();
  const token = cookieStore.get("accessToken");

  if (!token) {
    const redirectPath = currentPath ? `?redirect=${encodeURIComponent(currentPath)}` : "";
    redirect(`/login${redirectPath}`);
  }

  const options = {
    headers: {
      Authorization: `Bearer ${token.value}`,
    },
  };

  const { error } = await usersCurrentUser(options);

  if (error) {
    const redirectPath = currentPath ? `?redirect=${encodeURIComponent(currentPath)}` : "";
    redirect(`/login${redirectPath}`);
  }

  return token.value;
}

/**
 * 客户端认证检查函数
 * 返回当前用户的认证状态
 */
export function getClientAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  const cookies = document.cookie.split(';');
  const accessTokenCookie = cookies.find(cookie => 
    cookie.trim().startsWith('accessToken=')
  );
  
  if (!accessTokenCookie) {
    return null;
  }

  return accessTokenCookie.split('=')[1];
} 