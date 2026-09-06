import {
  BackendStatus,
} from "@/components/feedback/BackendStatus";

import {
  ThemeSwitcher,
} from "@/components/ui";

import type {
  BackendStatus as BackendStatusValue,
} from "@/hooks/useBackendHealth";

import {
  APP_NAME,
  APP_TAGLINE,
} from "@/lib/constants";


type AppHeaderProps = {
  backendStatus: BackendStatusValue;
};


function BrandIcon() {
  return (
    <span
      aria-hidden="true"
      className="
        inline-flex
        h-10
        w-10
        shrink-0
        items-center
        justify-center
        rounded-[var(--radius-md)]
        bg-[var(--primary)]
        text-[var(--primary-text)]
        shadow-[var(--shadow-sm)]
      "
    >
      <svg
        viewBox="0 0 24 24"
        className="h-5 w-5"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle
          cx="11"
          cy="11"
          r="7"
        />

        <path d="m20 20-3.5-3.5" />

        <path d="M8.5 11h5" />

        <path d="M11 8.5v5" />
      </svg>
    </span>
  );
}


export function AppHeader({
  backendStatus,
}: AppHeaderProps) {
  return (
    <header
      className="
        sticky
        top-0
        z-40
        border-b
        border-[var(--border)]
        bg-[var(--surface)]/95
        backdrop-blur
      "
    >
      <div
        className="
          app-container
          grid
          grid-cols-[minmax(0,1fr)_auto]
          items-center
          gap-x-3
          gap-y-2
          py-3
          md:grid-cols-[minmax(0,1fr)_auto_auto]
        "
      >
        <div
          className="
            flex
            min-w-0
            items-center
            gap-3
          "
        >
          <BrandIcon />

          <div className="min-w-0">
            <h1
              className="
                truncate
                text-base
                font-bold
                tracking-tight
                text-[var(--text-primary)]
                sm:text-lg
              "
            >
              {APP_NAME}
            </h1>

            <p
              className="
                hidden
                truncate
                text-xs
                text-[var(--text-muted)]
                sm:block
              "
            >
              {APP_TAGLINE}
            </p>
          </div>
        </div>


        <div
          className="
            col-span-2
            row-start-2
            md:col-span-1
            md:col-start-2
            md:row-start-1
          "
        >
          <BackendStatus
            status={backendStatus}
          />
        </div>


        <div
          className="
            col-start-2
            row-start-1
            md:col-start-3
          "
        >
          <ThemeSwitcher />
        </div>
      </div>
    </header>
  );
}