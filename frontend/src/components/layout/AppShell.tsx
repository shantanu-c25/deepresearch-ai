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

        <footer
          className="
            app-container
            border-t
            border-[var(--border)]
            py-6
            text-center
            text-sm
            text-[var(--text-secondary)]
          "
        >
          © 2026 Shantanu Chattopadhyay
        </footer>
    </div>
  );
}