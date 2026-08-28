/**
 * This is deliberately a small landing page in Phase 1. Feature pages will be
 * introduced beside it phase-by-phase, making the App Router structure easy to study.
 */
export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col justify-center px-6 py-16">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-700">BizReg</p>
      <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
        Business registration, made understandable.
      </h1>
      <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
        A learning project for a secure digital public-service workflow. Authentication,
        applications, reviews, payments, and certificates will be added one phase at a time.
      </p>
      <p className="mt-10 rounded-lg border border-blue-100 bg-white p-5 text-slate-700 shadow-sm">
        Create an account to try Phase 3 authentication. Business registration features arrive in the next phase.
      </p>
      <div className="mt-6 flex gap-3">
        <Link className="rounded bg-blue-700 px-5 py-3 font-semibold text-white" href="/register">Create account</Link>
        <Link className="rounded border border-slate-300 bg-white px-5 py-3 font-semibold text-slate-800" href="/login">Sign in</Link>
      </div>
    </main>
  );
}
import Link from "next/link";
