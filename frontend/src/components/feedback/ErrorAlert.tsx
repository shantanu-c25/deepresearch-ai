import {
  Card,
} from "@/components/ui";


type ErrorAlertProps = {
  message: string;
};


function WarningIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="
        mt-0.5
        h-5
        w-5
        shrink-0
      "
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 9v4" />
      <path d="M12 17h.01" />

      <path
        d="
          M10.3 3.8
          2.2 18
          A2 2 0 0 0
          3.9 21
          h16.2
          a2 2 0 0 0
          1.7-3
          L13.7 3.8
          a2 2 0 0 0
          -3.4 0
        "
      />
    </svg>
  );
}


export function ErrorAlert({
  message,
}: ErrorAlertProps) {
  return (
    <Card
      id="research-error"
      tone="danger"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
      className="
        mx-auto
        mt-6
        max-w-4xl
        px-4
        py-3
        shadow-none
      "
    >
      <div
        className="
          flex
          gap-3
          text-[var(--danger)]
        "
      >
        <WarningIcon />

        <div>
          <p
            className="
              text-sm
              font-semibold
            "
          >
            Research request failed
          </p>

          <p
            className="
              mt-0.5
              text-sm
            "
          >
            {message}
          </p>
        </div>
      </div>
    </Card>
  );
}