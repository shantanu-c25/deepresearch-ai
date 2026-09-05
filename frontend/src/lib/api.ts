export type HealthResponse = {
  status: string;
  service: string;
};

export type GenerateAIResponse = {
  response: string;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch("http://127.0.0.1:8000/health");

  if (!response.ok) {
    throw new Error("Backend health check failed");
  }

  return response.json();
}

export async function generateAI(
  prompt: string
): Promise<GenerateAIResponse> {
  const response = await fetch("http://127.0.0.1:8000/ai/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
    }),
  });

  if (!response.ok) {
    throw new Error("AI generation failed");
  }

  return response.json();
}