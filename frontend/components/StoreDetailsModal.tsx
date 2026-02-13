"use client";

import { useEffect, useState } from "react";

import { api } from "../lib/api";
import type { APIError, StoreDetails } from "../lib/types";
import { StatusBadge } from "./StatusBadge";

export function StoreDetailsModal({
  storeId,
  onClose,
  onDeleted,
}: {
  storeId: string;
  onClose: () => void;
  onDeleted: () => void;
}) {
  const [details, setDetails] = useState<StoreDetails | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    api
      .getStore(storeId)
      .then(setDetails)
      .catch((err: APIError) => setError(err.detail || err.error));
  }, [storeId]);

  async function handleDelete() {
    if (!details) {
      return;
    }
    const confirmed = window.confirm(`Delete ${details.name}? This cannot be undone.`);
    if (!confirmed) {
      return;
    }
    setDeleting(true);
    try {
      await api.deleteStore(details.id);
      onDeleted();
      onClose();
    } catch (err) {
      const apiError = err as APIError;
      setError(apiError.detail || apiError.error || "Unable to delete store");
    } finally {
      setDeleting(false);
    }
  }

  function formatDate(value: string) {
    return new Date(value).toLocaleString();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-6">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold">Store overview</h2>
            <p className="text-sm text-dusk">Keep these safe and change your password after first login.</p>
          </div>
          <button onClick={onClose} className="text-sm text-dusk">
            Close
          </button>
        </div>
        {error ? <p className="mt-4 text-sm text-ember">{error}</p> : null}
        {details ? (
          <div className="mt-6 space-y-6">
            <div className="flex items-center justify-between rounded-xl border border-dusk/20 bg-white/70 px-4 py-3">
              <div>
                <p className="text-xs uppercase text-dusk">Status</p>
                <p className="text-sm text-dusk">Created {formatDate(details.created_at)}</p>
              </div>
              <StatusBadge status={details.status} />
            </div>
            <div>
              <p className="text-xs uppercase text-dusk">Storefront URL</p>
              {details.url ? (
                <a className="text-sm font-semibold text-moss" href={details.url} target="_blank" rel="noreferrer">
                  {details.url}
                </a>
              ) : (
                <p className="text-sm text-dusk">Provisioning</p>
              )}
            </div>
            <div>
              <p className="text-xs uppercase text-dusk">WooCommerce Admin</p>
              {details.admin_url ? (
                <a className="text-sm font-semibold text-ink" href={details.admin_url} target="_blank" rel="noreferrer">
                  {details.admin_url}
                </a>
              ) : (
                <p className="text-sm text-dusk">Provisioning</p>
              )}
            </div>
            <div>
              <p className="text-xs uppercase text-dusk">Admin Username</p>
              <p className="text-sm font-semibold text-ink">{details.admin_username || "Pending"}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-dusk">Admin Password</p>
              <div className="flex items-center justify-between rounded-xl border border-dusk/20 px-3 py-2">
                <span className="text-sm font-semibold">
                  {details.admin_password ? "••••••••" : "Pending"}
                </span>
                {details.admin_password ? (
                  <button
                    className="text-xs font-semibold text-moss"
                    onClick={() => navigator.clipboard.writeText(details.admin_password || "")}
                  >
                    Copy
                  </button>
                ) : null}
              </div>
            </div>
            {details.status === "Ready" ? (
              <div className="rounded-xl border border-dusk/20 bg-white/70 p-4 text-sm text-dusk">
                <p className="font-semibold text-ink">Test checkout</p>
                <p>1. Open the storefront and add the sample product to cart.</p>
                <p>2. Checkout using COD (enabled).</p>
                <p>3. Confirm the order in WooCommerce admin.</p>
              </div>
            ) : null}
            <div className="flex items-center justify-between">
              <button
                className="text-sm font-semibold text-ember"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? "Deleting..." : "Delete store"}
              </button>
              <button className="text-sm font-semibold text-dusk" onClick={onClose}>
                Close
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
