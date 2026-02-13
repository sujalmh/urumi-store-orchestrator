import type { StoreStatus } from "../lib/types";

const statusStyles: Record<StoreStatus, string> = {
  Pending: "bg-sand/20 text-sand",
  Ready: "bg-moss/20 text-moss",
  Error: "bg-ember/20 text-ember",
  Deleting: "bg-dusk/20 text-dusk",
};

const statusLabels: Record<StoreStatus, string> = {
  Pending: "Provisioning",
  Ready: "Ready",
  Error: "Failed",
  Deleting: "Deleting",
};

export function StatusBadge({ status }: { status: StoreStatus }) {
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${statusStyles[status]}`}>
      {statusLabels[status]}
    </span>
  );
}
