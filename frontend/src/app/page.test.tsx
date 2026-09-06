import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getHealth, runResearch } from "@/lib/api";

import Home from "./page";


vi.mock("@/lib/api", () => ({
  getHealth: vi.fn(),
  runResearch: vi.fn(),
}));


const mockedGetHealth = vi.mocked(getHealth);
const mockedRunResearch = vi.mocked(runResearch);


describe("Home page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows Connected when the backend health check succeeds", async () => {
    mockedGetHealth.mockResolvedValue({
      status: "ok",
      service: "deep-research-api",
    });

    render(<Home />);

    expect(
      screen.getByRole("heading", { name: "DeepResearch AI" })
    ).toBeInTheDocument();

    expect(
      await screen.findByText("Connected")
    ).toBeInTheDocument();
  });

  it("submits a research question and shows the research report", async () => {
    const user = userEvent.setup();

    mockedGetHealth.mockResolvedValue({
      status: "ok",
      service: "deep-research-api",
    });

    mockedRunResearch.mockResolvedValue({
      question: "Explain RAG.",
      research_brief:
        "RAG retrieves relevant information before generation.",
      critical_analysis:
        "RAG can improve factual grounding but retrieval quality matters.",
      insights:
        "RAG is especially useful when models need external or private knowledge.",
      final_report:
        "RAG combines retrieval with generation to produce grounded responses.",
    });

    render(<Home />);

    const textarea = screen.getByLabelText(
      "What would you like to research?"
    );

    await user.type(
      textarea,
      "Explain RAG."
    );

    await user.click(
      screen.getByRole("button", { name: "Research" })
    );

    expect(
      await screen.findByText(
        "RAG combines retrieval with generation to produce grounded responses."
      )
    ).toBeInTheDocument();
  });

  it("shows a quota message when Gemini free-tier quota is exhausted", async () => {
    const user = userEvent.setup();

    mockedGetHealth.mockResolvedValue({
      status: "ok",
      service: "deep-research-api",
    });

    mockedRunResearch.mockRejectedValue(
      new Error(
        "Gemini free-tier quota has been reached. Please try again later."
      )
    );

    render(<Home />);

    const textarea = screen.getByLabelText(
      "What would you like to research?"
    );

    await user.type(
      textarea,
      "What are the benefits of AI agents?"
    );

    await user.click(
      screen.getByRole("button", { name: "Research" })
    );

    expect(
      await screen.findByRole("alert")
    ).toHaveTextContent(
      "Gemini free-tier quota has been reached. Please try again later."
    );
  });
});