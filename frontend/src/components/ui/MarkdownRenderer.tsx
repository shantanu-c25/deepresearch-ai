import {
  Fragment,
  type ReactNode,
} from "react";

import ReactMarkdown, {
  type Components,
} from "react-markdown";

import remarkGfm from "remark-gfm";

import {
  cn,
} from "@/lib/utils";


type MarkdownRendererProps = {
  content: string;
  className?: string;

  citationIds?: string[];

  onCitationClick?: (
    citationId: string
  ) => void;
};


type CitationAwareChildrenProps = {
  children: ReactNode;

  validCitationIds: Set<string>;

  onCitationClick?: (
    citationId: string
  ) => void;
};


const CITATION_PATTERN =
  /\[(S\d+)\]/g;


function CitationAwareChildren({
  children,
  validCitationIds,
  onCitationClick,
}: CitationAwareChildrenProps) {
  if (
    typeof children !== "string"
  ) {
    return <>{children}</>;
  }


  const parts: ReactNode[] = [];

  let lastIndex = 0;

  let match:
    | RegExpExecArray
    | null;


  CITATION_PATTERN.lastIndex = 0;


  while (
    (
      match =
        CITATION_PATTERN.exec(
          children
        )
    ) !== null
  ) {
    const fullMatch =
      match[0];

    const citationId =
      match[1];

    const matchIndex =
      match.index;


    if (
      matchIndex >
      lastIndex
    ) {
      parts.push(
        children.slice(
          lastIndex,
          matchIndex
        )
      );
    }


    const isValidCitation =
      validCitationIds.has(
        citationId
      );


    if (
      isValidCitation &&
      onCitationClick
    ) {
      parts.push(
        <button
          key={`${citationId}-${matchIndex}`}
          type="button"
          onClick={() =>
            onCitationClick(
              citationId
            )
          }
          aria-label={
            `View source ${citationId}`
          }
          className="
            mx-0.5
            inline-flex
            min-h-7
            items-center
            rounded-full
            border
            border-[var(--primary)]/30
            bg-[var(--primary-soft)]
            px-2
            align-baseline
            text-xs
            font-semibold
            leading-none
            text-[var(--primary)]
            transition-colors
            hover:border-[var(--primary)]
            hover:bg-[var(--surface-hover)]
          "
        >
          {fullMatch}
        </button>
      );
    } else if (
      isValidCitation
    ) {
      parts.push(
        <span
          key={`${citationId}-${matchIndex}`}
          className="
            mx-0.5
            inline-flex
            items-center
            rounded-full
            bg-[var(--primary-soft)]
            px-1.5
            py-0.5
            text-xs
            font-semibold
            text-[var(--primary)]
          "
        >
          {fullMatch}
        </span>
      );
    } else {
      /*
       * Unknown citation IDs remain
       * plain text.
       *
       * We never create a clickable
       * source that does not actually
       * exist in the API response.
       */
      parts.push(
        fullMatch
      );
    }


    lastIndex =
      matchIndex +
      fullMatch.length;
  }


  if (
    lastIndex === 0
  ) {
    return <>{children}</>;
  }


  if (
    lastIndex <
    children.length
  ) {
    parts.push(
      children.slice(
        lastIndex
      )
    );
  }


  return (
    <>
      {parts.map(
        (
          part,
          index
        ) => (
          <Fragment
            key={index}
          >
            {part}
          </Fragment>
        )
      )}
    </>
  );
}


