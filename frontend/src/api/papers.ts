import { apiClient } from './client';
import type { Paper, SearchRequest, SearchResponse } from './types';

export const papersApi = {
  // Search papers
  search: async (data: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post('/papers/search/', data);
    return response.data;
  },

  // List all papers
  list: async (page = 1): Promise<{ results: Paper[]; count: number }> => {
    const response = await apiClient.get(`/papers/?page=${page}`);
    return response.data;
  },

  // Get paper detail
  get: async (id: number): Promise<Paper> => {
    const response = await apiClient.get(`/papers/${id}/`);
    return response.data;
  },

  // Summarize paper
  summarize: async (
    id: number,
    level: string = 'medium',
    usePdf: boolean = false
  ): Promise<{ summary: string; level: string; source: string }> => {
    const response = await apiClient.post(`/papers/${id}/summarize/`, {
      level,
      use_pdf: usePdf,
    });
    return response.data;
  },

  // Analyze paper (extract gaps and findings)
  analyze: async (
    id: number
  ): Promise<{
    methodology_gaps: string;
    knowledge_gaps: string;
    future_directions: string;
    key_findings: string;
  }> => {
    const response = await apiClient.post(`/papers/${id}/analyze/`);
    return response.data;
  },

  // Download PDF
  downloadPdf: async (
    id: number
  ): Promise<{ success: boolean; text_length: number }> => {
    const response = await apiClient.post(`/papers/${id}/download_pdf/`);
    return response.data;
  },
};
