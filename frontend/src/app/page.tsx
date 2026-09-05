"use client";

import { useEffect, useState } from "react";

import { getHealth } from "@/lib/api";


export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

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

  return (
    <main>
      <h1>DeepResearch AI</h1>

      <p>Multi-Agent AI Research & Intelligence Platform</p>

      <p>
        Backend Status: <strong>{backendStatus}</strong>
      </p>
    </main>
  );
}