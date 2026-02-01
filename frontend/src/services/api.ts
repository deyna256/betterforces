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

// Retry with exponential backoff for rate limit errors
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  initialDelay = 2000
): Promise<T> {
  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 429) {
        lastError = new Error(
          'Service is temporarily overloaded. Please wait a moment and try again.'
        );

        // If not last attempt, wait and retry
        if (attempt < maxRetries) {
          const delay = initialDelay * Math.pow(2, attempt); // 2s, 4s, 8s
          console.log(`Rate limited (429), retrying in ${delay / 1000}s...`);
          await new Promise((resolve) => setTimeout(resolve, delay));
          continue;
        }
      }
      throw error;
    }
  }

  throw lastError || new Error('Max retries exceeded');
}

// Wrapper for API calls with polling support
async function fetchWithPolling<T>(
  endpoint: string,
  preferFresh = false
): Promise<{ data: T; metadata: DataMetadata }> {
  return retryWithBackoff(async () => {
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
        if (axiosError.response?.status === 429) {
          // Let retryWithBackoff handle this
          throw error;
        }
        if (axiosError.response?.status === 503) {
          throw new Error('Service temporarily unavailable. Please try again later.');
        }
        // Generic error with user-friendly message
        throw new Error('Failed to load data. Please check the handle and try again.');
      }
      throw error;
    }
  });
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
