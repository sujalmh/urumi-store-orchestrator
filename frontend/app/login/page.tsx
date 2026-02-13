"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { api } from "../../lib/api";
import { setToken } from "../../lib/auth";
import type { APIError } from "../../lib/types";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();

    try {
      setError(null);
      setLoading(true);
      const { access_token } = await api.login(email, password);
      if (access_token) {
        setToken(access_token);
        router.push("/");
      } else {
        setError("Invalid response from server");
      }
    } catch (err: unknown) {
      const apiError = err as APIError;
      setError(apiError.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-hero-glow p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <p className="text-xs uppercase tracking-[0.2em] text-dusk/70">Welcome back</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-ink">Sign in</h1>
        </div>

        <form onSubmit={submit} className="space-y-4 rounded-2xl bg-white p-6 shadow-xl shadow-dusk/5 backdrop-blur-sm">
          <div>
            <label className="mb-1 block text-sm font-medium text-dusk">
              Email
            </label>
            <input
              type="email"
              required
              className="block w-full rounded-xl border border-dusk/10 bg-fog/30 px-3 py-2 text-sm text-ink placeholder-dusk/40 transition focus:border-ink/20 focus:bg-white focus:outline-none focus:ring-2 focus:ring-ink/5"
              placeholder="name@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-dusk">
              Password
            </label>
            <input
              type="password"
              required
              className="block w-full rounded-xl border border-dusk/10 bg-fog/30 px-3 py-2 text-sm text-ink placeholder-dusk/40 transition focus:border-ink/20 focus:bg-white focus:outline-none focus:ring-2 focus:ring-ink/5"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error ? (
            <div className="rounded-lg bg-ember/5 p-3 text-center text-xs font-medium text-ember border border-ember/10">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-ink py-2.5 text-sm font-semibold text-white shadow-lg shadow-ink/10 transition hover:bg-dusk hover:shadow-xl hover:shadow-ink/20 disabled:opacity-70"
          >
            {loading ? "Verifying..." : "Continue"}
          </button>
        </form>
        
        <p className="text-center text-sm text-dusk/60">
          No account?{" "}
          <Link href="/register" className="font-medium text-ink hover:text-dusk transition-colors">
            Create one
          </Link>
        </p>
      </div>
    </main>
  );
}
