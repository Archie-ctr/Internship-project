"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch, clearTokens } from "@/lib/auth";

/* ── types ──────────────────────────────────────────────────────────────── */
type User = { id: string; full_name: string; email: string; role: string };
type Application = {
  id: string; service_code: string; service_name: string;
  status: string; business_name: string; created_at: string;
  form_data?: Record<string, unknown>; rejection_reason?: string | null;
};
type Notification = {
  id: string; subject: string; body: string;
  delivery_status: string; created_at: string; channel: string;
};

/* ── helpers ────────────────────────────────────────────────────────────── */
const STATUS_META: Record<string, { label: string; color: string }> = {
  submitted:       { label: "Submitted",        color: "bg-slate-100 text-slate-600" },
  under_review:    { label: "Under review",      color: "bg-blue-100 text-blue-700" },
  payment_pending: { label: "Payment pending",   color: "bg-amber-100 text-amber-700" },
  paid:            { label: "Paid",              color: "bg-cyan-100 text-cyan-700" },
  officer_review:  { label: "Officer review",    color: "bg-purple-100 text-purple-700" },
  approved:        { label: "Approved",          color: "bg-emerald-100 text-emerald-700" },
  rejected:        { label: "Rejected",          color: "bg-red-100 text-red-700" },
  completed:       { label: "Completed",         color: "bg-green-100 text-green-700" },
};

function StatusBadge({ status }: { status: string }) {
  const m = STATUS_META[status] ?? { label: status, color: "bg-slate-100 text-slate-600" };
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${m.color}`}>
      {m.label}
    </span>
  );
}

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString("en-RW", { day: "numeric", month: "short", year: "numeric" });
}

/* ── detail modal ───────────────────────────────────────────────────────── */
function AppModal({ app, onClose, onPay }: {
  app: Application; onClose: () => void; onPay: (id: string) => void;
}) {
  const [paying, setPaying] = useState(false);
  const [payError, setPayError] = useState("");
  const ownerDetails = typeof app.form_data === "object" && app.form_data !== null && "owner" in app.form_data
    ? (app.form_data.owner as Record<string, string> | undefined)
    : undefined;
  const addressDetails = typeof app.form_data === "object" && app.form_data !== null && "address" in app.form_data
    ? (app.form_data.address as Record<string, string> | undefined)
    : undefined;

  async function handlePay() {
    setPaying(true); setPayError("");
    try {
      const r = await apiFetch(`/applications/${app.id}/payment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: "mock" }),
      });
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail); }
      onPay(app.id);
      onClose();
    } catch (e) {
      setPayError(e instanceof Error ? e.message : "Payment failed");
    } finally { setPaying(false); }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center sm:p-4">
      <div className="w-full max-w-lg rounded-t-2xl bg-white shadow-xl sm:rounded-2xl max-h-[90vh] flex flex-col">
        <div className="flex items-start justify-between border-b px-6 py-4">
          <div>
            <h2 className="font-bold text-slate-900">{app.business_name}</h2>
            <p className="text-sm text-slate-500">{app.service_name} · {fmt(app.created_at)}</p>
          </div>
          <button onClick={onClose} className="ml-4 rounded-lg p-1 text-slate-400 hover:bg-slate-100">
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div className="overflow-y-auto px-6 py-4 space-y-3">
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-500">Status</span>
            <StatusBadge status={app.status} />
          </div>
          {app.rejection_reason && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <strong>Rejection reason:</strong> {app.rejection_reason}
            </div>
          )}
          {app.form_data && (
            <div className="rounded-lg border bg-slate-50 p-4 text-sm space-y-1">
              <p className="font-medium text-slate-700 mb-2">Application details</p>
              <p><span className="text-slate-500">Business type: </span>{String((app.form_data as Record<string, unknown>).business_type ?? "—").replace(/_/g, " ")}</p>
              {ownerDetails && "full_name" in ownerDetails && ownerDetails.full_name && (
                <p><span className="text-slate-500">Owner: </span>{ownerDetails.full_name}</p>
              )}
              {addressDetails && "city" in addressDetails && "district" in addressDetails && (
                <p><span className="text-slate-500">Address: </span>
                  {String(addressDetails.city)}, {String(addressDetails.district)}
                </p>
              )}
            </div>
          )}
          {app.status === "payment_pending" && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
              <p className="font-medium text-amber-800">Registration fee due</p>
              <p className="mt-1 text-2xl font-bold text-amber-900">RWF 50,000</p>
              <p className="mt-1 text-xs text-amber-700">Simulated sandbox payment — no real charge</p>
              {payError && <p className="mt-2 text-sm text-red-600">{payError}</p>}
              <button
                onClick={handlePay} disabled={paying}
                className="mt-3 rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-500 disabled:opacity-50"
              >
                {paying ? "Processing…" : "Pay registration fee"}
              </button>
            </div>
          )}
        </div>
        <div className="border-t px-6 py-3 flex justify-end">
          <button onClick={onClose} className="rounded-lg border px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">Close</button>
        </div>
      </div>
    </div>
  );
}

