import Link from "next/link";

/**
 * A deliberately small shared shell. Authentication remains enforced by the
 * API; links here are navigation, not a security control.
 */
export function SiteHeader() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <nav aria-label="Primary navigation" className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link className="text-lg font-bold tracking-tight text-slate-900" href="/">BizReg</Link>
        <div className="flex items-center gap-4 text-sm font-medium">
          <Link className="text-slate-700 hover:text-blue-700" href="/services">Services</Link>
          <Link className="text-slate-700 hover:text-blue-700" href="/login">Sign in</Link>
          <Link className="rounded bg-blue-700 px-3 py-2 text-white hover:bg-blue-800" href="/register">Create account</Link>
        </div>
      </nav>
    </header>
  );
}
