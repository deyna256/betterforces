import axios, { AxiosError } from 'axios';
import type {
  AbandonedProblemByTagsResponse,
  AbandonedProblemByRatingsResponse,
  DifficultyDistributionResponse,
  TagsResponse,
  TaskResponse,
  TaskStatusResponse,
  DataMetadata,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to check if response is a task (202 status)
function isTaskResponse(data: unknown): data is TaskResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'status' in data &&
    (data as TaskResponse).status === 'processing' &&
    'task_id' in data
  );
}

// Poll task status with exponential backoff
async function pollTask<T>(taskId: string, maxAttempts = 30): Promise<T> {
  let attempt = 0;
  let delay = 2000; // Start with 2 seconds

  while (attempt < maxAttempts) {
    attempt++;

    // Wait before polling (except first attempt)
    if (attempt > 1) {
      await new Promise((resolve) => setTimeout(resolve, delay));
    }

    try {
      const response = await apiClient.get<TaskStatusResponse>(`/tasks/${taskId}`);

      if (response.status === 200) {
        // Task completed - fetch actual data
        // The task endpoint returns completion info, we need to make the actual request again
        return response.data as unknown as T;
      }

      // Still processing (202), continue polling
      if (response.status === 202) {
        // Exponential backoff: 2s, 3s, 4.5s, 6.75s, max 10s
        delay = Math.min(delay * 1.5, 10000);
        continue;
      }
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 500) {
        // Task failed
        const taskError = error.response.data as TaskStatusResponse;
        throw new Error(taskError.error || 'Task failed');
      }
      throw error;
    }
  }

  throw new Error('Polling timeout: Task took too long to complete');
}

// Wrapper for API calls with polling support
async function fetchWithPolling<T>(
  endpoint: string,
  preferFresh = false
): Promise<{ data: T; metadata: DataMetadata }> {
  try {
    const url = preferFresh ? `${endpoint}?prefer_fresh=true` : endpoint;
    const response = await apiClient.get<T | TaskResponse>(url);

    // Check if response is a task (202 Accepted)
    if (response.status === 202 && isTaskResponse(response.data)) {
      const taskData = response.data;

      // Poll until task completes
      await pollTask(taskData.task_id);

      // After task completes, fetch the actual data
      const dataResponse = await apiClient.get<T>(endpoint);

      // Extract metadata from headers
      const metadata: DataMetadata = {
        isStale: dataResponse.headers['x-data-stale'] === 'true',
        dataAge: dataResponse.headers['x-data-age']
          ? parseInt(dataResponse.headers['x-data-age'], 10)
          : undefined,
      };

      return { data: dataResponse.data, metadata };
    }

    // Regular response (200 OK)
    const metadata: DataMetadata = {
      isStale: response.headers['x-data-stale'] === 'true',
      dataAge: response.headers['x-data-age']
        ? parseInt(response.headers['x-data-age'], 10)
        : undefined,
    };

    return { data: response.data as T, metadata };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response?.status === 404) {
        throw new Error('User not found on Codeforces');
      }
      throw new Error(
        axiosError.response?.data
          ? JSON.stringify(axiosError.response.data)
          : axiosError.message
      );
    }
    throw error;
  }
}

export const codeforcesApi = {
  // Abandoned Problems
  getAbandonedProblemsByTags: async (handle: string, preferFresh = false) => {
    return fetchWithPolling<AbandonedProblemByTagsResponse>(
      `/abandoned-problems/by-tags/${handle}`,
      preferFresh
    );
  },

  getAbandonedProblemsByRatings: async (handle: string, preferFresh = false) => {
    return fetchWithPolling<AbandonedProblemByRatingsResponse>(
      `/abandoned-problems/by-ratings/${handle}`,
      preferFresh
    );
  },

  // Difficulty Distribution
  getDifficultyDistribution: async (handle: string, preferFresh = false) => {
    return fetchWithPolling<DifficultyDistributionResponse>(
      `/difficulty-distribution/${handle}`,
      preferFresh
    );
  },

  // Tags
  getTagRatings: async (handle: string, preferFresh = false) => {
    return fetchWithPolling<TagsResponse>(`/tag-ratings/${handle}`, preferFresh);
  },
};
