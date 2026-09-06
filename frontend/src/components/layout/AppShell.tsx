import type {
  ReactNode,
} from "react";


type AppShellProps = {
  children: ReactNode;
};


export function AppShell({
  children,
}: AppShellProps) {
  return (
    <div
      className="
        min-h-screen
        bg-[var(--app-bg)]
        text-[var(--text-primary)]
      "
    >
      {children}
    </div>
  );
}