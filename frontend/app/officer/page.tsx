"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch, clearTokens } from "@/lib/auth";

/* ── types ──────────────────────────────────────────────────────────────── */
type User = { id: string; full_name: string; email: string; role: string };

type AppSummary = {
  id: string; service_code: string; service_name: string;
  citizen_email: string; status: string; business_name: string; created_at: string;
};

type AppDetail = AppSummary & {
  form_data: Record<string, unknown>;
  registration_number: string | null;
  rejection_reason: string | null;
};

type AuditEntry = {
  id: string; action: string; from_state: string | null;
  to_state: string | null; actor_id: string | null;
  details: Record<string, unknown>; created_at: string;
};

/* ── constants ──────────────────────────────────────────────────────────── */
const STATUS_META: Record<string, { label: string; color: string }> = {
  submitted:       { label: "Submitted",       color: "bg-slate-100 text-slate-600"   },
  under_review:    { label: "Under review",     color: "bg-blue-100 text-blue-700"    },
  payment_pending: { label: "Payment pending",  color: "bg-amber-100 text-amber-700"  },
  paid:            { label: "Paid",             color: "bg-cyan-100 text-cyan-700"    },
  officer_review:  { label: "Officer review",   color: "bg-purple-100 text-purple-700"},
  approved:        { label: "Approved",         color: "bg-emerald-100 text-emerald-700"},
  rejected:        { label: "Rejected",         color: "bg-red-100 text-red-700"      },
  completed:       { label: "Completed",        color: "bg-green-100 text-green-700"  },
};

const ALLOWED: Record<string, string[]> = {
  submitted:       ["under_review", "rejected"],
  under_review:    ["payment_pending", "rejected"],
  payment_pending: ["paid", "rejected"],
  paid:            ["officer_review", "rejected"],
  officer_review:  [],   // handled by approve/reject buttons
  approved:        ["completed"],
  rejected:        [],
  completed:       [],
};

