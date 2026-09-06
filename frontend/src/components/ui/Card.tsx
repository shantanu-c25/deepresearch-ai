import type {
  HTMLAttributes,
  ReactNode,
} from "react";

import { cn } from "@/lib/utils";


type CardTone =
  | "default"
  | "subtle"
  | "warning"
  | "danger"
  | "insight"
  | "success";


type CardProps =
  HTMLAttributes<HTMLDivElement> & {
    children: ReactNode;
    tone?: CardTone;
  };


const toneClasses: Record<
  CardTone,
  string
> = {
  default:
    "bg-[var(--surface)] " +
    "border-[var(--border)]",

  subtle:
    "bg-[var(--surface-subtle)] " +
    "border-[var(--border)]",

  warning:
    "bg-[var(--warning-soft)] " +
    "border-[var(--warning-border)]",

  danger:
    "bg-[var(--danger-soft)] " +
    "border-[var(--danger-border)]",

  insight:
    "bg-[var(--insight-soft)] " +
    "border-[var(--insight-border)]",

  success:
    "bg-[var(--success-soft)] " +
    "border-[var(--success-border)]",
};


export function Card({
  children,
  tone = "default",
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={cn(
        "rounded-[var(--radius-lg)]",
        "border",
        "shadow-[var(--shadow-sm)]",
        toneClasses[tone],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}