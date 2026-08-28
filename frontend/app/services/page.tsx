"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/auth";

type Service = { code: string; name: string; description: string };

function ServiceCatalogue() {
  const [services, setServices] = useState<Service[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/services").then(async (response) => {
      if (!response.ok) throw new Error("Could not load services");
      setServices(await response.json());
    }).catch(() => setError("Could not load the service catalogue. Is the API running?"));
  }, []);

  return <main className="mx-auto max-w-4xl px-6 py-16"><Link className="text-sm font-semibold text-blue-700" href="/dashboard">← Dashboard</Link><h1 className="mt-6 text-3xl font-bold">Available services</h1>{error && <p className="mt-6 text-red-700">{error}</p>}<div className="mt-8 grid gap-4">{services.map((service) => <article className="rounded-lg border bg-white p-6 shadow-sm" key={service.code}><h2 className="text-xl font-semibold">{service.name}</h2><p className="mt-2 text-slate-600">{service.description}</p><Link className="mt-5 inline-block rounded bg-blue-700 px-4 py-2 font-semibold text-white" href={`/services/${service.code}`}>Apply now</Link></article>)}</div></main>;
}

export default function ServicesPage() { return <ProtectedRoute><ServiceCatalogue /></ProtectedRoute>; }
