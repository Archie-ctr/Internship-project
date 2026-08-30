"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/auth";

const inputCls =
  "mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20";

const labelCls = "block text-sm font-medium text-slate-700";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className={labelCls}>{label}</label>
      {children}
    </div>
  );
}

function BusinessRegistrationForm() {
  const router       = useRouter();
  const [error, setError]           = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    const form    = new FormData(event.currentTarget);
    const payload = {
      business_name: form.get("businessName"),
      business_type: form.get("businessType"),
      owner: {
        full_name:    form.get("ownerName"),
        id_number:    form.get("ownerId"),
        phone_number: form.get("ownerPhone"),
      },
      address: {
        line1:    form.get("addressLine"),
        city:     form.get("city"),
        district: form.get("district"),
        country:  form.get("country"),
      },
    };
    try {
      const r = await apiFetch("/applications", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail ?? "Could not submit application");
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not submit application");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <Link
        className="inline-flex items-center gap-1 text-sm font-semibold text-blue-700 hover:text-blue-600"
        href="/services"
      >
        <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><polyline points="15 18 9 12 15 6"/></svg>
        Services
      </Link>

      <div className="mt-6">
        <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">Business Registration</h1>
        <p className="mt-1 text-sm text-slate-500">
          Complete all sections carefully. All fields are required.
        </p>
      </div>

      <form className="mt-8 space-y-8" onSubmit={submit}>

        {/* ── Business details ── */}
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <h2 className="mb-5 text-base font-semibold text-slate-900">Business details</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <Field label="Business name">
                <input className={inputCls} name="businessName" minLength={2} maxLength={150} required placeholder="e.g. Kigali Tech Solutions Ltd" />
              </Field>
            </div>
            <div className="sm:col-span-2">
              <Field label="Business type">
                <select className={inputCls} name="businessType" defaultValue="sole_proprietorship">
                  <option value="sole_proprietorship">Sole proprietorship</option>
                  <option value="partnership">Partnership</option>
                  <option value="limited_company">Limited company</option>
                </select>
              </Field>
            </div>
          </div>
        </section>

        {/* ── Owner details ── */}
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <h2 className="mb-5 text-base font-semibold text-slate-900">Owner details</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <Field label="Full name">
                <input className={inputCls} name="ownerName" minLength={2} required placeholder="Jean Paul Uwimana" />
              </Field>
            </div>
            <Field label="National ID number">
              <input className={inputCls} name="ownerId" minLength={6} required placeholder="1199880012345" />
            </Field>
            <Field label="Phone number">
              <input className={inputCls} name="ownerPhone" type="tel" minLength={7} required placeholder="+250788123456" />
            </Field>
          </div>
        </section>

        {/* ── Address ── */}
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <h2 className="mb-5 text-base font-semibold text-slate-900">Business address</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <Field label="Street / address line">
                <input className={inputCls} name="addressLine" minLength={3} required placeholder="KG 7 Ave" />
              </Field>
            </div>
            <Field label="City">
              <input className={inputCls} name="city" minLength={2} required placeholder="Kigali" />
            </Field>
            <Field label="District">
              <input className={inputCls} name="district" minLength={2} required placeholder="Gasabo" />
            </Field>
            <div className="sm:col-span-2">
              <Field label="Country">
                <input className={inputCls} name="country" minLength={2} required defaultValue="Rwanda" />
              </Field>
            </div>
          </div>
        </section>

        {error && (
          <div role="alert" className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <svg className="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white shadow transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
        >
          {isSubmitting ? (
            <>
              <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
              Submitting…
            </>
          ) : "Submit application"}
        </button>
      </form>
    </main>
  );
}

export default function BusinessRegistrationPage() {
  return <ProtectedRoute><BusinessRegistrationForm /></ProtectedRoute>;
}
