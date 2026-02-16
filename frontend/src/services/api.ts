import axios, { AxiosError } from 'axios';
import type {
  AbandonedProblemByTagsResponse,
  AbandonedProblemByRatingsResponse,
  DailyActivityResponse,
  DifficultyDistributionResponse,
  TagsResponse,
  TaskResponse,
  TaskStatusResponse,
  DataMetadata,
  TimePeriod,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

function isTaskResponse(data: unknown): data is TaskResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'status' in data &&
    (data as TaskResponse).status === 'processing' &&
    'task_id' in data
  );
}

async function pollTask<T>(taskId: string, maxAttempts = 30): Promise<T> {
  let attempt = 0;
  let delay = 2000;

  while (attempt < maxAttempts) {
    attempt++;

    if (attempt > 1) {
      await new Promise((resolve) => setTimeout(resolve, delay));
    }

    try {
      const response = await apiClient.get<TaskStatusResponse>(`/tasks/${taskId}`);

      if (response.status === 200) {
        return response.data as unknown as T;
      }

      if (response.status === 202) {
        delay = Math.min(delay * 1.5, 10000);
        continue;
      }
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 500) {
        const taskError = error.response.data as TaskStatusResponse;
        throw new Error(taskError.error || 'Task failed');
      }
      throw error;
    }
  }

  throw new Error('Polling timeout: Task took too long to complete');
}

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

        if (attempt < maxRetries) {
          const delay = initialDelay * Math.pow(2, attempt);
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

async function fetchWithPolling<T>(
  endpoint: string,
  params: Record<string, string> = {}
): Promise<{ data: T; metadata: DataMetadata }> {
  return retryWithBackoff(async () => {
    try {
      const searchParams = new URLSearchParams(params);
      const queryString = searchParams.toString();
      const url = queryString ? `${endpoint}?${queryString}` : endpoint;
      const response = await apiClient.get<T | TaskResponse>(url);

      if (response.status === 202 && isTaskResponse(response.data)) {
        const taskData = response.data;

        await pollTask(taskData.task_id);

        const dataResponse = await apiClient.get<T>(endpoint);

        const metadata: DataMetadata = {
          isStale: dataResponse.headers['x-data-stale'] === 'true',
          dataAge: dataResponse.headers['x-data-age']
            ? parseInt(dataResponse.headers['x-data-age'], 10)
            : undefined,
        };

        return { data: dataResponse.data, metadata };
      }

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
          throw error;
        }
        if (axiosError.response?.status === 503) {
          throw new Error('Service temporarily unavailable. Please try again later.');
        }
        throw new Error('Failed to load data. Please check the handle and try again.');
      }
      throw error;
    }
  });
}

function buildParams(preferFresh: boolean, period: TimePeriod): Record<string, string> {
  const params: Record<string, string> = {};
  if (preferFresh) params['prefer_fresh'] = 'true';
  if (period !== 'all_time') params['period'] = period;
  return params;
}

export const codeforcesApi = {
  getAbandonedProblemsByTags: async (
    handle: string,
    preferFresh = false,
    period: TimePeriod = 'all_time'
  ) => {
    return fetchWithPolling<AbandonedProblemByTagsResponse>(
      `/abandoned-problems/by-tags/${handle}`,
      buildParams(preferFresh, period)
    );
  },

  getAbandonedProblemsByRatings: async (
    handle: string,
    preferFresh = false,
    period: TimePeriod = 'all_time'
  ) => {
    return fetchWithPolling<AbandonedProblemByRatingsResponse>(
      `/abandoned-problems/by-ratings/${handle}`,
      buildParams(preferFresh, period)
    );
  },

  getDifficultyDistribution: async (
    handle: string,
    preferFresh = false,
    period: TimePeriod = 'all_time'
  ) => {
    return fetchWithPolling<DifficultyDistributionResponse>(
      `/difficulty-distribution/${handle}`,
      buildParams(preferFresh, period)
    );
  },

  getDailyActivity: async (handle: string, preferFresh = false, period: TimePeriod = 'all_time') => {
    return fetchWithPolling<DailyActivityResponse>(
      `/daily-activity/${handle}`,
      buildParams(preferFresh, period)
    );
  },

  getTagRatings: async (handle: string, preferFresh = false, period: TimePeriod = 'all_time') => {
    return fetchWithPolling<TagsResponse>(`/tag-ratings/${handle}`, buildParams(preferFresh, period));
  },
};