function createComponents(
  validCitationIds: Set<string>,
  onCitationClick?: (
    citationId: string
  ) => void
): Components {
  function renderChildren(
    children: ReactNode
  ) {
    return (
      <CitationAwareChildren
        validCitationIds={
          validCitationIds
        }
        onCitationClick={
          onCitationClick
        }
      >
        {children}
      </CitationAwareChildren>
    );
  }


  return {
    h1: ({ children }) => (
      <h3
        className="
          mb-3
          mt-7
          text-xl
          font-bold
          tracking-tight
          text-[var(--text-primary)]
          first:mt-0
          sm:text-2xl
        "
      >
        {renderChildren(
          children
        )}
      </h3>
    ),


    h2: ({ children }) => (
      <h4
        className="
          mb-3
          mt-7
          text-lg
          font-bold
          text-[var(--text-primary)]
          first:mt-0
          sm:text-xl
        "
      >
        {renderChildren(
          children
        )}
      </h4>
    ),


    h3: ({ children }) => (
      <h5
        className="
          mb-2
          mt-6
          text-base
          font-semibold
          text-[var(--text-primary)]
          first:mt-0
          sm:text-lg
        "
      >
        {renderChildren(
          children
        )}
      </h5>
    ),


    h4: ({ children }) => (
      <h6
        className="
          mb-2
          mt-5
          text-base
          font-semibold
          text-[var(--text-primary)]
        "
      >
        {renderChildren(
          children
        )}
      </h6>
    ),


    p: ({ children }) => (
      <p
        className="
          mb-4
          text-[15px]
          leading-7
          text-[var(--text-secondary)]
          last:mb-0
        "
      >
        {renderChildren(
          children
        )}
      </p>
    ),


    strong: ({
      children,
    }) => (
      <strong
        className="
          font-semibold
          text-[var(--text-primary)]
        "
      >
        {renderChildren(
          children
        )}
      </strong>
    ),


    em: ({ children }) => (
      <em
        className="
          italic
          text-[var(--text-secondary)]
        "
      >
        {renderChildren(
          children
        )}
      </em>
    ),


    ul: ({ children }) => (
      <ul
        className="
          mb-5
          ml-6
          list-disc
          space-y-2
          text-[15px]
          leading-7
          text-[var(--text-secondary)]
        "
      >
        {children}
      </ul>
    ),


    ol: ({ children }) => (
      <ol
        className="
          mb-5
          ml-6
          list-decimal
          space-y-2
          text-[15px]
          leading-7
          text-[var(--text-secondary)]
        "
      >
        {children}
      </ol>
    ),


    li: ({ children }) => (
      <li className="pl-1">
        {renderChildren(
          children
        )}
      </li>
    ),


    blockquote: ({
      children,
    }) => (
      <blockquote
        className="
          my-5
          rounded-r-[var(--radius-md)]
          border-l-4
          border-[var(--primary)]
          bg-[var(--primary-soft)]
          px-4
          py-3
          text-[var(--text-secondary)]
        "
      >
        {renderChildren(
          children
        )}
      </blockquote>
    ),


    hr: () => (
      <hr
        className="
          my-7
          border-0
          border-t
          border-[var(--border)]
        "
      />
    ),


    a: ({
      href,
      children,
    }) => {
      const isExternal =
        Boolean(
          href?.startsWith(
            "http://"
          ) ||
          href?.startsWith(
            "https://"
          )
        );


      return (
        <a
          href={href}
          target={
            isExternal
              ? "_blank"
              : undefined
          }
          rel={
            isExternal
              ? "noopener noreferrer"
              : undefined
          }
          className="
            font-medium
            text-[var(--primary)]
            underline
            decoration-[var(--primary)]/40
            underline-offset-4
            hover:decoration-[var(--primary)]
          "
        >
          {children}

          {isExternal && (
            <span className="sr-only">
              {" "}
              (opens in a new tab)
            </span>
          )}
        </a>
      );
    },


    code: ({
      className,
      children,
    }) => {
      const isCodeBlock =
        Boolean(
          className
        );


      if (
        isCodeBlock
      ) {
        return (
          <code
            className={cn(
              "font-mono",
              "text-sm",
              className
            )}
          >
            {children}
          </code>
        );
      }


      /*
       * Citations inside code are
       * deliberately not converted
       * into citation controls.
       */
      return (
        <code
          className="
            rounded
            border
            border-[var(--border)]
            bg-[var(--surface-subtle)]
            px-1.5
            py-0.5
            font-mono
            text-[0.9em]
            text-[var(--text-primary)]
          "
        >
          {children}
        </code>
      );
    },


    pre: ({ children }) => (
      <pre
        className="
          my-5
          overflow-x-auto
          rounded-[var(--radius-md)]
          border
          border-[var(--border)]
          bg-[var(--surface-subtle)]
          p-4
          text-sm
          leading-6
          text-[var(--text-primary)]
        "
      >
        {children}
      </pre>
    ),


    table: ({
      children,
    }) => (
      <div
        className="
          my-6
          overflow-x-auto
          rounded-[var(--radius-md)]
          border
          border-[var(--border)]
        "
      >
        <table
          className="
            w-full
            min-w-[640px]
            border-collapse
            text-left
            text-sm
          "
        >
          {children}
        </table>
      </div>
    ),


    thead: ({
      children,
    }) => (
      <thead
        className="
          bg-[var(--surface-subtle)]
          text-[var(--text-primary)]
        "
      >
        {children}
      </thead>
    ),


    tbody: ({
      children,
    }) => (
      <tbody
        className="
          divide-y
          divide-[var(--border)]
        "
      >
        {children}
      </tbody>
    ),


    tr: ({ children }) => (
      <tr
        className="
          transition-colors
          hover:bg-[var(--surface-hover)]
        "
      >
        {children}
      </tr>
    ),


    th: ({ children }) => (
      <th
        className="
          border-b
          border-[var(--border)]
          px-4
          py-3
          font-semibold
          text-[var(--text-primary)]
        "
      >
        {renderChildren(
          children
        )}
      </th>
    ),


    td: ({ children }) => (
      <td
        className="
          px-4
          py-3
          align-top
          leading-6
          text-[var(--text-secondary)]
        "
      >
        {renderChildren(
          children
        )}
      </td>
    ),
  };
}


export function MarkdownRenderer({
  content,
  className,
  citationIds = [],
  onCitationClick,
}: MarkdownRendererProps) {
  const validCitationIds =
    new Set(
      citationIds
    );


  const components =
    createComponents(
      validCitationIds,
      onCitationClick
    );


  return (
    <div
      className={cn(
        "min-w-0",
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[
          remarkGfm,
        ]}
        components={
          components
        }
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}