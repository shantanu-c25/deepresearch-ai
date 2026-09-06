"use client";

import {
  useRef,
  type KeyboardEvent,
} from "react";

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
  const tabRefs =
    useRef<
      Array<HTMLButtonElement | null>
    >([]);


  function selectTab(
    index: number
  ) {
    const tab =
      RESEARCH_TABS[index];

    if (!tab) {
      return;
    }

    onTabChange(tab.id);

    tabRefs.current[
      index
    ]?.focus();
  }


  function handleKeyDown(
    event: KeyboardEvent<HTMLButtonElement>,
    index: number
  ) {
    if (
      event.key ===
      "ArrowRight"
    ) {
      event.preventDefault();

      const nextIndex =
        (index + 1) %
        RESEARCH_TABS.length;

      selectTab(
        nextIndex
      );

      return;
    }


    if (
      event.key ===
      "ArrowLeft"
    ) {
      event.preventDefault();

      const previousIndex =
        (
          index -
          1 +
          RESEARCH_TABS.length
        ) %
        RESEARCH_TABS.length;

      selectTab(
        previousIndex
      );

      return;
    }


    if (
      event.key === "Home"
    ) {
      event.preventDefault();

      selectTab(0);

      return;
    }


    if (
      event.key === "End"
    ) {
      event.preventDefault();

      selectTab(
        RESEARCH_TABS.length -
          1
      );
    }
  }


  return (
    <div
      className="
        border-y
        border-[var(--border)]
        bg-[var(--surface-subtle)]
        px-3
        sm:px-5
      "
    >
      <div
        role="tablist"
        aria-label="Research report sections"
        aria-orientation="horizontal"
        className="
          flex
          gap-1
          overflow-x-auto
          py-2
        "
      >
        {RESEARCH_TABS.map(
          (tab, index) => {
            const selected =
              activeTab ===
              tab.id;

            return (
              <button
                key={tab.id}
                ref={(element) => {
                  tabRefs.current[
                    index
                  ] = element;
                }}
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
                onKeyDown={(
                  event
                ) =>
                  handleKeyDown(
                    event,
                    index
                  )
                }
                className={cn(
                  "relative",
                  "inline-flex",
                  "min-h-11",
                  "shrink-0",
                  "items-center",
                  "justify-center",
                  "rounded-[var(--radius-md)]",
                  "px-3.5",
                  "py-2",
                  "text-sm",
                  "font-medium",
                  "transition-colors",
                  "duration-150",
                  selected
                    ? [
                        "bg-[var(--surface)]",
                        "text-[var(--primary)]",
                        "shadow-[var(--shadow-sm)]",
                      ].join(" ")
                    : [
                        "text-[var(--text-muted)]",
                        "hover:bg-[var(--surface-hover)]",
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
                      inset-x-3
                      -bottom-2
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
    </div>
  );
}