"use client";

import {
  RESEARCH_TABS,
} from "@/lib/constants";

import {
  cn,
} from "@/lib/utils";

import type {
  ResearchTabId,
} from "@/types/research";


type ResearchTabsProps = {
  activeTab: ResearchTabId;

  onTabChange: (
    tab: ResearchTabId
  ) => void;
};


export function ResearchTabs({
  activeTab,
  onTabChange,
}: ResearchTabsProps) {
  return (
    <div
      role="tablist"
      aria-label="Research report sections"
      className="
        flex
        gap-1
        overflow-x-auto
        border-b
        border-[var(--border)]
        px-3
        sm:px-5
      "
    >
      {RESEARCH_TABS.map(
        (tab) => {
          const selected =
            activeTab === tab.id;

          return (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              type="button"
              role="tab"
              aria-selected={
                selected
              }
              aria-controls={`panel-${tab.id}`}
              tabIndex={
                selected
                  ? 0
                  : -1
              }
              onClick={() =>
                onTabChange(
                  tab.id
                )
              }
              className={cn(
                "relative",
                "min-h-12",
                "shrink-0",
                "px-3",
                "text-sm",
                "font-medium",
                "transition-colors",
                selected
                  ? "text-[var(--primary)]"
                  : [
                      "text-[var(--text-muted)]",
                      "hover:text-[var(--text-primary)]",
                    ].join(" ")
              )}
            >
              {tab.label}

              {selected && (
                <span
                  aria-hidden="true"
                  className="
                    absolute
                    inset-x-2
                    bottom-0
                    h-0.5
                    rounded-full
                    bg-[var(--primary)]
                  "
                />
              )}
            </button>
          );
        }
      )}
    </div>
  );
}