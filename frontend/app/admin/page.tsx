"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch, clearTokens } from "@/lib/auth";

/* ── types ──────────────────────────────────────────────────────────────── */
type User = { id: string; full_name: string; email: string; role: string; is_active: boolean };

type AppSummary = {
  id: string; service_name: string; citizen_email: string;
  status: string; business_name: string; created_at: string;
  registration_number?: string | null;
};

type AppDetail = AppSummary & {
  form_data: Record<string, unknown>;
  rejection_reason: string | null;
};

type AuditEntry = {
  id: string; action: string; from_state: string | null;
  to_state: string | null; details: Record<string, unknown>; created_at: string;
};

type Notification = {
  id: string; subject: string; recipient: string;
  delivery_status: string; channel: string; created_at: string;
};

/* ── helpers ────────────────────────────────────────────────────────────── */
const STATUS_META: Record<string, { label: string; color: string }> = {
  submitted:       { label: "Submitted",       color: "bg-slate-100 text-slate-600"    },
  under_review:    { label: "Under review",     color: "bg-blue-100 text-blue-700"     },
  payment_pending: { label: "Payment pending",  color: "bg-amber-100 text-amber-700"   },
  paid:            { label: "Paid",             color: "bg-cyan-100 text-cyan-700"     },
  officer_review:  { label: "Officer review",   color: "bg-purple-100 text-purple-700" },
  approved:        { label: "Approved",         color: "bg-emerald-100 text-emerald-700"},
  rejected:        { label: "Rejected",         color: "bg-red-100 text-red-700"       },
  completed:       { label: "Completed",        color: "bg-green-100 text-green-700"   },
};

const ROLE_COLOR: Record<string, string> = {
  citizen: "bg-slate-100 text-slate-700",
  officer: "bg-blue-100 text-blue-700",
  admin:   "bg-purple-100 text-purple-700",
};

