"use client";

import {
  useState,
} from "react";

import {
  Badge,
  Card,
  MarkdownRenderer,
} from "@/components/ui";

import {
  ReportActions,
} from "@/components/research/ReportActions";

import {
  ResearchTabs,
} from "@/components/research/ResearchTabs";

import {
  SourcesPanel,
} from "@/components/research/SourcesPanel";

import type {
  ResearchResponse,
  ResearchTabId,
} from "@/types/research";


type ResearchWorkspaceProps = {
  result: ResearchResponse;
};


type ReportSectionProps = {
  content: string;

  citationIds: string[];

  onCitationClick: (
    citationId: string
  ) => void;
};


function ReportSection({
  content,
  citationIds,
  onCitationClick,
}: ReportSectionProps) {
  return (
    <MarkdownRenderer
      content={content}
      citationIds={
        citationIds
      }
      onCitationClick={
        onCitationClick
      }
    />
  );
}


export function ResearchWorkspace({
  result,
}: ResearchWorkspaceProps) {
  const [
    activeTab,
    setActiveTab,
  ] =
    useState<ResearchTabId>(
      "overview"
    );


  const citationIds =
    result.sources
      .map(
        (source) =>
          source.citation_id
      )
      .filter(
        (
          citationId
        ): citationId is string =>
          Boolean(citationId)
      );


  function handleCitationClick(
    citationId: string
  ) {
    const sourceExists =
      result.sources.some(
        (source) =>
          source.citation_id ===
          citationId
      );


    if (!sourceExists) {
      return;
    }


    setActiveTab(
      "sources"
    );


    window.setTimeout(
      () => {
        const sourceElement =
          document.getElementById(
            `source-${citationId}`
          );


        if (!sourceElement) {
          return;
        }


        sourceElement.scrollIntoView?.({
          behavior: "smooth",
          block: "center",
        });


        sourceElement.focus({
          preventScroll: true,
        });
      },
      0
    );
  }


  function renderPanel() {
    if (
      activeTab ===
      "research-brief"
    ) {
      return (
        <>
          <h3
            className="
              text-xl
              font-semibold
              text-[var(--text-primary)]
            "
          >
            Research Brief
          </h3>

          <div className="mt-5">
            <ReportSection
              content={
                result.research_brief
              }
              citationIds={
                citationIds
              }
              onCitationClick={
                handleCitationClick
              }
            />
          </div>
        </>
      );
    }


    if (
      activeTab ===
      "critical-analysis"
    ) {
      return (
        <Card
          tone="warning"
          className="
            p-5
            shadow-none
            sm:p-6
          "
        >
          <h3
            className="
              text-xl
              font-semibold
              text-[var(--warning)]
            "
          >
            Critical Analysis
          </h3>

          <div className="mt-5">
            <ReportSection
              content={
                result.critical_analysis
              }
              citationIds={
                citationIds
              }
              onCitationClick={
                handleCitationClick
              }
            />
          </div>
        </Card>
      );
    }


    if (
      activeTab ===
      "insights"
    ) {
      return (
        <Card
          tone="insight"
          className="
            p-5
            shadow-none
            sm:p-6
          "
        >
          <h3
            className="
              text-xl
              font-semibold
              text-[var(--insight)]
            "
          >
            Key Insights
          </h3>

          <div className="mt-5">
            <ReportSection
              content={
                result.insights
              }
              citationIds={
                citationIds
              }
              onCitationClick={
                handleCitationClick
              }
            />
          </div>
        </Card>
      );
    }


    if (
      activeTab ===
      "final-report"
    ) {
      return (
        <>
          <h3
            className="
              text-xl
              font-semibold
              text-[var(--text-primary)]
            "
          >
            Final Research Report
          </h3>

          <div className="mt-5">
            <ReportSection
              content={
                result.final_report
              }
              citationIds={
                citationIds
              }
              onCitationClick={
                handleCitationClick
              }
            />
          </div>
        </>
      );
    }


    if (
      activeTab ===
      "sources"
    ) {
      return (
        <SourcesPanel
          sources={
            result.sources ?? []
          }
        />
      );
    }


    return (
      <>
        <h3
          className="
            text-xl
            font-semibold
            text-[var(--text-primary)]
          "
        >
          Research Overview
        </h3>

        <p
          className="
            mt-2
            text-sm
            font-medium
            text-[var(--text-muted)]
          "
        >
          Original research question
        </p>

        <blockquote
          className="
            mt-3
            rounded-[var(--radius-md)]
            border-l-4
            border-[var(--primary)]
            bg-[var(--primary-soft)]
            px-4
            py-3
            text-[var(--text-primary)]
          "
        >
          {result.question}
        </blockquote>


        <div
          className="
            mt-8
            border-t
            border-[var(--border)]
            pt-7
          "
        >
          <h4
            className="
              mb-4
              text-base
              font-semibold
              text-[var(--text-primary)]
            "
          >
            Research Brief
          </h4>

          <ReportSection
            content={
              result.research_brief
            }
            citationIds={
              citationIds
            }
            onCitationClick={
              handleCitationClick
            }
          />
        </div>
      </>
    );
  }


  return (
    <section
      aria-labelledby="research-report-title"
      className="
        mx-auto
        mt-10
        max-w-5xl
      "
    >
      <Card
        className="
          overflow-hidden
          shadow-[var(--shadow-md)]
        "
      >
        <div
          className="
            flex
            flex-wrap
            items-start
            justify-between
            gap-4
            px-5
            py-5
            sm:px-6
          "
        >
          <div>
            <div
              className="
                flex
                flex-wrap
                items-center
                gap-2
              "
            >
              <h2
                id="research-report-title"
                className="
                  text-2xl
                  font-bold
                  tracking-tight
                  text-[var(--text-primary)]
                "
              >
                Research Report
              </h2>

              <Badge
                variant="success"
              >
                Completed
              </Badge>
            </div>


            <p
              className="
                mt-2
                max-w-2xl
                text-sm
                text-[var(--text-muted)]
              "
            >
              Multi-agent research,
              analysis, insights, and
              final synthesis.
            </p>
          </div>


          <ReportActions
            result={result}
          />
        </div>


        <ResearchTabs
          activeTab={
            activeTab
          }
          onTabChange={
            setActiveTab
          }
        />


        <div
          id={`panel-${activeTab}`}
          role="tabpanel"
          aria-labelledby={`tab-${activeTab}`}
          tabIndex={0}
          className="
            report-container
            min-h-72
            px-5
            py-7
            sm:px-7
            sm:py-9
            lg:px-10
          "
        >
          {renderPanel()}
        </div>
      </Card>
    </section>
  );
}