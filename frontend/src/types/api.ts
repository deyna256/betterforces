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

export interface WeakTagsResponse {
  weak_tags: TagInfo[];
  overall_average_rating: number;
  overall_median_rating: number;
  total_solved: number;
  threshold_used: number;
  last_updated: string;
}
