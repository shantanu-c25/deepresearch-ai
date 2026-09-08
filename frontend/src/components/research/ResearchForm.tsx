"use client";

import type {
  FormEvent,
  ReactNode,
} from "react";

import {
  Button,
  Card,
} from "@/components/ui";

import {
  EXAMPLE_RESEARCH_QUESTIONS,
} from "@/lib/constants";


type ResearchFormProps = {
  question: string;

  children?: ReactNode;

  onQuestionChange: (
    question: string
  ) => void;

  onSubmit: () =>
    void | Promise<void>;

  isLoading: boolean;

  isUploadInProgress?: boolean;

  hasError?: boolean;
};


function ResearchIcon() {
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
      <path d="M12 3v3" />
      <path d="M12 18v3" />
      <path d="M3 12h3" />
      <path d="M18 12h3" />

      <path d="m5.6 5.6 2.1 2.1" />
      <path d="m16.3 16.3 2.1 2.1" />
      <path d="m18.4 5.6-2.1 2.1" />
      <path d="m7.7 16.3-2.1 2.1" />

      <circle
        cx="12"
        cy="12"
        r="3"
      />
    </svg>
  );
}


export function ResearchForm({
  question,
  onQuestionChange,
  onSubmit,
  isLoading,
  hasError = false,
  isUploadInProgress = false,
  children,
}: ResearchFormProps) {
  function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    void onSubmit();
  }


  return (
    <Card
      className="
        mx-auto
        mt-8
        max-w-4xl
        p-5
        shadow-[var(--shadow-md)]
        sm:p-6
      "
    >
      <form
        onSubmit={handleSubmit}
        aria-labelledby="research-form-title"
      >
        <div>
          <h3
            id="research-form-title"
            className="
              text-base
              font-semibold
              text-[var(--text-primary)]
            "
          >
            Start a new research task
          </h3>

          <p
            id="research-hint"
            className="
              mt-1
              text-sm
              text-[var(--text-muted)]
            "
          >
            Ask a detailed question and
            DeepResearch AI will coordinate
            specialized research agents.
          </p>
        </div>


        <div className="mt-5">
          <label
            htmlFor="research-prompt"
            className="
              mb-2
              block
              text-sm
              font-semibold
              text-[var(--text-primary)]
            "
          >
            What would you like to research?
          </label>

          <textarea
            id="research-prompt"
            value={question}
            onChange={(event) =>
              onQuestionChange(
                event.target.value
              )
            }
            disabled={isLoading}
            placeholder="Example: What are the main benefits and risks of using AI agents in healthcare?"
            rows={6}
            aria-invalid={hasError}
            aria-describedby={
              hasError
                ? "research-error"
                : "research-hint"
            }
            className="
              min-h-40
              w-full
              rounded-[var(--radius-md)]
              border
              border-[var(--border)]
              bg-[var(--surface)]
              px-4
              py-3
              text-base
              text-[var(--text-primary)]
              placeholder:text-[var(--text-muted)]
              transition-colors
              hover:border-[var(--border-strong)]
              disabled:cursor-not-allowed
              disabled:opacity-70
            "
          />

          {children && (
            <div className="mt-5">
              {children}
            </div>
          )}
        </div>


        <div
          className="
            mt-4
            flex
            flex-wrap
            items-center
            gap-2
          "
        >
          <span
            className="
              mr-1
              text-xs
              font-medium
              text-[var(--text-muted)]
            "
          >
            Examples:
          </span>

          {EXAMPLE_RESEARCH_QUESTIONS.map(
            (example) => (
              <button
                key={example.label}
                type="button"
                disabled={isLoading}
                onClick={() =>
                  onQuestionChange(
                    example.question
                  )
                }
                className="
                  inline-flex
                  min-h-11
                  items-center
                  rounded-full
                  border
                  border-[var(--border)]
                  bg-[var(--surface-subtle)]
                  px-3
                  py-2
                  text-xs
                  font-medium
                  text-[var(--text-secondary)]
                  transition-colors
                  hover:border-[var(--border-strong)]
                  hover:bg-[var(--surface-hover)]
                  hover:text-[var(--text-primary)]
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                {example.label}
              </button>
            )
          )}
        </div>


        <div
          className="
            mt-6
            flex
            justify-end
          "
        >
          <Button
            type="submit"
            size="lg"
            isLoading={isLoading || isUploadInProgress}
            disabled={isUploadInProgress}
            className="
              w-full
              sm:w-auto
            "
          >
            <ResearchIcon />

            {isLoading
              ? "Researching..."
              : "Start Deep Research"}
          </Button>
        </div>
      </form>
    </Card>
  );
}