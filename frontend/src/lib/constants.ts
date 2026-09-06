import type {
  ResearchStage,
  ResearchTab,
} from "@/types/research";


export const APP_NAME = "DeepResearch AI";

export const APP_TAGLINE =
  "AI Research & Intelligence Platform";

export const APP_DESCRIPTION =
  "DeepResearch AI researches, analyzes, challenges, and synthesizes information into structured intelligence reports.";


export const EXAMPLE_RESEARCH_QUESTIONS = [
  {
    label: "AI Agents in Healthcare",
    question:
      "What are the main benefits and risks of using AI agents in healthcare?",
  },
  {
    label: "Future of Generative AI",
    question:
      "What are the most important trends shaping the future of generative AI?",
  },
  {
    label: "Renewable Energy Trends",
    question:
      "What are the major global trends in renewable energy adoption?",
  },
  {
    label: "AI in Financial Services",
    question:
      "How are AI agents changing financial services, and what risks do they introduce?",
  },
] as const;


export const RESEARCH_PIPELINE_STAGES: ResearchStage[] = [
  {
    id: "retrieving-sources",
    label: "Retrieving Sources",
    description:
      "Finding relevant sources and evidence for the research question.",
  },
  {
    id: "researching",
    label: "Researching",
    description:
      "Building the initial research brief and identifying important concepts.",
  },
  {
    id: "critical-analysis",
    label: "Critical Analysis",
    description:
      "Examining assumptions, weaknesses, risks, and missing perspectives.",
  },
  {
    id: "generating-insights",
    label: "Generating Insights",
    description:
      "Synthesizing patterns, trends, implications, and unanswered questions.",
  },
  {
    id: "building-report",
    label: "Building Report",
    description:
      "Combining the research into a structured final intelligence report.",
  },
];


export const RESEARCH_TABS: ResearchTab[] = [
  {
    id: "overview",
    label: "Overview",
  },
  {
    id: "research-brief",
    label: "Research Brief",
  },
  {
    id: "critical-analysis",
    label: "Critical Analysis",
  },
  {
    id: "insights",
    label: "Insights",
  },
  {
    id: "final-report",
    label: "Final Report",
  },
  {
    id: "sources",
    label: "Sources",
  },
];