import { apiClient } from './client';
import { Project, ProjectPaper } from './types';

export const projectsApi = {
  // List all projects
  list: async (): Promise<Project[]> => {
    const response = await apiClient.get('/projects/');
    return response.data;
  },

  // Get project detail
  get: async (id: number): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}/`);
    return response.data;
  },

  // Create project
  create: async (data: {
    name: string;
    description?: string;
    tags?: string[];
  }): Promise<Project> => {
    const response = await apiClient.post('/projects/', data);
    return response.data;
  },

  // Update project
  update: async (
    id: number,
    data: Partial<Project>
  ): Promise<Project> => {
    const response = await apiClient.put(`/projects/${id}/`, data);
    return response.data;
  },

  // Delete project
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/projects/${id}/`);
  },

  // Add paper to project
  addPaper: async (
    projectId: number,
    paperId: number,
    notes?: string,
    tags?: string[],
    importance?: number
  ): Promise<ProjectPaper> => {
    const response = await apiClient.post(
      `/projects/${projectId}/add_paper/`,
      {
        paper_id: paperId,
        notes,
        tags,
        importance,
      }
    );
    return response.data;
  },

  // Remove paper from project
  removePaper: async (projectId: number, paperId: number): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/papers/${paperId}/`);
  },

  // Get project papers
  getPapers: async (projectId: number): Promise<ProjectPaper[]> => {
    const response = await apiClient.get(`/projects/${projectId}/papers/`);
    return response.data;
  },
};
