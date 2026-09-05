"use client";

import { FormEvent, useEffect, useState } from "react";

import { generateAI, getHealth } from "@/lib/api";


export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");
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
    setResult("");

    try {
      const data = await generateAI(trimmedPrompt);
      setResult(data.response);
    } catch {
      setError("Unable to generate a response. Please try again.");
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
          <h2>Research Result</h2>
          <p>{result}</p>
        </section>
      )}
    </main>
  );
}