function StatusBadge({ status }: { status: string }) {
  const m = STATUS_META[status] ?? { label: status, color: "bg-slate-100 text-slate-600" };
  return <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${m.color}`}>{m.label}</span>;
}

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString("en-RW", { day: "numeric", month: "short", year: "numeric" });
}

/* ── application detail panel ───────────────────────────────────────────── */
function DetailPanel({ app, audit, onTransition, onClose }: {
  app: AppDetail;
  audit: AuditEntry[];
  onTransition: (id: string, status: string, reason?: string) => Promise<void>;
  onClose: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [showReject, setShowReject] = useState(false);
  const [tab, setTab] = useState<"details" | "audit">("details");
  const ownerDetails = typeof app.form_data === "object" && app.form_data !== null && "owner" in app.form_data
    ? (app.form_data.owner as Record<string, string> | undefined)
    : undefined;
  const addressDetails = typeof app.form_data === "object" && app.form_data !== null && "address" in app.form_data
    ? (app.form_data.address as Record<string, string> | undefined)
    : undefined;

  const nextStates = ALLOWED[app.status] ?? [];
  const canReview = app.status === "officer_review";
  const isTerminal = app.status === "rejected" || app.status === "completed";

  async function transition(newStatus: string, reason?: string) {
    setBusy(true); setErr("");
    try { await onTransition(app.id, newStatus, reason); }
    catch (e) { setErr(e instanceof Error ? e.message : "Action failed"); }
    finally { setBusy(false); }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end bg-black/30">
      <div className="flex h-full w-full sm:max-w-xl flex-col bg-white shadow-2xl">
        {/* header */}
        <div className="flex items-start justify-between border-b px-6 py-5">
          <div>
            <h2 className="font-bold text-slate-900 text-lg">{app.business_name}</h2>
            <p className="text-sm text-slate-500">{app.citizen_email} · {fmt(app.created_at)}</p>
          </div>
          <button onClick={onClose} className="ml-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-100">
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>

        {/* status + tabs */}
        <div className="border-b px-6 py-3 flex items-center justify-between">
          <StatusBadge status={app.status} />
          <div className="flex gap-1">
            {(["details","audit"] as const).map(t => (
              <button key={t} onClick={() => setTab(t)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium ${tab === t ? "bg-blue-50 text-blue-700" : "text-slate-500 hover:bg-slate-50"}`}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* body */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
          {tab === "details" ? (
            <>
              {/* form data */}
              <section className="rounded-xl border bg-slate-50 p-4 text-sm space-y-2">
                <p className="font-semibold text-slate-700">Business information</p>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-slate-600">
                  <span className="text-slate-400">Service</span><span>{app.service_name}</span>
                  <span className="text-slate-400">Type</span>
                  <span className="capitalize">{String(app.form_data?.business_type ?? "—").replace(/_/g, " ")}</span>
                  {app.registration_number && (
                    <><span className="text-slate-400">Reg. no.</span><span className="font-mono font-medium text-emerald-700">{app.registration_number}</span></>
                  )}
                </div>
              </section>

              {ownerDetails && Object.keys(ownerDetails).length > 0 && (
                <section className="rounded-xl border bg-slate-50 p-4 text-sm space-y-2">
                  <p className="font-semibold text-slate-700">Owner details</p>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-slate-600">
                    {Object.entries(ownerDetails).map(([k,v]) => (
                      <><span key={k+"-k"} className="capitalize text-slate-400">{k.replace(/_/g," ")}</span><span key={k+"-v"}>{v}</span></>
                    ))}
                  </div>
                </section>
              )}

              {addressDetails && Object.keys(addressDetails).length > 0 && (
                <section className="rounded-xl border bg-slate-50 p-4 text-sm space-y-2">
                  <p className="font-semibold text-slate-700">Address</p>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-slate-600">
                    {Object.entries(addressDetails).map(([k,v]) => (
                      <><span key={k+"-k"} className="capitalize text-slate-400">{k.replace(/_/g," ")}</span><span key={k+"-v"}>{v}</span></>
                    ))}
                  </div>
                </section>
              )}

              {app.rejection_reason && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  <p className="font-semibold mb-1">Rejection reason</p>
                  {app.rejection_reason}
                </div>
              )}
            </>
          ) : (
            <div className="space-y-2">
              {audit.length === 0 && <p className="text-sm text-slate-400">No audit events yet.</p>}
              {audit.map(e => (
                <div key={e.id} className="rounded-xl border bg-slate-50 p-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-800">{e.action.replace(/_/g, " ")}</span>
                    <span className="text-xs text-slate-400">{fmt(e.created_at)}</span>
                  </div>
                  {(e.from_state || e.to_state) && (
                    <p className="mt-1 text-xs text-slate-500">
                      {e.from_state ?? "—"} → <span className="font-medium text-slate-700">{e.to_state}</span>
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* actions footer */}
        {!isTerminal && (
          <div className="border-t bg-white px-6 py-4 space-y-3">
            {err && <p className="text-sm text-red-600">{err}</p>}

            {/* next-state buttons */}
            {nextStates.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {nextStates.map(s => (
                  <button key={s} onClick={() => transition(s)} disabled={busy}
                    className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100 disabled:opacity-50">
                    {busy ? "…" : `→ ${STATUS_META[s]?.label ?? s}`}
                  </button>
                ))}
              </div>
            )}

            {/* approve / reject (officer_review only) */}
            {canReview && !showReject && (
              <div className="flex gap-2">
                <button onClick={() => transition("approved")} disabled={busy}
                  className="flex-1 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-50">
                  {busy ? "Processing…" : "Approve"}
                </button>
                <button onClick={() => setShowReject(true)} disabled={busy}
                  className="flex-1 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-500 disabled:opacity-50">
                  Reject
                </button>
              </div>
            )}
            {canReview && showReject && (
              <div className="space-y-2">
                <textarea value={rejectReason} onChange={e => setRejectReason(e.target.value)}
                  rows={3} placeholder="Rejection reason (required)"
                  className="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:border-red-400 focus:ring-2 focus:ring-red-400/20" />
                <div className="flex gap-2">
                  <button onClick={() => { if (rejectReason.trim()) transition("rejected", rejectReason.trim()); else setErr("Rejection reason is required"); }}
                    disabled={busy}
                    className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500 disabled:opacity-50">
                    Confirm rejection
                  </button>
                  <button onClick={() => { setShowReject(false); setRejectReason(""); }}
                    className="rounded-lg border px-4 py-2 text-sm text-slate-600 hover:bg-slate-50">
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── dashboard ──────────────────────────────────────────────────────────── */
function OfficerDashboard() {
  const router = useRouter();
  const [me, setMe] = useState<User | null>(null);
  const [apps, setApps] = useState<AppSummary[]>([]);
  const [detail, setDetail] = useState<AppDetail | null>(null);
  const [auditLog, setAuditLog] = useState<AuditEntry[]>([]);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const [uR, aR] = await Promise.all([
      apiFetch("/auth/me"),
      apiFetch("/officer/applications"),
    ]);
    if (!uR.ok) { clearTokens(); router.replace("/login"); return; }
    const u: User = await uR.json();
    if (u.role === "admin") { router.replace("/admin"); return; }
    if (u.role === "citizen") { router.replace("/dashboard"); return; }
    setMe(u);
    if (aR.ok) setApps(await aR.json());
    setLoading(false);
  }, [router]);

  useEffect(() => { load(); }, [load]);

  async function openDetail(app: AppSummary) {
    const [dR, aR] = await Promise.all([
      apiFetch(`/officer/applications/${app.id}`),
      apiFetch(`/officer/applications/${app.id}/audit`),
    ]);
    if (dR.ok) setDetail(await dR.json());
    if (aR.ok) setAuditLog(await aR.json());
  }

  async function handleTransition(id: string, newStatus: string, reason?: string) {
    let r: Response;
    if (newStatus === "approved" || newStatus === "rejected") {
      r = await apiFetch(`/officer/applications/${id}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision: newStatus, rejection_reason: reason ?? null }),
      });
    } else {
      r = await apiFetch(`/officer/applications/${id}/transition`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_status: newStatus }),
      });
    }
    if (!r.ok) { const d = await r.json(); throw new Error(d.detail ?? "Action failed"); }
    const updated: AppDetail = await r.json();
    setApps(prev => prev.map(a => a.id === id ? { ...a, status: updated.status, registration_number: updated.registration_number } as AppSummary : a));
    setDetail(updated);
    // refresh audit
    const aR = await apiFetch(`/officer/applications/${id}/audit`);
    if (aR.ok) setAuditLog(await aR.json());
  }

  const filtered = apps.filter(a => {
    const matchStatus = filter === "all" || a.status === filter;
    const matchSearch = a.business_name.toLowerCase().includes(search.toLowerCase()) ||
                        a.citizen_email.toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  const counts: Record<string, number> = {};
  apps.forEach(a => { counts[a.status] = (counts[a.status] ?? 0) + 1; });

  const statCards = [
    { label: "Total",           value: apps.length,                  color: "border-slate-200 bg-slate-50" },
    { label: "Awaiting review", value: (counts.submitted ?? 0) + (counts.under_review ?? 0), color: "border-blue-200 bg-blue-50"   },
    { label: "Payment pending", value: counts.payment_pending ?? 0,  color: "border-amber-200 bg-amber-50" },
    { label: "Officer review",  value: counts.officer_review ?? 0,   color: "border-purple-200 bg-purple-50" },
    { label: "Approved",        value: (counts.approved ?? 0) + (counts.completed ?? 0), color: "border-emerald-200 bg-emerald-50" },
    { label: "Rejected",        value: counts.rejected ?? 0,         color: "border-red-200 bg-red-50"     },
  ];

  if (loading) return (
    <main className="flex min-h-[60vh] items-center justify-center">
      <svg className="h-8 w-8 animate-spin text-blue-500" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
    </main>
  );

  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      {/* header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">Officer portal</p>
          <h1 className="text-2xl font-bold text-slate-900">Application Queue</h1>
          <p className="text-sm text-slate-500">{me?.full_name} · {me?.email}</p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700">
          <span className="h-2 w-2 rounded-full bg-blue-500"></span>Officer
        </span>
      </div>

      {/* stat cards */}
      <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {statCards.map(s => (
          <div key={s.label} className={`rounded-xl border p-4 ${s.color}`}>
            <p className="text-2xl font-bold text-slate-900">{s.value}</p>
            <p className="mt-0.5 text-xs text-slate-500">{s.label}</p>
          </div>
        ))}
      </div>

      {/* filter + search */}
      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Search by business name or email…"
          className="flex-1 rounded-lg border px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
        />
        <select value={filter} onChange={e => setFilter(e.target.value)}
          className="rounded-lg border px-3.5 py-2.5 text-sm outline-none focus:border-blue-500">
          <option value="all">All statuses</option>
          {Object.keys(STATUS_META).map(s => (
            <option key={s} value={s}>{STATUS_META[s].label}</option>
          ))}
        </select>
      </div>

      {/* table */}
      <div className="mt-4 overflow-hidden rounded-xl border bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
              <th className="px-4 py-3">Business</th>
              <th className="px-4 py-3 hidden sm:table-cell">Citizen</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 hidden md:table-cell">Submitted</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filtered.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-10 text-center text-slate-400">No applications match your filter.</td></tr>
            )}
            {filtered.map(a => (
              <tr key={a.id} className="hover:bg-slate-50 cursor-pointer" onClick={() => openDetail(a)}>
                <td className="px-4 py-3 font-medium text-slate-900">{a.business_name}</td>
                <td className="px-4 py-3 text-slate-500 hidden sm:table-cell">{a.citizen_email}</td>
                <td className="px-4 py-3"><StatusBadge status={a.status} /></td>
                <td className="px-4 py-3 text-slate-500 hidden md:table-cell">{fmt(a.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  <button className="rounded-lg border px-3 py-1 text-xs text-blue-600 hover:bg-blue-50">Review</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {detail && (
        <DetailPanel
          app={detail} audit={auditLog}
          onTransition={handleTransition}
          onClose={() => { setDetail(null); setAuditLog([]); }}
        />
      )}
    </main>
  );
}

export default function OfficerPage() {
  return <ProtectedRoute><OfficerDashboard /></ProtectedRoute>;
}
