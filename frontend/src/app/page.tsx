"use client";

import {
  useState,
} from "react";

import {
  ErrorAlert,
} from "@/components/feedback/ErrorAlert";

import {
  AppHeader,
} from "@/components/layout/AppHeader";

import {
  AppShell,
} from "@/components/layout/AppShell";

import {
  ResearchForm,
} from "@/components/research/ResearchForm";

import {
  ResearchHero,
} from "@/components/research/ResearchHero";

import {
  ResearchPipeline,
} from "@/components/research/ResearchPipeline";

import {
  ResearchWorkspace,
} from "@/components/research/ResearchWorkspace";

import {
  DocumentUpload,
} from "@/components/research/DocumentUpload";

import {
  useBackendHealth,
} from "@/hooks/useBackendHealth";

import {
  useResearch,
} from "@/hooks/useResearch";


export default function Home() {
  const [isUploadInProgress, setIsUploadInProgress] =
    useState(false);

  const {
    status: backendStatus,
  } = useBackendHealth();


  const {
    question,
    setQuestion,
    result,
    isLoading,
    error,
    submitResearch,
  } = useResearch();


  const pipelineStatus =
    isLoading
      ? "running"
      : result
        ? "completed"
        : error
          ? "error"
          : "idle";


  return (
    <AppShell>
      <AppHeader
        backendStatus={
          backendStatus
        }
      />

      <main
        className="
          app-container
          py-10
          sm:py-14
        "
      >
        <section
          aria-labelledby="research-title"
        >
          <ResearchHero />

          <ResearchForm
            question={question}
            onQuestionChange={
              setQuestion
            }
            onSubmit={
              submitResearch
            }
            isLoading={
              isLoading
            }
            isUploadInProgress={
              isUploadInProgress
            }
            hasError={
              Boolean(error)
            }
          >
            <DocumentUpload
              onUploadingChange={
                setIsUploadInProgress
              }
            />
          </ResearchForm>

          {error && (
            <ErrorAlert
              message={error}
            />
          )}

          <ResearchPipeline
            status={
              pipelineStatus
            }
          />
        </section>


        {result && (
          <ResearchWorkspace
            result={result}
          />
        )}
      </main>
    </AppShell>
  );
}