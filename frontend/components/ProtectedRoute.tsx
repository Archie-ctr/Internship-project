"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";

import { getAccessToken } from "@/lib/auth";

/**
 * Client-side navigation guard for usability. It is not an authorisation
 * boundary: the FastAPI endpoint always verifies the JWT and user role too.
 */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    if (!getAccessToken()) router.replace("/login");
  }, [router]);

  if (!getAccessToken()) return <p className="p-8 text-slate-600">Checking your session…</p>;
  return <>{children}</>;
}
