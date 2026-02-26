"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/login");
  }, [router]);

  return (
    <div className="flex bg-gray-50 dark:bg-zinc-950 min-h-screen items-center justify-center">
       <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
    </div>
  );
}
