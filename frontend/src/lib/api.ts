import type { ResearchResponse } from "@/types/research";

export type { ResearchResponse } from "@/types/research";


export type HealthResponse = {
  status: string;
  service: string;
};


export type GenerateAIResponse = {
  response: string;
};


export type UploadDocumentResponse = {
  status: string;
  document_id: string;
  filename: string;
  file_type: string;
  sections: number;
  chunks: number;
};


export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(
    "http://127.0.0.1:8000/health"
  );

  if (!response.ok) {
    throw new Error(
      "Backend health check failed"
    );
  }

  return response.json();
}


export async function generateAI(
  prompt: string
): Promise<GenerateAIResponse> {
  const response = await fetch(
    "http://127.0.0.1:8000/ai/generate",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "AI generation failed"
    );
  }

  return response.json();
}


export async function runResearch(
  question: string
): Promise<ResearchResponse> {
  const response = await fetch(
    "http://127.0.0.1:8000/research",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
      }),
    }
  );

  if (!response.ok) {
    let message =
      "Research request failed";

    try {
      const errorData =
        await response.json();

      if (errorData.detail) {
        message = errorData.detail;
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  return response.json();
}


export async function uploadDocument(
  file: File
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    "http://127.0.0.1:8000/rag/documents",
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    let message = "Document upload failed";
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        message = errorData.detail;
      }
    } catch {
      // Keep the default error message.
    }
    throw new Error(message);
  }

  return response.json();
}