function Badge({ label, color }: { label: string; color: string }) {
  return <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${color}`}>{label}</span>;
}

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString("en-RW", { day: "numeric", month: "short", year: "numeric" });
}

/* ── detail slide-over ───────────────────────────────────────────────────── */
function AppDetailPanel({ app, audit, onClose }: {
  app: AppDetail; audit: AuditEntry[]; onClose: () => void;
}) {
  const ownerDetails = typeof app.form_data === "object" && app.form_data !== null && "owner" in app.form_data
    ? (app.form_data.owner as Record<string, string> | undefined)
    : undefined;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end bg-black/30">
      <div className="flex h-full w-full sm:max-w-lg flex-col bg-white shadow-2xl">
        <div className="flex items-start justify-between border-b px-6 py-5">
          <div>
            <h2 className="font-bold text-slate-900 text-lg">{app.business_name}</h2>
            <p className="text-sm text-slate-500">{app.citizen_email} · {fmt(app.created_at)}</p>
          </div>
          <button onClick={onClose} className="ml-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-100">
            <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-4">
          <div className="flex items-center gap-3">
            <Badge label={STATUS_META[app.status]?.label ?? app.status} color={STATUS_META[app.status]?.color ?? "bg-slate-100 text-slate-600"} />
            {app.registration_number && (
              <span className="font-mono text-sm font-medium text-emerald-700">{app.registration_number}</span>
            )}
          </div>
          {ownerDetails && Object.keys(ownerDetails).length > 0 && (
            <section className="rounded-xl border bg-slate-50 p-4 text-sm">
              <p className="font-semibold text-slate-700 mb-2">Owner details</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
                {Object.entries(ownerDetails).map(([k,v]) => (
                  <><span key={k+"-k"} className="capitalize text-slate-400">{k.replace(/_/g," ")}</span><span key={k+"-v"} className="text-slate-700">{v}</span></>
                ))}
              </div>
            </section>
          )}
          {app.rejection_reason && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <strong>Rejection:</strong> {app.rejection_reason}
            </div>
          )}
          <section>
            <p className="font-semibold text-slate-700 mb-2 text-sm">Audit trail</p>
            <div className="space-y-2">
              {audit.map(e => (
                <div key={e.id} className="rounded-lg border bg-slate-50 p-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-800">{e.action.replace(/_/g," ")}</span>
                    <span className="text-xs text-slate-400">{fmt(e.created_at)}</span>
                  </div>
                  {(e.from_state || e.to_state) && (
                    <p className="text-xs text-slate-500 mt-0.5">{e.from_state ?? "—"} → <span className="font-medium">{e.to_state}</span></p>
                  )}
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

/* ── main dashboard ─────────────────────────────────────────────────────── */
type Tab = "overview" | "applications" | "users" | "notifications";

function AdminDashboard() {
  const router = useRouter();
  const [me, setMe] = useState<User | null>(null);
  const [apps, setApps] = useState<AppSummary[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [notifs, setNotifs] = useState<Notification[]>([]);
  const [tab, setTab] = useState<Tab>("overview");
  const [appFilter, setAppFilter] = useState("all");
  const [appSearch, setAppSearch] = useState("");
  const [selectedApp, setSelectedApp] = useState<AppDetail | null>(null);
  const [selectedAudit, setSelectedAudit] = useState<AuditEntry[]>([]);
  const [dispatching, setDispatching] = useState(false);
  const [dispatchMsg, setDispatchMsg] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const [uR, aR] = await Promise.all([
      apiFetch("/auth/me"),
      apiFetch("/officer/applications"),
    ]);
    if (!uR.ok) { clearTokens(); router.replace("/login"); return; }
    const u: User = await uR.json();
    if (u.role !== "admin") { router.replace(u.role === "officer" ? "/officer" : "/dashboard"); return; }
    setMe(u);
    if (aR.ok) setApps(await aR.json());
    setLoading(false);
  }, [router]);

  useEffect(() => { load(); }, [load]);

  // Lazy-load users / notifications when those tabs are first opened
  useEffect(() => {
    if (tab === "users" && users.length === 0) {
      apiFetch("/officer/users").then(async r => { if (r.ok) setUsers(await r.json()); });
    }
    if (tab === "notifications" && notifs.length === 0) {
      apiFetch("/notifications/me").then(async r => { if (r.ok) setNotifs(await r.json()); });
    }
  }, [tab, users.length, notifs.length]);

  async function openAppDetail(app: AppSummary) {
    const [dR, aR] = await Promise.all([
      apiFetch(`/officer/applications/${app.id}`),
      apiFetch(`/officer/applications/${app.id}/audit`),
    ]);
    if (dR.ok) setSelectedApp(await dR.json());
    if (aR.ok) setSelectedAudit(await aR.json());
  }

  async function dispatchNotifications() {
    setDispatching(true); setDispatchMsg("");
    const r = await apiFetch("/notifications/dispatch", { method: "POST" });
    if (r.ok) setDispatchMsg("Dispatch queued. Notifications will be delivered shortly.");
    else setDispatchMsg("Dispatch failed.");
    setDispatching(false);
  }

  /* ── derived stats ── */
  const counts: Record<string, number> = {};
  apps.forEach(a => { counts[a.status] = (counts[a.status] ?? 0) + 1; });
  const revenue = apps.filter(a => ["paid","officer_review","approved","completed"].includes(a.status)).length * 50000;

  const statCards = [
    { icon: "📋", label: "Total applications", value: apps.length,      color: "border-slate-200 bg-white" },
    { icon: "⏳", label: "Pending action",     value: (counts.submitted ?? 0) + (counts.under_review ?? 0) + (counts.officer_review ?? 0), color: "border-blue-200 bg-blue-50" },
    { icon: "💰", label: "Revenue (RWF)",       value: `${revenue.toLocaleString()}`, color: "border-emerald-200 bg-emerald-50" },
    { icon: "✅", label: "Completed",           value: (counts.completed ?? 0), color: "border-green-200 bg-green-50" },
    { icon: "❌", label: "Rejected",            value: counts.rejected ?? 0, color: "border-red-200 bg-red-50" },
  ];

  const filteredApps = apps.filter(a => {
    const matchStatus = appFilter === "all" || a.status === appFilter;
    const matchSearch = a.business_name.toLowerCase().includes(appSearch.toLowerCase()) ||
                        a.citizen_email.toLowerCase().includes(appSearch.toLowerCase());
    return matchStatus && matchSearch;
  });

  const TAB_LABELS: { id: Tab; label: string }[] = [
    { id: "overview",      label: "Overview" },
    { id: "applications",  label: "Applications" },
    { id: "users",         label: "Users" },
    { id: "notifications", label: "Notifications" },
  ];

  if (loading) return (
    <main className="flex min-h-[60vh] items-center justify-center">
      <svg className="h-8 w-8 animate-spin text-blue-500" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
    </main>
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-10">
      {/* header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-slate-500">Admin portal</p>
          <h1 className="text-2xl font-bold text-slate-900">Platform Dashboard</h1>
          <p className="text-sm text-slate-500">{me?.full_name} · {me?.email}</p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-sm font-medium text-purple-700">
          <span className="h-2 w-2 rounded-full bg-purple-500"></span>Admin
        </span>
      </div>

      {/* tabs */}
      <div className="mt-8 flex gap-1 border-b overflow-x-auto scrollbar-none">
        {TAB_LABELS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`whitespace-nowrap px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition ${
              tab === t.id
                ? "border-blue-600 text-blue-700"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW tab ── */}
      {tab === "overview" && (
        <div className="mt-8 space-y-8">
          {/* stat cards */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {statCards.map(s => (
              <div key={s.label} className={`rounded-xl border p-5 ${s.color}`}>
                <div className="text-2xl mb-1">{s.icon}</div>
                <p className="text-2xl font-bold text-slate-900">{s.value}</p>
                <p className="mt-0.5 text-xs text-slate-500">{s.label}</p>
              </div>
            ))}
          </div>

          {/* status breakdown */}
          <div>
            <h2 className="mb-4 font-semibold text-slate-800">Status breakdown</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {Object.entries(STATUS_META).map(([k, v]) => (
                <div key={k} className="rounded-xl border bg-white p-4 flex items-center justify-between">
                  <div>
                    <p className="text-xl font-bold text-slate-900">{counts[k] ?? 0}</p>
                    <p className="text-xs text-slate-500">{v.label}</p>
                  </div>
                  <Badge label={String(counts[k] ?? 0)} color={v.color} />
                </div>
              ))}
            </div>
          </div>

          {/* recent applications */}
          <div>
            <h2 className="mb-4 font-semibold text-slate-800">Recent submissions</h2>
            <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                    <th className="px-4 py-3">Business</th>
                    <th className="px-4 py-3 hidden sm:table-cell">Citizen</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 hidden md:table-cell">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {apps.slice(0, 8).map(a => (
                    <tr key={a.id} className="hover:bg-slate-50 cursor-pointer" onClick={() => openAppDetail(a)}>
                      <td className="px-4 py-3 font-medium text-slate-900">{a.business_name}</td>
                      <td className="px-4 py-3 text-slate-500 hidden sm:table-cell">{a.citizen_email}</td>
                      <td className="px-4 py-3"><Badge label={STATUS_META[a.status]?.label ?? a.status} color={STATUS_META[a.status]?.color ?? ""} /></td>
                      <td className="px-4 py-3 text-slate-500 hidden md:table-cell">{fmt(a.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ── APPLICATIONS tab ── */}
      {tab === "applications" && (
        <div className="mt-8 space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <input value={appSearch} onChange={e => setAppSearch(e.target.value)}
              placeholder="Search business or email…"
              className="flex-1 rounded-lg border px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"/>
            <select value={appFilter} onChange={e => setAppFilter(e.target.value)}
              className="rounded-lg border px-3.5 py-2.5 text-sm outline-none">
              <option value="all">All statuses</option>
              {Object.keys(STATUS_META).map(s => (
                <option key={s} value={s}>{STATUS_META[s].label}</option>
              ))}
            </select>
          </div>

          <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-3">Business</th>
                  <th className="px-4 py-3 hidden sm:table-cell">Citizen</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 hidden md:table-cell">Submitted</th>
                  <th className="px-4 py-3 hidden lg:table-cell">Reg. No.</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredApps.length === 0 && (
                  <tr><td colSpan={6} className="px-4 py-10 text-center text-slate-400">No applications match.</td></tr>
                )}
                {filteredApps.map(a => (
                  <tr key={a.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-900">{a.business_name}</td>
                    <td className="px-4 py-3 text-slate-500 hidden sm:table-cell">{a.citizen_email}</td>
                    <td className="px-4 py-3"><Badge label={STATUS_META[a.status]?.label ?? a.status} color={STATUS_META[a.status]?.color ?? ""} /></td>
                    <td className="px-4 py-3 text-slate-500 hidden md:table-cell">{fmt(a.created_at)}</td>
                    <td className="px-4 py-3 font-mono text-xs text-emerald-700 hidden lg:table-cell">{a.registration_number ?? "—"}</td>
                    <td className="px-4 py-3 text-right">
                      <button onClick={() => openAppDetail(a)} className="rounded-lg border px-3 py-1 text-xs text-blue-600 hover:bg-blue-50">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="border-t bg-slate-50 px-4 py-2 text-xs text-slate-400">
              Showing {filteredApps.length} of {apps.length} applications
            </div>
          </div>
        </div>
      )}

      {/* ── USERS tab ── */}
      {tab === "users" && (
        <div className="mt-8">
          <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
            User management (activate/deactivate, role changes) requires admin-level API endpoints — planned for Day 13.
            This view reads from the applications list to infer citizen accounts.
          </div>
          <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-3">Citizen email</th>
                  <th className="px-4 py-3 hidden sm:table-cell">Applications</th>
                  <th className="px-4 py-3">Latest status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {/* Derive unique citizens from apps */}
                {Array.from(new Map(apps.map(a => [a.citizen_email, a])).values()).map(a => {
                  const citizenApps = apps.filter(x => x.citizen_email === a.citizen_email);
                  const latest = citizenApps.sort((x,y) => y.created_at.localeCompare(x.created_at))[0];
                  return (
                    <tr key={a.citizen_email} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-900">{a.citizen_email}</td>
                      <td className="px-4 py-3 text-slate-500 hidden sm:table-cell">{citizenApps.length}</td>
                      <td className="px-4 py-3"><Badge label={STATUS_META[latest.status]?.label ?? latest.status} color={STATUS_META[latest.status]?.color ?? ""} /></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {/* Real users from API */}
          <div className="mt-6 overflow-hidden rounded-xl border bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3 hidden sm:table-cell">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {users.length === 0 && (
                  <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-400">Loading users…</td></tr>
                )}
                {users.map(u => (
                  <tr key={u.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white ${
                          u.role === "admin" ? "bg-purple-500" : u.role === "officer" ? "bg-blue-500" : "bg-emerald-500"
                        }`}>{u.full_name.charAt(0)}</span>
                        <span className="font-medium text-slate-900 truncate max-w-[120px] sm:max-w-none">{u.full_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-500 hidden sm:table-cell truncate max-w-[160px]">{u.email}</td>
                    <td className="px-4 py-3"><Badge label={u.role} color={ROLE_COLOR[u.role] ?? "bg-slate-100 text-slate-600"} /></td>
                    <td className="px-4 py-3">
                      <Badge label={u.is_active ? "Active" : "Inactive"}
                        color={u.is_active ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── NOTIFICATIONS tab ── */}
      {tab === "notifications" && (
        <div className="mt-8 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-slate-800">Notification queue</h2>
            <div className="flex items-center gap-3">
              {dispatchMsg && <p className="text-sm text-emerald-700">{dispatchMsg}</p>}
              <button onClick={dispatchNotifications} disabled={dispatching}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                {dispatching ? "Dispatching…" : "Flush queue"}
              </button>
            </div>
          </div>
          <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-3">Recipient</th>
                  <th className="px-4 py-3">Subject</th>
                  <th className="px-4 py-3">Channel</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 hidden md:table-cell">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {notifs.length === 0 && (
                  <tr><td colSpan={5} className="px-4 py-10 text-center text-slate-400">No notifications to display.</td></tr>
                )}
                {notifs.map(n => (
                  <tr key={n.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-700">{n.recipient}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs truncate">{n.subject}</td>
                    <td className="px-4 py-3 capitalize text-slate-500">{n.channel}</td>
                    <td className="px-4 py-3">
                      <Badge
                        label={n.delivery_status}
                        color={n.delivery_status === "delivered" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}
                      />
                    </td>
                    <td className="px-4 py-3 text-slate-500 hidden md:table-cell">{fmt(n.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {selectedApp && (
        <AppDetailPanel
          app={selectedApp} audit={selectedAudit}
          onClose={() => { setSelectedApp(null); setSelectedAudit([]); }}
        />
      )}
    </main>
  );
}

export default function AdminPage() {
  return <ProtectedRoute><AdminDashboard /></ProtectedRoute>;
}
