"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "../lib/api";
import type { APIError, Store } from "../lib/types";
import { StatusBadge } from "./StatusBadge";

export function StoreList({
  onOpen,
  refreshKey,
}: {
  onOpen: (id: string) => void;
  refreshKey: number;
}) {
  const [stores, setStores] = useState<Store[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [actioningId, setActioningId] = useState<string | null>(null);

  const pendingIds = useMemo(
    () => stores.filter((store) => store.status === "Pending").map((store) => store.id),
    [stores],
  );

  const load = useCallback(async () => {
    try {
      const data = await api.listStores();
      setStores(data);
      setError(null);
    } catch (err) {
      const apiError = err as APIError;
      setError(apiError.detail || apiError.error || "Unable to load stores");
    }
  }, []);

  useEffect(() => {
    let active = true;
    const loadSafe = async () => {
      if (!active) {
        return;
      }
      await load();
    };

    loadSafe();
    const interval = setInterval(() => {
      if (pendingIds.length > 0) {
        loadSafe();
      }
    }, 5000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [pendingIds.length, refreshKey, load]);

  async function handleDelete(store: Store) {
    const confirmed = window.confirm(`Delete ${store.name}? This cannot be undone.`);
    if (!confirmed) {
      return;
    }
    setActioningId(store.id);
    try {
      await api.deleteStore(store.id);
      await load();
    } catch (err) {
      const apiError = err as APIError;
      setError(apiError.detail || apiError.error || "Unable to delete store");
    } finally {
      setActioningId(null);
    }
  }

  function formatDate(value: string) {
    return new Date(value).toLocaleString();
  }

  if (error) {
    return <p className="text-sm text-ember">{error}</p>;
  }

  if (stores.length === 0) {
    return (
      <div className="rounded-2xl border border-dusk/20 bg-white/60 p-6 text-center">
        <p className="text-lg font-semibold">No stores yet</p>
        <p className="text-sm text-dusk">Create your first store to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {stores.map((store) => (
        <div
          key={store.id}
          className="flex flex-wrap items-center justify-between gap-4 rounded-2xl bg-white/80 p-5 shadow-md"
        >
          <div className="space-y-1">
            <p className="text-lg font-semibold text-ink">{store.name}</p>
            <p className="text-sm text-dusk">{store.domain}</p>
            <p className="text-xs text-dusk">Created {formatDate(store.created_at)}</p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={store.status} />
            {store.url ? (
              <a className="text-sm font-semibold text-moss" href={store.url} target="_blank" rel="noreferrer">
                Open storefront
              </a>
            ) : null}
            <button
              className="text-sm font-semibold text-ink"
              onClick={() => onOpen(store.id)}
            >
              Details
            </button>
            <button
              className="text-sm font-semibold text-ember"
              onClick={() => handleDelete(store)}
              disabled={actioningId === store.id}
            >
              {actioningId === store.id ? "Deleting..." : "Delete"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