/* ── main content ───────────────────────────────────────────────────────── */
function CitizenDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [apps, setApps] = useState<Application[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [selected, setSelected] = useState<Application | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      apiFetch("/auth/me"),
      apiFetch("/applications/me"),
      apiFetch("/notifications/me"),
    ]).then(async ([uR, aR, nR]) => {
      if (!uR.ok) { clearTokens(); router.replace("/login"); return; }
      const u: User = await uR.json();
      // Redirect non-citizens to their own dashboard
      if (u.role === "officer") { router.replace("/officer"); return; }
      if (u.role === "admin")   { router.replace("/admin");   return; }
      setUser(u);
      if (aR.ok) setApps(await aR.json());
      if (nR.ok) setNotifications(await nR.json());
    }).catch(() => setError("Could not reach the API."))
      .finally(() => setLoading(false));
  }, [router]);

  // Load detail when modal opens
  async function openDetail(app: Application) {
    const r = await apiFetch(`/applications/${app.id}`);
    if (r.ok) setSelected(await r.json());
    else setSelected(app);
  }

  function handlePaid(id: string) {
    setApps(prev => prev.map(a => a.id === id ? { ...a, status: "paid" } : a));
  }

  const stats = [
    { label: "Total",    value: apps.length,                                   color: "bg-slate-50  border-slate-200" },
    { label: "Active",   value: apps.filter(a => !["approved","rejected","completed"].includes(a.status)).length, color: "bg-blue-50   border-blue-200" },
    { label: "Approved", value: apps.filter(a => a.status === "approved" || a.status === "completed").length,    color: "bg-emerald-50 border-emerald-200" },
    { label: "Rejected", value: apps.filter(a => a.status === "rejected").length,                               color: "bg-red-50    border-red-200" },
  ];

  if (loading) return (
    <main className="flex min-h-[60vh] items-center justify-center">
      <div className="flex flex-col items-center gap-3 text-slate-500">
        <svg className="h-8 w-8 animate-spin text-blue-500" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
        Loading…
      </div>
    </main>
  );

  if (error) return <main className="p-8 text-red-600">{error}</main>;

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      {/* header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">Citizen portal</p>
          <h1 className="text-2xl font-bold text-slate-900">
            Welcome back, {user?.full_name.split(" ")[0]}
          </h1>
          <p className="text-sm text-slate-500">{user?.email}</p>
        </div>
        <Link
          href="/services"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-500"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New application
        </Link>
      </div>

      {/* stats */}
      <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {stats.map(s => (
          <div key={s.label} className={`rounded-xl border p-4 ${s.color}`}>
            <p className="text-2xl font-bold text-slate-900">{s.value}</p>
            <p className="mt-0.5 text-sm text-slate-500">{s.label} applications</p>
          </div>
        ))}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        {/* applications table */}
        <div className="lg:col-span-2">
          <h2 className="mb-3 font-semibold text-slate-800">My applications</h2>
          {apps.length === 0 ? (
            <div className="rounded-xl border border-dashed bg-white p-10 text-center text-slate-400">
              No applications yet.{" "}
              <Link href="/services" className="text-blue-600 underline">Start one now</Link>
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                    <th className="px-4 py-3">Business</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 hidden sm:table-cell">Date</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {apps.map(a => (
                    <tr key={a.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-900 max-w-[140px] truncate">{a.business_name}</td>
                      <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                      <td className="px-4 py-3 text-slate-500 hidden sm:table-cell">{fmt(a.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => openDetail(a)}
                          className="rounded-lg border px-3 py-1 text-xs text-slate-600 hover:bg-slate-100"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* notifications */}
        <div>
          <h2 className="mb-3 font-semibold text-slate-800">Notifications</h2>
          {notifications.length === 0 ? (
            <div className="rounded-xl border border-dashed bg-white p-6 text-center text-sm text-slate-400">No notifications</div>
          ) : (
            <div className="space-y-2">
              {notifications.slice(0, 6).map(n => (
                <div key={n.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <p className="text-sm font-medium text-slate-800">{n.subject}</p>
                  <p className="mt-1 text-xs text-slate-500 line-clamp-2">{n.body}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${n.delivery_status === "delivered" ? "bg-emerald-50 text-emerald-600" : "bg-slate-100 text-slate-500"}`}>
                      {n.delivery_status}
                    </span>
                    <span className="text-xs text-slate-400">{fmt(n.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selected && (
        <AppModal app={selected} onClose={() => setSelected(null)} onPay={handlePaid} />
      )}
    </main>
  );
}

export default function DashboardPage() {
  return <ProtectedRoute><CitizenDashboard /></ProtectedRoute>;
}
