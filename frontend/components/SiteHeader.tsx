"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { clearTokens, getAccessToken, apiFetch } from "@/lib/auth";

type Me = { role: string; full_name: string };

export function SiteHeader() {
  const [me, setMe]           = useState<Me | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef               = useRef<HTMLDivElement>(null);
  const router                = useRouter();

  useEffect(() => {
    async function checkAuth() {
      const token = getAccessToken();
      if (!token) { setMe(null); return; }
      try {
        const r = await apiFetch("/auth/me");
        if (r.ok) setMe(await r.json());
        else setMe(null);
      } catch { setMe(null); }
    }
    checkAuth();
    window.addEventListener("storage", checkAuth);
    return () => window.removeEventListener("storage", checkAuth);
  }, []);

  // Close mobile menu when clicking outside
  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [menuOpen]);

  function handleSignOut() {
    clearTokens();
    setMe(null);
    setMenuOpen(false);
    router.push("/login");
  }

  const roleColor =
    me?.role === "admin"   ? "bg-purple-500" :
    me?.role === "officer" ? "bg-blue-500"   : "bg-emerald-500";

  const dashboardHref =
    me?.role === "officer" ? "/officer" :
    me?.role === "admin"   ? "/admin"   : "/dashboard";

  /* ── shared link list used in both desktop bar and mobile drawer ── */
  function NavLinks({ mobile = false }: { mobile?: boolean }) {
    const cls = mobile
      ? "flex flex-col divide-y divide-slate-100"
      : "hidden md:flex items-center gap-1 text-sm font-medium";

    const linkCls = mobile
      ? "flex items-center gap-2 px-5 py-3.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
      : "rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900";

    return (
      <div className={cls}>
        <Link href="/services" className={linkCls} onClick={() => setMenuOpen(false)}>
          Services
        </Link>

        {me ? (
          <>
            {me.role === "citizen" && (
              <Link href="/dashboard" className={mobile ? linkCls : "rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-100"} onClick={() => setMenuOpen(false)}>
                My applications
              </Link>
            )}
            {me.role === "officer" && (
              <Link href="/officer" className={mobile ? linkCls : "rounded-lg px-3 py-2 text-blue-700 hover:bg-blue-50"} onClick={() => setMenuOpen(false)}>
                Queue
              </Link>
            )}
            {me.role === "admin" && (
              <Link href="/admin" className={mobile ? linkCls : "rounded-lg px-3 py-2 text-purple-700 hover:bg-purple-50"} onClick={() => setMenuOpen(false)}>
                Platform
              </Link>
            )}

            {!mobile && (
              <div className="flex items-center gap-2 ml-2 rounded-full border border-slate-200 bg-slate-50 pl-1 pr-3 py-1">
                <span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold text-white ${roleColor}`}>
                  {me.full_name.charAt(0)}
                </span>
                <span className="text-xs text-slate-600 max-w-[90px] truncate">{me.full_name.split(" ")[0]}</span>
              </div>
            )}

            {mobile && (
              <div className="flex items-center gap-3 px-5 py-3.5">
                <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold text-white ${roleColor}`}>
                  {me.full_name.charAt(0)}
                </span>
                <div>
                  <p className="text-sm font-medium text-slate-900">{me.full_name}</p>
                  <p className="text-xs text-slate-500 capitalize">{me.role}</p>
                </div>
              </div>
            )}

            <button
              onClick={handleSignOut}
              className={mobile
                ? "flex w-full items-center gap-2 px-5 py-3.5 text-sm font-medium text-red-600 hover:bg-red-50"
                : "ml-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-500 hover:border-slate-300 hover:text-slate-700"
              }
            >
              {mobile && (
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              )}
              Sign out
            </button>
          </>
        ) : (
          <>
            <Link href="/login" className={mobile ? linkCls : "rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-100"} onClick={() => setMenuOpen(false)}>
              Sign in
            </Link>
            <Link
              href="/register"
              className={mobile
                ? "mx-5 my-3 flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500"
                : "ml-1 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-500"
              }
              onClick={() => setMenuOpen(false)}
            >
              Create account
            </Link>
          </>
        )}
      </div>
    );
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <nav aria-label="Primary navigation" className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">

        {/* Logo */}
        <Link className="text-lg font-bold tracking-tight text-slate-900" href="/">
          BizReg
        </Link>

        {/* Desktop nav */}
        <NavLinks />

        {/* Mobile: hamburger */}
        <button
          className="flex items-center justify-center rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen(v => !v)}
        >
          {menuOpen ? (
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6 6 18M6 6l12 12"/></svg>
          ) : (
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          )}
        </button>
      </nav>

      {/* Mobile drawer */}
      {menuOpen && (
        <div ref={menuRef} className="border-t border-slate-100 bg-white pb-2 md:hidden">
          <NavLinks mobile />
        </div>
      )}
    </header>
  );
}
