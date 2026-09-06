"use client";

import {
  useRef,
  useState,
} from "react";

import {
  Button,
} from "@/components/ui";

import type {
  ResearchResponse,
} from "@/types/research";


type ReportActionsProps = {
  result: ResearchResponse;
};


function CopyIcon() {
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
      <rect
        x="9"
        y="9"
        width="13"
        height="13"
        rx="2"
      />

      <path
        d="
          M5 15H4
          a2 2 0 0 1
          -2-2
          V4
          a2 2 0 0 1
          2-2
          h9
          a2 2 0 0 1
          2 2
          v1
        "
      />
    </svg>
  );
}


function CheckIcon() {
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
      <path d="m5 12 4 4L19 6" />
    </svg>
  );
}


function buildReportText(
  result: ResearchResponse
) {
  return [
    "DeepResearch AI",
    "",
    "Research Question",
    result.question,
    "",
    "Research Brief",
    result.research_brief,
    "",
    "Critical Analysis",
    result.critical_analysis,
    "",
    "Insights",
    result.insights,
    "",
    "Final Report",
    result.final_report,
  ].join("\n");
}


export function ReportActions({
  result,
}: ReportActionsProps) {
  const [
    copied,
    setCopied,
  ] = useState(false);

  const timeoutRef =
    useRef<ReturnType<
      typeof setTimeout
    > | null>(null);


  async function handleCopy() {
    const reportText =
      buildReportText(result);

    try {
      await navigator.clipboard.writeText(
        reportText
      );

      setCopied(true);

      if (timeoutRef.current) {
        clearTimeout(
          timeoutRef.current
        );
      }

      timeoutRef.current =
        setTimeout(() => {
          setCopied(false);
        }, 2000);
    } catch {
      setCopied(false);
    }
  }


  return (
    <div
      className="
        flex
        flex-wrap
        items-center
        gap-2
      "
    >
      <Button
        type="button"
        variant="secondary"
        size="sm"
        onClick={handleCopy}
      >
        {copied
          ? <CheckIcon />
          : <CopyIcon />}

        {copied
          ? "Copied"
          : "Copy Report"}
      </Button>

      <span
        aria-live="polite"
        className="sr-only"
      >
        {copied
          ? "Research report copied to clipboard."
          : ""}
      </span>
    </div>
  );
}