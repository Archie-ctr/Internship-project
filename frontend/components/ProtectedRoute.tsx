"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/auth";

/**
 * Client-side navigation guard.
 *
 * The key constraint: localStorage is only available in the browser.
 * During server-side rendering (and the first client render before
 * hydration completes) we must NOT read localStorage, otherwise React
 * sees different HTML from the server vs. the client and throws a
 * hydration error.
 *
 * Fix: defer the auth check until after mount (useEffect) and render a
 * neutral placeholder on both server and client until that point.
 * This guarantees server HTML === initial client HTML === spinner, so
 * hydration never mismatches.
 */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const router = useRouter();
  // null  = not yet checked (pre-mount, safe on server)
  // false = checked, no token → redirect
  // true  = checked, token present → render children
  const [authState, setAuthState] = useState<boolean | null>(null);

  useEffect(() => {
    // This only ever runs in the browser, after hydration completes.
    if (!getAccessToken()) {
      router.replace("/login");
      setAuthState(false);
    } else {
      setAuthState(true);
    }
  }, [router]);

  // Pre-mount and during redirect: render a neutral, server-safe placeholder.
  // Both server and client agree on this output, so no hydration mismatch.
  if (authState !== true) {
    return (
      <main className="flex min-h-[60vh] items-center justify-center">
        <svg
          className="h-8 w-8 animate-spin text-blue-500"
          viewBox="0 0 24 24"
          fill="none"
          aria-label="Checking session"
        >
          <circle
            className="opacity-25"
            cx="12" cy="12" r="10"
            stroke="currentColor" strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v8z"
          />
        </svg>
      </main>
    );
  }

  return <>{children}</>;
}
