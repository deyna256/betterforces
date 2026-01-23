import axios from 'axios';
import type {
  AbandonedProblemByTagsResponse,
  AbandonedProblemByRatingsResponse,
  DifficultyDistributionResponse,
  TagsResponse,
  WeakTagsResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const codeforcesApi = {
  // Abandoned Problems
  getAbandonedProblemsByTags: async (handle: string) => {
    const response = await apiClient.get<AbandonedProblemByTagsResponse>(
      `/abandoned-problems/by-tags/${handle}`
    );
    return response.data;
  },

  getAbandonedProblemsByRatings: async (handle: string) => {
    const response = await apiClient.get<AbandonedProblemByRatingsResponse>(
      `/abandoned-problems/by-ratings/${handle}`
    );
    return response.data;
  },

  // Difficulty Distribution
  getDifficultyDistribution: async (handle: string) => {
    const response = await apiClient.get<DifficultyDistributionResponse>(
      `/difficulty-distribution/${handle}`
    );
    return response.data;
  },

  // Tags
  getTagRatings: async (handle: string) => {
    const response = await apiClient.get<TagsResponse>(`/tag-ratings/${handle}`);
    return response.data;
  },

  getWeakTagRatings: async (handle: string, threshold: number = 200) => {
    const response = await apiClient.get<WeakTagsResponse>(
      `/tag-ratings/${handle}/weak`,
      { params: { threshold } }
    );
    return response.data;
  },
};
