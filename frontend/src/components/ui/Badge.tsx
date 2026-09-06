import type {
  HTMLAttributes,
  ReactNode,
} from "react";

import { cn } from "@/lib/utils";


type BadgeVariant =
  | "neutral"
  | "primary"
  | "success"
  | "warning"
  | "danger"
  | "insight";


type BadgeProps =
  HTMLAttributes<HTMLSpanElement> & {
    children: ReactNode;
    variant?: BadgeVariant;
  };


const variantClasses: Record<
  BadgeVariant,
  string
> = {
  neutral:
    "bg-[var(--surface-subtle)] " +
    "text-[var(--text-secondary)] " +
    "border-[var(--border)]",

  primary:
    "bg-[var(--primary-soft)] " +
    "text-[var(--primary)] " +
    "border-[var(--primary)]/30",

  success:
    "bg-[var(--success-soft)] " +
    "text-[var(--success)] " +
    "border-[var(--success-border)]",

  warning:
    "bg-[var(--warning-soft)] " +
    "text-[var(--warning)] " +
    "border-[var(--warning-border)]",

  danger:
    "bg-[var(--danger-soft)] " +
    "text-[var(--danger)] " +
    "border-[var(--danger-border)]",

  insight:
    "bg-[var(--insight-soft)] " +
    "text-[var(--insight)] " +
    "border-[var(--insight-border)]",
};


export function Badge({
  children,
  variant = "neutral",
  className,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5",
        "rounded-full",
        "border",
        "px-2.5 py-1",
        "text-xs font-semibold",
        "leading-none",
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}