import {
  Badge,
  Card,
} from "@/components/ui";


type PipelineStatus =
  | "idle"
  | "running"
  | "completed"
  | "error";


type ResearchPipelineProps = {
  status: PipelineStatus;
};


const stages = [
  {
    id: "researching",
    label: "Researching",
    description:
      "Creating the initial research brief.",
  },
  {
    id: "analysis",
    label: "Critical Analysis",
    description:
      "Examining risks, assumptions, and missing perspectives.",
  },
  {
    id: "insights",
    label: "Generating Insights",
    description:
      "Synthesizing patterns, trends, and implications.",
  },
  {
    id: "report",
    label: "Building Report",
    description:
      "Creating the structured final research report.",
  },
] as const;


function getStageState(
  index: number,
  status: PipelineStatus
) {
  if (status === "completed") {
    return "completed";
  }

  if (status === "error") {
    return index === 0
      ? "error"
      : "waiting";
  }

  if (status === "running") {
    return index === 0
      ? "active"
      : "waiting";
  }

  return "waiting";
}


function StageIcon({
  state,
}: {
  state:
    | "completed"
    | "active"
    | "waiting"
    | "error";
}) {
  if (state === "completed") {
    return (
      <span
        aria-hidden="true"
        className="
          inline-flex
          h-8
          w-8
          items-center
          justify-center
          rounded-full
          bg-[var(--success-soft)]
          text-[var(--success)]
        "
      >
        ✓
      </span>
    );
  }

  if (state === "error") {
    return (
      <span
        aria-hidden="true"
        className="
          inline-flex
          h-8
          w-8
          items-center
          justify-center
          rounded-full
          bg-[var(--danger-soft)]
          text-[var(--danger)]
        "
      >
        !
      </span>
    );
  }

  if (state === "active") {
    return (
      <span
        aria-hidden="true"
        className="
          relative
          inline-flex
          h-8
          w-8
          items-center
          justify-center
          rounded-full
          bg-[var(--primary-soft)]
          text-[var(--primary)]
        "
      >
        <span
          className="
            h-2.5
            w-2.5
            rounded-full
            bg-current
          "
        />
      </span>
    );
  }

  return (
    <span
      aria-hidden="true"
      className="
        inline-flex
        h-8
        w-8
        items-center
        justify-center
        rounded-full
        border
        border-[var(--border)]
        bg-[var(--surface-subtle)]
        text-[var(--text-muted)]
      "
    >
      ○
    </span>
  );
}


function StageBadge({
  state,
}: {
  state:
    | "completed"
    | "active"
    | "waiting"
    | "error";
}) {
  if (state === "completed") {
    return (
      <Badge variant="success">
        Completed
      </Badge>
    );
  }

  if (state === "active") {
    return (
      <Badge variant="primary">
        Running
      </Badge>
    );
  }

  if (state === "error") {
    return (
      <Badge variant="danger">
        Failed
      </Badge>
    );
  }

  return (
    <Badge variant="neutral">
      Queued
    </Badge>
  );
}


export function ResearchPipeline({
  status,
}: ResearchPipelineProps) {
  const statusMessage =
    status === "running"
      ? "Research is in progress."
      : status === "completed"
        ? "Research pipeline completed."
        : status === "error"
          ? "Research pipeline stopped because of an error."
          : "Research pipeline is waiting to start.";


  return (
    <Card
      className="
        mx-auto
        mt-8
        max-w-4xl
        overflow-hidden
      "
    >
      <div
        className="
          border-b
          border-[var(--border)]
          px-5
          py-4
          sm:px-6
        "
      >
        <div
          className="
            flex
            flex-wrap
            items-center
            justify-between
            gap-3
          "
        >
          <div>
            <h2
              className="
                text-base
                font-semibold
                text-[var(--text-primary)]
              "
            >
              Research Pipeline
            </h2>

            <p
              className="
                mt-1
                text-sm
                text-[var(--text-muted)]
              "
            >
              Multi-agent workflow status
            </p>
          </div>

          {status === "running" && (
            <Badge variant="primary">
              Running
            </Badge>
          )}

          {status === "completed" && (
            <Badge variant="success">
              Complete
            </Badge>
          )}
        </div>
      </div>


      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {statusMessage}
      </div>


      <ol
        className="
          grid
          gap-0
          p-5
          sm:p-6
          lg:grid-cols-4
        "
      >
        {stages.map(
          (stage, index) => {
            const state =
              getStageState(
                index,
                status
              );

            return (
              <li
                key={stage.id}
                className="
                  relative
                  flex
                  gap-3
                  border-b
                  border-[var(--border)]
                  py-4
                  last:border-b-0
                  lg:block
                  lg:border-b-0
                  lg:border-r
                  lg:px-5
                  lg:py-1
                  lg:last:border-r-0
                "
              >
                <StageIcon
                  state={state}
                />

                <div
                  className="
                    min-w-0
                    flex-1
                    lg:mt-3
                  "
                >
                  <div
                    className="
                      flex
                      flex-wrap
                      items-center
                      gap-2
                    "
                  >
                    <h3
                      className="
                        text-sm
                        font-semibold
                        text-[var(--text-primary)]
                      "
                    >
                      {stage.label}
                    </h3>

                    <StageBadge
                      state={state}
                    />
                  </div>

                  <p
                    className="
                      mt-1
                      text-xs
                      leading-5
                      text-[var(--text-muted)]
                    "
                  >
                    {stage.description}
                  </p>
                </div>
              </li>
            );
          }
        )}
      </ol>


      {status === "running" && (
        <div
          className="
            border-t
            border-[var(--border)]
            bg-[var(--surface-subtle)]
            px-5
            py-3
            text-xs
            text-[var(--text-muted)]
            sm:px-6
          "
        >
          Step-level progress will become
          live when backend progress
          streaming is added.
        </div>
      )}
    </Card>
  );
}