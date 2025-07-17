"use client";

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { usersCurrentUser } from '@/app/clientService';

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function AuthGuard({ children, fallback }: AuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // 获取token from cookies
        const cookies = document.cookie.split(';');
        const accessTokenCookie = cookies.find(cookie => 
          cookie.trim().startsWith('accessToken=')
        );
        
        if (!accessTokenCookie) {
          // 没有token，重定向到登录页
          const redirectUrl = encodeURIComponent(pathname);
          router.push(`/login?redirect=${redirectUrl}`);
          return;
        }

        const token = accessTokenCookie.split('=')[1];
        
        // 验证token有效性
        const { error } = await usersCurrentUser({
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (error) {
          // Token无效，重定向到登录页
          const redirectUrl = encodeURIComponent(pathname);
          router.push(`/login?redirect=${redirectUrl}`);
          return;
        }

        // 认证成功
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Auth check failed:', error);
        // 出错时重定向到登录页
        const redirectUrl = encodeURIComponent(pathname);
        router.push(`/login?redirect=${redirectUrl}`);
      }
    };

    checkAuth();
  }, [router, pathname]);

  // 正在检查认证状态时显示加载状态
  if (isAuthenticated === null) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">验证登录状态中...</p>
        </div>
      </div>
    );
  }

  // 已认证，显示子组件
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // 认证失败时不渲染任何内容（因为会重定向）
  return null;
} 