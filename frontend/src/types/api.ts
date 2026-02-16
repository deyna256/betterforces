export type TimePeriod = 'day' | 'week' | 'month' | 'half_year' | 'year' | 'all_time';

// API Response types based on backend schemas

export interface TagAbandoned {
  tag: string;
  problem_count: number;
  total_failed_attempts: number;
}

export interface RatingAbandoned {
  rating: number;
  problem_count: number;
  total_failed_attempts: number;
}

export interface AbandonedProblemByTagsResponse {
  tags: TagAbandoned[];
  total_abandoned_problems: number;
  last_updated: string;
}

export interface AbandonedProblemByRatingsResponse {
  ratings: RatingAbandoned[];
  total_abandoned_problems: number;
  last_updated: string;
}

export interface RatingRange {
  rating: number;
  problem_count: number;
}

export interface DifficultyDistributionResponse {
  ranges: RatingRange[];
  total_solved: number;
  last_updated: string;
}

export interface TagInfo {
  tag: string;
  average_rating: number;
  median_rating: number;
  problem_count: number;
}

export interface TagsResponse {
  tags: TagInfo[];
  overall_average_rating: number;
  overall_median_rating: number;
  total_solved: number;
  last_updated: string;
}

export interface DailyActivityItem {
  date: string;
  solved_count: number;
  attempt_count: number;
}

export interface DailyActivityResponse {
  days: DailyActivityItem[];
  total_solved: number;
  total_attempts: number;
  active_days: number;
  last_updated: string;
}

// Task polling types
export interface TaskResponse {
  status: 'processing';
  task_id: string;
  retry_after: number;
}

export interface TaskStatusResponse {
  status: 'processing' | 'completed' | 'failed';
  handle?: string;
  submission_count?: number;
  message?: string;
  error?: string;
}

// Metadata for stale data
export interface DataMetadata {
  isStale: boolean;
  dataAge?: number; // Age in seconds
}

