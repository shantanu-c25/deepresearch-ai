import type {
  ResearchSource,
} from "@/types/research";


type SourceCardProps = {
  source: ResearchSource;
};


function ExternalLinkIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M15 3h6v6" />

      <path d="M10 14 21 3" />

      <path
        d="
          M18 13v6
          a2 2 0 0 1
          -2 2
          H5
          a2 2 0 0 1
          -2-2
          V8
          a2 2 0 0 1
          2-2
          h6
        "
      />
    </svg>
  );
}


function formatProvider(
  provider: ResearchSource["provider"],
) {
  if (provider === "arxiv") {
    return "arXiv";
  }

  if (provider === "tavily") {
    return "Tavily";
  }

  return "Manual";
}


function formatSourceType(
  sourceType: ResearchSource["source_type"],
) {
  return sourceType
    .replace("-", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


function formatCredibility(
  credibility: ResearchSource["credibility"],
) {
  return credibility
    .replace("-", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


function formatRelevance(
  score: number,
) {
  return `${Math.round(
    score * 100
  )}%`;
}


export function SourceCard({
  source,
}: SourceCardProps) {
  const evidence =
    source.snippet ||
    source.content;

  return (
    <article
      className="
        rounded-[var(--radius-lg)]
        border
        border-[var(--border)]
        bg-[var(--surface)]
        p-5
        shadow-[var(--shadow-sm)]
      "
    >
      <div
        className="
          flex
          flex-wrap
          items-start
          justify-between
          gap-3
        "
      >
        <div className="min-w-0 flex-1">
          <div
            className="
              flex
              flex-wrap
              items-center
              gap-2
            "
          >
            {source.citation_id && (
              <span
                className="
                  inline-flex
                  min-h-7
                  items-center
                  rounded-full
                  bg-[var(--primary-soft)]
                  px-2.5
                  text-xs
                  font-semibold
                  text-[var(--primary)]
                "
              >
                [{source.citation_id}]
              </span>
            )}

            <span
              className="
                text-xs
                font-medium
                text-[var(--text-muted)]
              "
            >
              {formatProvider(
                source.provider
              )}
            </span>

            <span
              aria-hidden="true"
              className="
                text-[var(--text-muted)]
              "
            >
              ·
            </span>

            <span
              className="
                text-xs
                font-medium
                text-[var(--text-muted)]
              "
            >
              {formatSourceType(
                source.source_type
              )}
            </span>
          </div>

          <h4
            className="
              mt-3
              text-base
              font-semibold
              leading-6
              text-[var(--text-primary)]
            "
          >
            {source.title}
          </h4>

          <p
            className="
              mt-1
              break-all
              text-xs
              text-[var(--text-muted)]
            "
          >
            {source.domain}
          </p>
        </div>

        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="
            inline-flex
            min-h-11
            shrink-0
            items-center
            gap-2
            rounded-[var(--radius-md)]
            border
            border-[var(--border)]
            px-3
            text-sm
            font-medium
            text-[var(--text-primary)]
            transition-colors
            hover:bg-[var(--surface-hover)]
          "
        >
          Open Source

          <ExternalLinkIcon />

          <span className="sr-only">
            opens in a new tab
          </span>
        </a>
      </div>


      {evidence && (
        <p
          className="
            mt-4
            text-sm
            leading-6
            text-[var(--text-secondary)]
          "
        >
          {evidence}
        </p>
      )}


      {source.authors.length > 0 && (
        <p
          className="
            mt-4
            text-sm
            text-[var(--text-secondary)]
          "
        >
          <span className="font-medium">
            Authors:
          </span>{" "}

          {source.authors.join(", ")}
        </p>
      )}


      {source.published_date && (
        <p
          className="
            mt-1
            text-sm
            text-[var(--text-secondary)]
          "
        >
          <span className="font-medium">
            Published:
          </span>{" "}

          {source.published_date}
        </p>
      )}


      <div
        className="
          mt-4
          flex
          flex-wrap
          gap-2
          border-t
          border-[var(--border)]
          pt-4
        "
      >
        <span
          className="
            rounded-full
            bg-[var(--surface-subtle)]
            px-2.5
            py-1
            text-xs
            font-medium
            text-[var(--text-secondary)]
          "
        >
          Credibility:{" "}
          {formatCredibility(
            source.credibility
          )}
        </span>

        <span
          className="
            rounded-full
            bg-[var(--surface-subtle)]
            px-2.5
            py-1
            text-xs
            font-medium
            text-[var(--text-secondary)]
          "
        >
          Relevance:{" "}
          {formatRelevance(
            source.relevance_score
          )}
        </span>
      </div>
    </article>
  );
}