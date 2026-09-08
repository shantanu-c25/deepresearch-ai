import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  getHealth,
  runResearch,
  uploadDocument,
} from "@/lib/api";

import {
  ThemeProvider,
} from "@/providers/ThemeProvider";

import Home from "./page";


vi.mock("@/lib/api", () => ({
  getHealth: vi.fn(),
  runResearch: vi.fn(),
  uploadDocument: vi.fn(),
}));


const mockedGetHealth =
  vi.mocked(getHealth);

const mockedRunResearch =
  vi.mocked(runResearch);

const mockedUploadDocument =
  vi.mocked(uploadDocument);


function renderHome() {
  return render(
    <ThemeProvider>
      <Home />
    </ThemeProvider>
  );
}


describe("Home page", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    window.localStorage.clear();
  });


  it(
    "shows Backend Connected when the backend health check succeeds",
    async () => {
      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });

      renderHome();

      expect(
        screen.getByRole(
          "heading",
          {
            name: "DeepResearch AI",
          }
        )
      ).toBeInTheDocument();

      expect(
        await screen.findByText(
          "Backend Connected"
        )
      ).toBeInTheDocument();
    }
  );


  it(
    "submits a research question and shows the research report",
    async () => {
      const user =
        userEvent.setup();

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

        sources: [],
      });

      renderHome();

      const textarea =
        screen.getByLabelText(
          "What would you like to research?"
        );

      await user.type(
        textarea,
        "Explain RAG."
      );

      await user.click(
        screen.getByRole(
          "button",
          {
            name:
              "Start Deep Research",
          }
        )
      );

      expect(
        await screen.findByRole(
          "heading",
          {
            name:
              "Research Report",
          }
        )
      ).toBeInTheDocument();

      expect(
        screen.getByText(
          "Explain RAG.",
          {
            selector:
              "blockquote",
          }
        )
      ).toBeInTheDocument();

      await user.click(
        screen.getByRole(
          "tab",
          {
            name:
              "Final Report",
          }
        )
      );

      expect(
        await screen.findByText(
          "RAG combines retrieval with generation to produce grounded responses."
        )
      ).toBeInTheDocument();
    }
  );


  it(
    "keeps document upload inside the research task card",
    async () => {
      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });

      renderHome();

      expect(
        screen.getByLabelText(
          "What would you like to research?"
        )
      ).toBeInTheDocument();

      expect(
        screen.getByLabelText(
          "Document file"
        )
      ).toBeInTheDocument();

      expect(
        screen.getByRole(
          "button",
          {
            name: "Start Deep Research",
          }
        )
      ).toBeInTheDocument();
    }
  );


  it(
    "keeps the product identity and copyright footer accessible",
    () => {
      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });

      renderHome();

      expect(
        screen.getByRole("heading", {
          name: "DeepResearch AI",
        })
      ).toBeInTheDocument();

      expect(
        screen.getByRole("contentinfo")
      ).toHaveTextContent(
        "© 2026 Shantanu Chattopadhyay"
      );
    }
  );


  it(
    "rejects unsupported documents with an accessible error",
    async () => {
      const user = userEvent.setup({
        applyAccept: false,
      });

      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });

      renderHome();

      await user.upload(
        screen.getByLabelText("Document file"),
        new File(["not supported"], "evidence.exe", {
          type: "application/octet-stream",
        })
      );

      expect(
        await screen.findByRole("alert")
      ).toHaveTextContent(
        "Unsupported file type"
      );
      expect(mockedUploadDocument).not.toHaveBeenCalled();
    }
  );


  it(
    "prevents duplicate research submissions while running",
    async () => {
      const user = userEvent.setup();
      let finishResearch: (
        response: {
          question: string;
          research_brief: string;
          critical_analysis: string;
          insights: string;
          final_report: string;
          sources: [];
        }
      ) => void = () => {};

      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });
      mockedRunResearch.mockReturnValue(
        new Promise((resolve) => {
          finishResearch = resolve;
        })
      );

      renderHome();

      await user.type(
        screen.getByLabelText(
          "What would you like to research?"
        ),
        "Explain RAG."
      );

      const researchButton = screen.getByRole(
        "button",
        { name: "Start Deep Research" }
      );

      await user.click(researchButton);
      expect(researchButton).toBeDisabled();
      expect(mockedRunResearch).toHaveBeenCalledTimes(1);

      await user.click(researchButton);
      expect(mockedRunResearch).toHaveBeenCalledTimes(1);

      finishResearch({
        question: "Explain RAG.",
        research_brief: "RAG brief",
        critical_analysis: "RAG analysis",
        insights: "RAG insights",
        final_report: "RAG report",
        sources: [],
      });
    }
  );


  it(
    "does not submit research while document indexing is active",
    async () => {
      const user = userEvent.setup();
      let finishUpload: (
        response: {
          status: string;
          document_id: string;
          filename: string;
          file_type: string;
          sections: number;
          chunks: number;
        }
      ) => void = () => {};

      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });
      mockedUploadDocument.mockReturnValue(
        new Promise((resolve) => {
          finishUpload = resolve;
        })
      );

      renderHome();

      await user.type(
        screen.getByLabelText(
          "What would you like to research?"
        ),
        "Explain RAG."
      );

      const file = new File(
        ["RAG evidence"],
        "evidence.txt",
        { type: "text/plain" }
      );

      await user.upload(
        screen.getByLabelText("Document file"),
        file
      );
      await user.click(
        screen.getByRole(
          "button",
          { name: "Upload and index" }
        )
      );

      const researchButton = screen.getByRole(
        "button",
        { name: "Start Deep Research" }
      );

      expect(researchButton).toBeDisabled();

      expect(mockedRunResearch).not.toHaveBeenCalled();

      finishUpload({
        status: "ok",
        document_id: "doc-1",
        filename: "evidence.txt",
        file_type: "text/plain",
        sections: 1,
        chunks: 1,
      });

      await waitFor(() => {
        expect(
          screen.getByRole(
            "button",
            { name: "Start Deep Research" }
          )
        ).not.toBeDisabled();
      });
    }
  );


  it(
    "shows a quota message when Gemini free-tier quota is exhausted",
    async () => {
      const user =
        userEvent.setup();

      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });

      mockedRunResearch.mockRejectedValue(
        new Error(
          "Gemini free-tier quota has been reached. Please try again later."
        )
      );

      renderHome();

      const textarea =
        screen.getByLabelText(
          "What would you like to research?"
        );

      await user.type(
        textarea,
        "What are the benefits of AI agents?"
      );

      await user.click(
        screen.getByRole(
          "button",
          {
            name:
              "Start Deep Research",
          }
        )
      );

      expect(
        await screen.findByRole(
          "alert"
        )
      ).toHaveTextContent(
        "Gemini free-tier quota has been reached. Please try again later."
      );
    }
  );


  it(
    "shows validated research sources in the Sources tab",
    async () => {
      const user =
        userEvent.setup();

      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });

      mockedRunResearch.mockResolvedValue({
        question:
          "How are AI agents used in healthcare?",

        research_brief:
          "AI agents can support healthcare workflows [S1].",

        critical_analysis:
          "Healthcare AI requires careful validation.",

        insights:
          "Agentic systems may improve workflow efficiency.",

        final_report:
          "AI agents have several healthcare applications.",

        sources: [
          {
            id: "source-1",

            citation_id: "S1",

            title:
              "AI Agents in Healthcare",

            url:
              "https://www.ibm.com/think/topics/ai-agents-healthcare",

            domain: "ibm.com",

            source_type: "web",

            provider: "tavily",

            snippet:
              "AI agents can support healthcare workflows.",

            content:
              "AI agents can support healthcare workflows.",

            authors: [],

            published_date: null,

            relevance_score: 0.82,

            credibility: "medium",

            validation_status:
              "accepted",

            validation_notes: [
              (
                "Vendor-authored source; "
                + "useful for industry perspective."
              ),
            ],
          },
        ],
      });

      renderHome();

      const textarea =
        screen.getByLabelText(
          "What would you like to research?"
        );

      await user.type(
        textarea,
        "How are AI agents used in healthcare?"
      );

      await user.click(
        screen.getByRole(
          "button",
          {
            name:
              "Start Deep Research",
          }
        )
      );

      expect(
        await screen.findByRole(
          "heading",
          {
            name:
              "Research Report",
          }
        )
      ).toBeInTheDocument();

      await user.click(
        screen.getByRole(
          "tab",
          {
            name: "Sources",
          }
        )
      );

      expect(
        screen.getByRole(
          "heading",
          {
            name:
              "Sources & Evidence",
          }
        )
      ).toBeInTheDocument();

      expect(
        screen.getByRole(
          "heading",
          {
            name:
              "AI Agents in Healthcare",
            level: 4,
          }
        )
      ).toBeInTheDocument();

      expect(
        screen.getByText(
          "[S1]"
        )
      ).toBeInTheDocument();

      expect(
        screen.getByText(
          "ibm.com"
        )
      ).toBeInTheDocument();

      expect(
        screen.getByText(
          "Credibility: Medium"
        )
      ).toBeInTheDocument();

      expect(
        screen.getByText(
          "Relevance: 82%"
        )
      ).toBeInTheDocument();

      const sourceLink =
        screen.getByRole(
          "link",
          {
            name:
              /Open Source/i,
          }
        );

      expect(
        sourceLink
      ).toHaveAttribute(
        "href",
        "https://www.ibm.com/think/topics/ai-agents-healthcare"
      );

      expect(
        sourceLink
      ).toHaveAttribute(
        "target",
        "_blank"
      );
    }
  );


  it(
    "opens the Sources tab and focuses the matching source when a citation is clicked",
    async () => {
      const user =
        userEvent.setup();

      mockedGetHealth.mockResolvedValue({
        status: "ok",
        service: "deep-research-api",
      });

      mockedRunResearch.mockResolvedValue({
        question:
          "How are AI agents used in healthcare?",

        research_brief:
          "AI agents can support healthcare workflows [S1].",

        critical_analysis:
          "Healthcare AI requires careful validation.",

        insights:
          "Agentic systems may improve workflow efficiency.",

        final_report:
          "AI agents may improve healthcare workflows [S1].",

        sources: [
          {
            id: "source-1",

            citation_id: "S1",

            title:
              "Healthcare AI Agent Research",

            url:
              "https://example.com/healthcare-ai-agents",

            domain:
              "example.com",

            source_type:
              "web",

            provider:
              "tavily",

            snippet:
              "Evidence about healthcare AI agents.",

            content:
              "Evidence about healthcare AI agents.",

            authors: [],

            published_date:
              null,

            relevance_score:
              0.91,

            credibility:
              "medium",

            validation_status:
              "accepted",

            validation_notes: [],
          },
        ],
      });

      renderHome();

      const textarea =
        screen.getByLabelText(
          "What would you like to research?"
        );

      await user.type(
        textarea,
        "How are AI agents used in healthcare?"
      );

      await user.click(
        screen.getByRole(
          "button",
          {
            name:
              "Start Deep Research",
          }
        )
      );

      expect(
        await screen.findByRole(
          "heading",
          {
            name:
              "Research Report",
          }
        )
      ).toBeInTheDocument();

      const citationButton =
        screen.getByRole(
          "button",
          {
            name:
              "View source S1",
          }
        );

      expect(
        citationButton
      ).toHaveTextContent(
        "[S1]"
      );

      await user.click(
        citationButton
      );

      const sourcesTab =
        screen.getByRole(
          "tab",
          {
            name: "Sources",
          }
        );

      expect(
        sourcesTab
      ).toHaveAttribute(
        "aria-selected",
        "true"
      );

      expect(
        await screen.findByRole(
          "heading",
          {
            name:
              "Sources & Evidence",
          }
        )
      ).toBeInTheDocument();

      expect(
        screen.getByRole(
          "heading",
          {
            name:
              "Healthcare AI Agent Research",
            level: 4,
          }
        )
      ).toBeInTheDocument();

      const sourceCard =
        document.getElementById(
          "source-S1"
        );

      expect(
        sourceCard
      ).not.toBeNull();

      await waitFor(() => {
        expect(
          sourceCard
        ).toHaveFocus();
      });
    }
  );
});