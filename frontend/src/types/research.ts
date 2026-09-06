export type SourceType =
  | "web"
  | "news"
  | "paper"
  | "report"
  | "documentation"
  | "unknown";


export type SourceProvider =
  | "tavily"
  | "arxiv"
  | "manual";


export type CredibilityLevel =
  | "high"
  | "medium"
  | "low"
  | "unrated";


export type ValidationStatus =
  | "unreviewed"
  | "accepted"
  | "needs-review"
  | "rejected";


export type ResearchSource = {
  id: string;

  citation_id: string | null;

  title: string;

  url: string;

  domain: string;

  source_type: SourceType;

  provider: SourceProvider;

  snippet: string;

  content: string;

  authors: string[];

  published_date: string | null;

  relevance_score: number;

  credibility: CredibilityLevel;

  validation_status: ValidationStatus;

  validation_notes: string[];
};


export type ResearchResponse = {
  question: string;

  research_brief: string;

  critical_analysis: string;

  insights: string;

  final_report: string;

  sources: ResearchSource[];
};


export type ResearchTabId =
  | "overview"
  | "research-brief"
  | "critical-analysis"
  | "insights"
  | "final-report"
  | "sources";


export type ResearchTab = {
  id: ResearchTabId;

  label: string;
};


export type ResearchStage = {
  id: string;

  label: string;

  description: string;
};