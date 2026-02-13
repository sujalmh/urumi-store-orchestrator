export type StoreStatus = "Pending" | "Ready" | "Error" | "Deleting";

export interface Store {
  id: string;
  name: string;
  domain: string;
  status: StoreStatus;
  created_at: string;
  url?: string;
}

export interface StoreDetails extends Store {
  admin_url?: string;
  admin_username?: string;
  admin_password?: string;
}

export interface CreateStoreRequest {
  name: string;
  domain: string;
}

export interface HealthStatus {
  healthy: boolean;
  wordpress_ready: boolean;
  mysql_ready: boolean;
  details?: string;
}

export interface APIError {
  error: string;
  detail?: string;
  field_errors?: Record<string, string[]>;
}
