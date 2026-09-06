import {
  SourceCard,
} from "@/components/research/SourceCard";

import type {
  ResearchSource,
} from "@/types/research";


type SourcesPanelProps = {
  sources: ResearchSource[];
};


export function SourcesPanel({
  sources,
}: SourcesPanelProps) {
  if (sources.length === 0) {
    return (
      <div
        className="
          rounded-[var(--radius-lg)]
          border
          border-dashed
          border-[var(--border)]
          bg-[var(--surface-subtle)]
          p-6
        "
      >
        <h3
          className="
            text-lg
            font-semibold
            text-[var(--text-primary)]
          "
        >
          Sources & Evidence
        </h3>

        <p
          className="
            mt-2
            text-sm
            leading-6
            text-[var(--text-secondary)]
          "
        >
          No validated external sources
          were available for this
          research run.
        </p>
      </div>
    );
  }


  return (
    <div>
      <div
        className="
          flex
          flex-wrap
          items-end
          justify-between
          gap-3
        "
      >
        <div>
          <h3
            className="
              text-xl
              font-semibold
              text-[var(--text-primary)]
            "
          >
            Sources & Evidence
          </h3>

          <p
            className="
              mt-2
              text-sm
              leading-6
              text-[var(--text-secondary)]
            "
          >
            Validated external sources
            used to ground the research
            brief.
          </p>
        </div>

        <p
          className="
            text-sm
            font-medium
            text-[var(--text-muted)]
          "
        >
          {sources.length}{" "}
          {sources.length === 1
            ? "source"
            : "sources"}
        </p>
      </div>


      <div
        className="
          mt-6
          grid
          gap-4
        "
      >
        {sources.map(
          (source) => (
            <SourceCard
              key={source.id}
              source={source}
            />
          )
        )}
      </div>
    </div>
  );
}