import type {
  ButtonHTMLAttributes,
  ReactNode,
} from "react";

import { cn } from "@/lib/utils";


type IconButtonProps =
  Omit<
    ButtonHTMLAttributes<HTMLButtonElement>,
    "aria-label"
  > & {
    icon: ReactNode;
    label: string;
  };


export function IconButton({
  icon,
  label,
  className,
  type = "button",
  ...props
}: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={label}
      title={label}
      className={cn(
        "inline-flex",
        "h-11 w-11",
        "items-center justify-center",
        "rounded-[var(--radius-md)]",
        "border border-[var(--border)]",
        "bg-[var(--surface)]",
        "text-[var(--text-secondary)]",
        "transition-colors duration-150",
        "hover:bg-[var(--surface-hover)]",
        "hover:text-[var(--text-primary)]",
        "disabled:pointer-events-none",
        "disabled:opacity-50",
        className
      )}
      {...props}
    >
      {icon}
    </button>
  );
}