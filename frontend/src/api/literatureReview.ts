import { apiClient } from './client';
import { LiteratureReview, LiteratureReviewRequest } from './types';

export const literatureReviewApi = {
  // Generate literature review
  generate: async (
    data: LiteratureReviewRequest
  ): Promise<LiteratureReview> => {
    const response = await apiClient.post(
      '/literature-reviews/generate/',
      data
    );
    return response.data;
  },

  // Get literature review
  get: async (id: number): Promise<LiteratureReview> => {
    const response = await apiClient.get(`/literature-reviews/${id}/`);
    return response.data;
  },

  // List literature reviews
  list: async (): Promise<LiteratureReview[]> => {
    const response = await apiClient.get('/literature-reviews/');
    return response.data;
  },

  // Export review
  export: async (
    reviewId: number,
    format: string
  ): Promise<{ content: string; format: string; title: string }> => {
    const response = await apiClient.post('/export/review/', {
      review_id: reviewId,
      format,
    });
    return response.data;
  },
};
