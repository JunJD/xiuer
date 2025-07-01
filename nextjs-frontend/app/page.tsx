"use client"

import XiuerHero from "@/components/hero";
import { useRouter } from "next/navigation";
export default function Home() {
  const router = useRouter()
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
      <XiuerHero ToDashboard={() => {
        router.push("/dashboard")
      }} />
    </main>
  );
}
