import {
  Badge,
} from "@/components/ui";

import type {
  BackendStatus as BackendStatusValue,
} from "@/hooks/useBackendHealth";


type BackendStatusProps = {
  status: BackendStatusValue;
};


const statusConfig = {
  checking: {
    label: "Checking backend",
    variant: "neutral" as const,
    dotClass:
      "bg-[var(--text-muted)]",
  },

  connected: {
    label: "Backend Connected",
    variant: "success" as const,
    dotClass:
      "bg-[var(--success)]",
  },

  unavailable: {
    label: "Backend Unavailable",
    variant: "warning" as const,
    dotClass:
      "bg-[var(--warning)]",
  },

  offline: {
    label: "Backend Offline",
    variant: "danger" as const,
    dotClass:
      "bg-[var(--danger)]",
  },
};


export function BackendStatus({
  status,
}: BackendStatusProps) {
  const config =
    statusConfig[status];


  return (
    <Badge
      variant={config.variant}
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="min-h-8"
    >
      <span
        aria-hidden="true"
        className={`
          h-2
          w-2
          rounded-full
          ${config.dotClass}
        `}
      />

      {config.label}
    </Badge>
  );
}