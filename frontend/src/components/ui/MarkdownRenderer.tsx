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
};


const components: Components = {
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
      {children}
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
      {children}
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
      {children}
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
      {children}
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
      {children}
    </p>
  ),

  strong: ({ children }) => (
    <strong
      className="
        font-semibold
        text-[var(--text-primary)]
      "
    >
      {children}
    </strong>
  ),

  em: ({ children }) => (
    <em
      className="
        italic
        text-[var(--text-secondary)]
      "
    >
      {children}
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
      {children}
    </li>
  ),

  blockquote: ({ children }) => (
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
      {children}
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
        href?.startsWith("http://") ||
        href?.startsWith("https://")
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
      Boolean(className);

    if (isCodeBlock) {
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

  table: ({ children }) => (
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

  thead: ({ children }) => (
    <thead
      className="
        bg-[var(--surface-subtle)]
        text-[var(--text-primary)]
      "
    >
      {children}
    </thead>
  ),

  tbody: ({ children }) => (
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
      {children}
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
      {children}
    </td>
  ),
};


export function MarkdownRenderer({
  content,
  className,
}: MarkdownRendererProps) {
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