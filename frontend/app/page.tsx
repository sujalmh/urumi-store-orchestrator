"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { CreateStoreForm } from "../components/CreateStoreForm";
import { StoreDetailsModal } from "../components/StoreDetailsModal";
import { StoreList } from "../components/StoreList";
import { clearToken, getToken } from "../lib/auth";
import type { Store } from "../lib/types";

export default function HomePage() {
  const router = useRouter();
  const [selectedStoreId, setSelectedStoreId] = useState<string | null>(null);
  const [lastCreated, setLastCreated] = useState<Store | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
    } else {
      setAuthorized(true);
    }
  }, [router]);

  if (!authorized) {
    return null; // or a loading spinner
  }

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <main className="min-h-screen bg-hero-glow">
      <section className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-12 lg:flex-row">
        <div className="flex-1 space-y-6">
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <p className="text-sm uppercase tracking-[0.2em] text-dusk">Provisioning Console</p>
              <h1 className="text-4xl font-semibold leading-tight text-ink lg:text-5xl">
                Launch isolated WooCommerce stores in minutes.
              </h1>
              <p className="text-base text-dusk">
                Create tenant-safe WordPress stores backed by Kubernetes, complete with TLS and resource controls.
              </p>
            </div>
          </div>
          <CreateStoreForm
            onCreated={(store) => {
              setLastCreated(store);
              setRefreshKey((value) => value + 1);
            }}
          />
          {lastCreated ? (
            <p className="text-sm text-moss">
              Store {lastCreated.name} is provisioning. Status will update automatically.
            </p>
          ) : null}
        </div>
        <div className="flex-1 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Your stores</h2>
            <div className="flex items-center gap-4">
              <span className="text-xs uppercase tracking-[0.2em] text-dusk">Status</span>
              <button 
                onClick={handleLogout}
                className="text-xs font-medium text-ember hover:underline"
              >
                LOGOUT
              </button>
            </div>
          </div>
          <StoreList onOpen={(id) => setSelectedStoreId(id)} refreshKey={refreshKey} />
        </div>
      </section>
      {selectedStoreId ? (
        <StoreDetailsModal
          storeId={selectedStoreId}
          onClose={() => setSelectedStoreId(null)}
          onDeleted={() => setRefreshKey((value) => value + 1)}
        />
      ) : null}
    </main>
  );
}
