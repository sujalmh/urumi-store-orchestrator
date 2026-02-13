import { getToken } from "./auth";
import type { APIError, CreateStoreRequest, HealthStatus, Store, StoreDetails } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = (await response.json()) as APIError;
    throw error;
  }

  return (await response.json()) as T;
}

export const api = {
  register: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  createStore: (payload: CreateStoreRequest) =>
    request<Store>("/stores", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listStores: () => request<Store[]>("/stores"),
  getStore: (id: string) => request<StoreDetails>(`/stores/${id}`),
  deleteStore: (id: string) => request<void>(`/stores/${id}`, { method: "DELETE" }),
  getHealth: (id: string) => request<HealthStatus>(`/stores/${id}/health`),
};
