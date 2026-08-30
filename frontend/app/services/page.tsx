"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/auth";

type Service = { code: string; name: string; description: string };

const SERVICE_ICONS: Record<string, string> = {
  "business-registration": "🏢",
};

function ServiceCatalogue() {
  const [services, setServices] = useState<Service[]>([]);
  const [error, setError]       = useState("");

  useEffect(() => {
    apiFetch("/services")
      .then(async r => { if (!r.ok) throw new Error(); setServices(await r.json()); })
      .catch(() => setError("Could not load services. Is the API running?"));
  }, []);

  return (
    <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <Link className="inline-flex items-center gap-1 text-sm font-semibold text-blue-700 hover:text-blue-600" href="/dashboard">
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><polyline points="15 18 9 12 15 6"/></svg>
        Dashboard
      </Link>

      <div className="mt-6">
        <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">Available services</h1>
        <p className="mt-1 text-sm text-slate-500">Choose a service to begin your application.</p>
      </div>

      {error && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {services.map(s => (
          <article key={s.code} className="flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-blue-200 hover:shadow-md">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{SERVICE_ICONS[s.code] ?? "📋"}</span>
              <h2 className="text-lg font-semibold text-slate-900">{s.name}</h2>
            </div>
            <p className="mt-3 flex-1 text-sm leading-relaxed text-slate-500">{s.description}</p>
            <Link
              href={`/services/${s.code}`}
              className="mt-5 flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500"
            >
              Apply now
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </Link>
          </article>
        ))}

        {services.length === 0 && !error && (
          <div className="col-span-2 rounded-2xl border border-dashed border-slate-200 p-12 text-center text-slate-400">
            Loading services…
          </div>
        )}
      </div>
    </main>
  );
}

export default function ServicesPage() {
  return <ProtectedRoute><ServiceCatalogue /></ProtectedRoute>;
}
