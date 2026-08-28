"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch, clearTokens } from "@/lib/auth";
import Link from "next/link";

type CurrentUser = { full_name: string; email: string; role: string };
type Application = { id: string; business_name: string; status: string; created_at: string };

function DashboardContent() {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState("");
  const [applications, setApplications] = useState<Application[]>([]);

  useEffect(() => {
    apiFetch("/auth/me").then(async (response) => {
      if (!response.ok) {
        clearTokens();
        router.replace("/login");
        return;
      }
      setUser(await response.json());
      const applicationsResponse = await apiFetch("/applications/me");
      if (applicationsResponse.ok) setApplications(await applicationsResponse.json());
    }).catch(() => setError("Could not contact the BizReg API. Is it running?"));
  }, [router]);

  function signOut() {
    clearTokens();
    router.push("/login");
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <div className="flex items-center justify-between gap-4"><div><p className="font-semibold text-blue-700">BizReg</p><h1 className="mt-2 text-3xl font-bold">Your dashboard</h1></div><button className="rounded border px-4 py-2" onClick={signOut}>Sign out</button></div>
      {error && <p className="mt-8 text-red-700">{error}</p>}
      {!user && !error && <p className="mt-8 text-slate-600">Loading your account…</p>}
      {user && <section className="mt-8 rounded-lg border bg-white p-6 shadow-sm"><h2 className="text-xl font-semibold">Welcome, {user.full_name}</h2><p className="mt-2 text-slate-600">{user.email} · {user.role}</p><Link className="mt-6 inline-block rounded bg-blue-700 px-4 py-2 font-semibold text-white" href="/services">Start a business registration</Link><h3 className="mt-8 text-lg font-semibold">Your applications</h3>{applications.length === 0 ? <p className="mt-2 text-slate-600">You have not submitted an application yet.</p> : <ul className="mt-3 space-y-2">{applications.map((application) => <li className="rounded border p-3" key={application.id}><span className="font-medium">{application.business_name}</span><span className="ml-3 text-sm text-slate-600">{application.status.replace("_", " ")}</span></li>)}</ul>}</section>}
    </main>
  );
}

export default function DashboardPage() {
  return <ProtectedRoute><DashboardContent /></ProtectedRoute>;
}
