export type HealthResponse = {
  status: string;
  service: string;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch("http://127.0.0.1:8000/health");

  if (!response.ok) {
    throw new Error("Backend health check failed");
  }

  return response.json();
}