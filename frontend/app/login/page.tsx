"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { getApiUrl, readApiBody, saveTokens, type TokenPair } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    const form = new FormData(event.currentTarget);

    // FastAPI's OAuth2 password flow intentionally expects form-urlencoded data
    // with a `username` field; BizReg uses the email address as that username.
    const body = new URLSearchParams({
      username: String(form.get("email")),
      password: String(form.get("password")),
    });
    try {
      const response = await fetch(`${getApiUrl()}/auth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      const data = await readApiBody(response);
      if (!response.ok) throw new Error(data.detail ?? "Unable to sign in");
      saveTokens(data as TokenPair);
      router.push("/dashboard");
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Unable to sign in");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-md px-6 py-16">
      <Link className="text-sm font-semibold text-blue-700" href="/">← BizReg</Link>
      <h1 className="mt-8 text-3xl font-bold">Sign in</h1>
      <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
        <label className="block">Email<input className="mt-1 w-full rounded border p-3" name="email" type="email" required /></label>
        <label className="block">Password<input className="mt-1 w-full rounded border p-3" name="password" type="password" required /></label>
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        <button className="w-full rounded bg-blue-700 p-3 font-semibold text-white disabled:opacity-50" disabled={isSubmitting} type="submit">{isSubmitting ? "Signing in…" : "Sign in"}</button>
      </form>
      <p className="mt-6 text-sm">New to BizReg? <Link className="text-blue-700 underline" href="/register">Create an account</Link>.</p>
    </main>
  );
}
