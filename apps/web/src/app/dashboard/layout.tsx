"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Sidebar } from "@/components/dashboard/sidebar";
import { useAuth } from "@/lib/auth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [loading, isAuthenticated, router]);

  if (loading) return null;
  if (!isAuthenticated) return null;

  return (
    <>
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </>
  );
}
