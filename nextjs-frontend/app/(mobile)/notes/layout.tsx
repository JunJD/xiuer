import AuthGuard from "@/components/auth-guard";

export default function NotesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">正在验证登录状态...</p>
            <p className="text-gray-500 text-sm mt-2">请稍候</p>
          </div>
        </div>
      }
    >
      {children}
    </AuthGuard>
  );
} 