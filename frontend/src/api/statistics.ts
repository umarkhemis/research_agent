import { apiClient } from './client';
import { DashboardStats } from './types';

export const statisticsApi = {
  // Get dashboard statistics
  getDashboard: async (): Promise<DashboardStats> => {
    const response = await apiClient.get('/statistics/dashboard/');
    return response.data;
  },
};
