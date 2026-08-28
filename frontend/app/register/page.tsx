"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { getApiUrl, readApiBody, saveTokens, type TokenPair } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const password = String(form.get("password"));
    if (password !== String(form.get("confirmPassword"))) {
      setError("Passwords do not match");
      return;
    }
    setIsSubmitting(true);
    try {
      const response = await fetch(`${getApiUrl()}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name: form.get("fullName"), email: form.get("email"), password }),
      });
      const data = await readApiBody(response);
      if (!response.ok) throw new Error(data.detail ?? "Unable to create account");
      saveTokens(data as TokenPair);
      router.push("/dashboard");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to create account");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <Link className="text-sm font-semibold text-blue-700" href="/">← BizReg</Link>
      <h1 className="mt-8 text-3xl font-bold">Create a citizen account</h1>
      <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
        <label className="block">Full name<input className="mt-1 w-full rounded border p-3" name="fullName" minLength={2} required /></label>
        <label className="block">Email<input className="mt-1 w-full rounded border p-3" name="email" type="email" required /></label>
        <label className="block">Password<input className="mt-1 w-full rounded border p-3" name="password" type="password" minLength={12} required /></label>
        <label className="block">Confirm password<input className="mt-1 w-full rounded border p-3" name="confirmPassword" type="password" minLength={12} required /></label>
        <p className="text-xs text-slate-600">Use at least 12 characters. Passwords are bcrypt-hashed before storage.</p>
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        <button className="w-full rounded bg-blue-700 p-3 font-semibold text-white disabled:opacity-50" disabled={isSubmitting} type="submit">{isSubmitting ? "Creating account…" : "Create account"}</button>
      </form>
      <p className="mt-6 text-sm">Already registered? <Link className="text-blue-700 underline" href="/login">Sign in</Link>.</p>
    </main>
  );
}
