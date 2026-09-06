"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  getHealth,
  ResearchResponse,
  runResearch,
} from "@/lib/api";


export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function checkBackend() {
      try {
        const health = await getHealth();

        setBackendStatus(
          health.status === "ok" ? "Connected" : "Unavailable"
        );
      } catch {
        setBackendStatus("Offline");
      }
    }

    checkBackend();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedPrompt = prompt.trim();

    if (!trimmedPrompt) {
      setError("Please enter a research question.");
      return;
    }

    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await runResearch(trimmedPrompt);
      setResult(data);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Unable to complete the research. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>DeepResearch AI</h1>

      <p>Multi-Agent AI Research & Intelligence Platform</p>

      <p>
        Backend Status: <strong>{backendStatus}</strong>
      </p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="research-prompt">
          What would you like to research?
        </label>

        <textarea
          id="research-prompt"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Example: Explain how AI agents are used in healthcare."
          rows={6}
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Researching..." : "Research"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {result && (
        <section>
          <h2>Research Report</h2>

          <h3>Research Question</h3>
          <p>{result.question}</p>

          <h3>Research Brief</h3>
          <p>{result.research_brief}</p>

          <h3>Critical Analysis</h3>
          <p>{result.critical_analysis}</p>

          <h3>Insights</h3>
          <p>{result.insights}</p>

          <h3>Final Report</h3>
          <p>{result.final_report}</p>
        </section>
      )}
    </main>
  );
}