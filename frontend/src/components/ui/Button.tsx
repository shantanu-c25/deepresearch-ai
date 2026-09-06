import type {
  ButtonHTMLAttributes,
  ReactNode,
} from "react";

import { cn } from "@/lib/utils";


type ButtonVariant =
  | "primary"
  | "secondary"
  | "ghost"
  | "danger";


type ButtonSize =
  | "sm"
  | "md"
  | "lg";


type ButtonProps =
  ButtonHTMLAttributes<HTMLButtonElement> & {
    children: ReactNode;
    variant?: ButtonVariant;
    size?: ButtonSize;
    isLoading?: boolean;
  };


const variantClasses: Record<
  ButtonVariant,
  string
> = {
  primary:
    "bg-[var(--primary)] text-[var(--primary-text)] " +
    "border border-transparent " +
    "hover:bg-[var(--primary-hover)]",

  secondary:
    "bg-[var(--surface)] text-[var(--text-primary)] " +
    "border border-[var(--border)] " +
    "hover:bg-[var(--surface-hover)] " +
    "hover:border-[var(--border-strong)]",

  ghost:
    "bg-transparent text-[var(--text-secondary)] " +
    "border border-transparent " +
    "hover:bg-[var(--surface-subtle)] " +
    "hover:text-[var(--text-primary)]",

  danger:
    "bg-[var(--danger)] text-white " +
    "border border-transparent " +
    "hover:opacity-90",
};


const sizeClasses: Record<
  ButtonSize,
  string
> = {
  sm: "min-h-10 px-3.5 py-2 text-sm",
  md: "min-h-11 px-4 py-2.5 text-sm",
  lg: "min-h-12 px-5 py-3 text-base",
};


export function Button({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled,
  className,
  type = "button",
  ...props
}: ButtonProps) {
  const isDisabled =
    disabled || isLoading;

  return (
    <button
      type={type}
      disabled={isDisabled}
      aria-busy={isLoading || undefined}
      className={cn(
        "inline-flex items-center justify-center gap-2",
        "rounded-[var(--radius-md)]",
        "font-semibold",
        "transition-colors duration-150",
        "disabled:pointer-events-none",
        "disabled:cursor-not-allowed",
        "disabled:opacity-55",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {isLoading && (
        <span
          aria-hidden="true"
          className="
            h-4 w-4
            rounded-full
            border-2
            border-current
            border-r-transparent
            animate-spin
          "
        />
      )}

      {children}
    </button>
  );
}