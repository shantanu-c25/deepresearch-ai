import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { generateAI, getHealth } from "@/lib/api";

import Home from "./page";


vi.mock("@/lib/api", () => ({
  getHealth: vi.fn(),
  generateAI: vi.fn(),
}));


const mockedGetHealth = vi.mocked(getHealth);
const mockedGenerateAI = vi.mocked(generateAI);


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

  it("submits a research question and shows the AI response", async () => {
    const user = userEvent.setup();

    mockedGetHealth.mockResolvedValue({
      status: "ok",
      service: "deep-research-api",
    });

    mockedGenerateAI.mockResolvedValue({
      response: "RAG combines retrieval with generation.",
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
        "RAG combines retrieval with generation."
      )
    ).toBeInTheDocument();
  });
});