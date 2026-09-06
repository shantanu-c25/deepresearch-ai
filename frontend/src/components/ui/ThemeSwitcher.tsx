"use client";

import type {
  ReactNode,
} from "react";

import { useTheme } from "@/hooks/useTheme";
import { cn } from "@/lib/utils";
import type {
  ThemePreference,
} from "@/types/theme";


type ThemeOption = {
  value: ThemePreference;
  label: string;
  icon: ReactNode;
};


const options: ThemeOption[] = [
  {
    value: "light",
    label: "Light theme",
    icon: (
      <svg
        aria-hidden="true"
        viewBox="0 0 24 24"
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle
          cx="12"
          cy="12"
          r="4"
        />

        <path d="M12 2v2" />
        <path d="M12 20v2" />
        <path d="m4.93 4.93 1.41 1.41" />
        <path d="m17.66 17.66 1.41 1.41" />
        <path d="M2 12h2" />
        <path d="M20 12h2" />
        <path d="m6.34 17.66-1.41 1.41" />
        <path d="m19.07 4.93-1.41 1.41" />
      </svg>
    ),
  },
  {
    value: "system",
    label: "Use system theme",
    icon: (
      <svg
        aria-hidden="true"
        viewBox="0 0 24 24"
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <rect
          x="3"
          y="4"
          width="18"
          height="13"
          rx="2"
        />

        <path d="M8 21h8" />
        <path d="M12 17v4" />
      </svg>
    ),
  },
  {
    value: "dark",
    label: "Dark theme",
    icon: (
      <svg
        aria-hidden="true"
        viewBox="0 0 24 24"
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path
          d="
            M21 12.79
            A9 9 0 1 1
            11.21 3
            7 7 0 0 0
            21 12.79
          "
        />
      </svg>
    ),
  },
];


export function ThemeSwitcher() {
  const {
    preference,
    setPreference,
  } = useTheme();


  return (
    <div
      role="group"
      aria-label="Color theme"
      className="
        inline-flex
        items-center
        rounded-[var(--radius-md)]
        border
        border-[var(--border)]
        bg-[var(--surface-subtle)]
        p-1
      "
    >
      {options.map((option) => {
        const isSelected =
          preference === option.value;

        return (
          <button
            key={option.value}
            type="button"
            aria-label={option.label}
            aria-pressed={isSelected}
            title={option.label}
            onClick={() =>
              setPreference(
                option.value
              )
            }
            className={cn(
              "inline-flex",
              "h-9 w-9",
              "items-center justify-center",
              "rounded-[8px]",
              "transition-colors",
              "duration-150",
              isSelected
                ? [
                    "bg-[var(--surface)]",
                    "text-[var(--primary)]",
                    "shadow-[var(--shadow-sm)]",
                  ].join(" ")
                : [
                    "text-[var(--text-muted)]",
                    "hover:bg-[var(--surface)]",
                    "hover:text-[var(--text-primary)]",
                  ].join(" ")
            )}
          >
            {option.icon}

            <span className="sr-only">
              {option.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}