"use client";

import { useState } from "react";

import { api } from "../lib/api";
import type { APIError, CreateStoreRequest, Store } from "../lib/types";

export function CreateStoreForm({ onCreated }: { onCreated: (store: Store) => void }) {
  const [form, setForm] = useState<CreateStoreRequest>({ name: "", domain: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const store = await api.createStore(form);
      onCreated(store);
      setForm({ name: "", domain: "" });
    } catch (err) {
      const apiError = err as APIError;
      setError(apiError.detail || apiError.error || "Unable to create store");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4 rounded-2xl bg-white/80 p-6 shadow-lg">
      <div>
        <label className="text-sm font-semibold text-dusk">Store name</label>
        <input
          className="mt-2 w-full rounded-xl border border-dusk/20 bg-white px-4 py-3 text-sm"
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
          placeholder="artisan-supplies"
          pattern="[a-z0-9-]{3,63}"
          title="Use 3-63 lowercase letters, numbers, and hyphens"
          required
        />
      </div>
      <div>
        <label className="text-sm font-semibold text-dusk">Custom domain</label>
        <input
          className="mt-2 w-full rounded-xl border border-dusk/20 bg-white px-4 py-3 text-sm"
          value={form.domain}
          onChange={(event) => setForm({ ...form, domain: event.target.value })}
          placeholder="store.example.com"
          pattern="[a-z0-9.-]+\.[a-z]{2,}"
          title="Enter a valid domain like store.example.com"
          required
        />
      </div>
      {error ? <p className="text-sm text-ember">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-ink px-4 py-3 text-sm font-semibold text-white transition hover:bg-dusk"
      >
        {loading ? "Provisioning..." : "Create store"}
      </button>
    </form>
  );
}
