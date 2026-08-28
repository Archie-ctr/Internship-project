"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { apiFetch } from "@/lib/auth";

function BusinessRegistrationForm() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    const form = new FormData(event.currentTarget);
    const payload = {
      business_name: form.get("businessName"), business_type: form.get("businessType"),
      owner: { full_name: form.get("ownerName"), id_number: form.get("ownerId"), phone_number: form.get("ownerPhone") },
      address: { line1: form.get("addressLine"), city: form.get("city"), district: form.get("district"), country: form.get("country") },
    };
    try {
      const response = await apiFetch("/applications", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Could not submit application");
      router.push("/dashboard");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not submit application");
    } finally { setIsSubmitting(false); }
  }

  return <main className="mx-auto max-w-2xl px-6 py-12"><Link className="text-sm font-semibold text-blue-700" href="/services">← Services</Link><h1 className="mt-6 text-3xl font-bold">Business Registration</h1><p className="mt-2 text-slate-600">Complete all fields carefully. You can upload supporting documents in Phase 5.</p><form className="mt-8 space-y-8" onSubmit={submit}><fieldset className="space-y-4"><legend className="text-lg font-semibold">Business details</legend><label className="block">Business name<input className="mt-1 w-full rounded border p-3" name="businessName" minLength={2} maxLength={150} required /></label><label className="block">Business type<select className="mt-1 w-full rounded border p-3" name="businessType" defaultValue="sole_proprietorship"><option value="sole_proprietorship">Sole proprietorship</option><option value="partnership">Partnership</option><option value="limited_company">Limited company</option></select></label></fieldset><fieldset className="space-y-4"><legend className="text-lg font-semibold">Owner details</legend><label className="block">Full name<input className="mt-1 w-full rounded border p-3" name="ownerName" minLength={2} required /></label><label className="block">ID number<input className="mt-1 w-full rounded border p-3" name="ownerId" minLength={6} required /></label><label className="block">Phone number<input className="mt-1 w-full rounded border p-3" name="ownerPhone" type="tel" minLength={7} required /></label></fieldset><fieldset className="space-y-4"><legend className="text-lg font-semibold">Business address</legend><label className="block">Address line<input className="mt-1 w-full rounded border p-3" name="addressLine" minLength={3} required /></label><label className="block">City<input className="mt-1 w-full rounded border p-3" name="city" minLength={2} required /></label><label className="block">District<input className="mt-1 w-full rounded border p-3" name="district" minLength={2} required /></label><label className="block">Country<input className="mt-1 w-full rounded border p-3" name="country" defaultValue="Rwanda" minLength={2} required /></label></fieldset>{error && <p role="alert" className="text-sm text-red-700">{error}</p>}<button className="rounded bg-blue-700 px-5 py-3 font-semibold text-white disabled:opacity-50" disabled={isSubmitting} type="submit">{isSubmitting ? "Submitting…" : "Submit application"}</button></form></main>;
}

export default function BusinessRegistrationPage() { return <ProtectedRoute><BusinessRegistrationForm /></ProtectedRoute>; }
