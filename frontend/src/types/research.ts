export type ResearchResponse = {
  question: string;
  research_brief: string;
  critical_analysis: string;
  insights: string;
  final_report: string;
};


export type ResearchStageId =
  | "retrieving-sources"
  | "researching"
  | "critical-analysis"
  | "generating-insights"
  | "building-report";


export type ResearchStageStatus =
  | "waiting"
  | "active"
  | "completed"
  | "error";


export type ResearchStage = {
  id: ResearchStageId;
  label: string;
  description: string;
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