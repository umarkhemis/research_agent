// API Types
export interface Project {
  id: number;
  name: string;
  description?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  papers_count: number;
}

export interface Paper {
  id: number;
  title: string;
  doi?: string;
  arxiv_id?: string;
  semantic_scholar_id?: string;
  url?: string;
  abstract?: string;
  authors: string[];
  year?: number;
  venue?: string;
  publication_date?: string;
  citation_count: number;
  has_pdf: boolean;
  pdf_url?: string;
  pdf_text?: string;
  abstract_summary_short?: string;
  abstract_summary_medium?: string;
  abstract_summary_long?: string;
  pdf_summary_short?: string;
  pdf_summary_medium?: string;
  pdf_summary_long?: string;
  key_findings?: string;
  methodology_gaps?: string;
  knowledge_gaps?: string;
  future_directions?: string;
  source?: string;
  processing_status: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ProjectPaper {
  id: number;
  project: number;
  paper: Paper;
  notes?: string;
  tags: string[];
  importance: number;
  added_at: string;
}

export interface SearchHistory {
  id: number;
  query: string;
  project?: number;
  limit?: number;
  summary_level?: string;
  year_from?: number;
  year_to?: number;
  open_access_only: boolean;
  databases: string[];
  results_count?: number;
  papers_found: number[];
  search_duration_seconds?: number;
  created_at: string;
}

export interface ProjectNote {
  id: number;
  project: number;
  title?: string;
  content: string;
  note_type?: string;
  created_at: string;
  updated_at: string;
}

export interface LiteratureReview {
  id: number;
  project?: number;
  title?: string;
  content: string;
  papers_included: number[];
  review_type?: string;
  detail_level?: string;
  markdown_content?: string;
  latex_content?: string;
  created_at: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  year_from?: number;
  year_to?: number;
  open_access_only?: boolean;
  databases?: string[];
  summary_level?: string;
  project_id?: number;
}

export interface SearchResponse {
  papers: Paper[];
  count: number;
  search_id: number;
  duration: number;
}

export interface LiteratureReviewRequest {
  project_id?: number;
  paper_ids?: number[];
  review_type: string;
  detail_level: string;
  custom_instructions?: string;
}

export interface DashboardStats {
  counts: {
    projects: number;
    papers: number;
    searches: number;
    reviews: number;
  };
  recent: {
    projects: Project[];
    papers: Paper[];
    searches: SearchHistory[];
  };
}
