import { useState, useEffect } from 'react';
import { Header } from './components/layout/Header';
import { StatCard } from './components/layout/StatCard';
import { AbandonedProblemsChart } from './components/charts/AbandonedProblemsChart';
import { DifficultyDistributionChart } from './components/charts/DifficultyDistributionChart';
import { TagsChart } from './components/charts/TagsChart';
import { TagsRadarChart } from './components/charts/TagsRadarChart';
import { codeforcesApi } from './services/api';
import type {
  AbandonedProblemByTagsResponse,
  AbandonedProblemByRatingsResponse,
  DifficultyDistributionResponse,
  TagsResponse,
  WeakTagsResponse,
} from './types/api';

function App() {
  const [handle, setHandle] = useState<string>('tourist');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [abandonedByTags, setAbandonedByTags] = useState<AbandonedProblemByTagsResponse | null>(
    null
  );
  const [abandonedByRatings, setAbandonedByRatings] =
    useState<AbandonedProblemByRatingsResponse | null>(null);
  const [difficultyDist, setDifficultyDist] = useState<DifficultyDistributionResponse | null>(
    null
  );
  const [tagRatings, setTagRatings] = useState<TagsResponse | null>(null);
  const [weakTags, setWeakTags] = useState<WeakTagsResponse | null>(null);

  const fetchAllData = async (userHandle: string) => {
    setLoading(true);
    setError(null);

    try {
      const [abandonedTags, abandonedRatings, difficulty, tags, weak] = await Promise.all([
        codeforcesApi.getAbandonedProblemsByTags(userHandle),
        codeforcesApi.getAbandonedProblemsByRatings(userHandle),
        codeforcesApi.getDifficultyDistribution(userHandle),
        codeforcesApi.getTagRatings(userHandle),
        codeforcesApi.getWeakTagRatings(userHandle, 200),
      ]);

      setAbandonedByTags(abandonedTags);
      setAbandonedByRatings(abandonedRatings);
      setDifficultyDist(difficulty);
      setTagRatings(tags);
      setWeakTags(weak);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to fetch data. Please check the handle and try again.'
      );
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (handle) {
      fetchAllData(handle);
    }
  }, [handle]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header handle={handle} onHandleChange={setHandle} />

      <main className="container mx-auto px-4 py-8">
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-cf-blue mx-auto mb-4"></div>
              <p className="text-gray-600 text-lg">Loading analytics for {handle}...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-8">
            <h3 className="text-red-900 font-semibold text-lg mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {!loading && !error && difficultyDist && tagRatings && (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Solved"
                value={difficultyDist.total_solved}
                description="Unique problems"
                color="green"
              />
              <StatCard
                title="Overall Median Rating"
                value={Math.round(tagRatings.overall_median_rating)}
                description="Across all problems"
                color="blue"
              />
              <StatCard
                title="Abandoned Problems"
                value={abandonedByTags?.total_abandoned_problems || 0}
                description="Never solved after attempts"
                color="red"
              />
              <StatCard
                title="Weak Areas"
                value={weakTags?.weak_tags.length || 0}
                description="Tags needing practice"
                color="orange"
              />
            </div>

            {/* Difficulty Distribution */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <DifficultyDistributionChart
                ranges={difficultyDist.ranges}
                totalSolved={difficultyDist.total_solved}
              />
            </div>

            {/* Tag Ratings - Radar Chart */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <TagsRadarChart
                tags={tagRatings.tags}
                overallMedian={tagRatings.overall_median_rating}
                type="all"
              />
            </div>

            {/* Tag Ratings - Bar Chart */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <TagsChart
                tags={tagRatings.tags}
                overallMedian={tagRatings.overall_median_rating}
                type="all"
              />
            </div>

            {/* Weak Tags - Two Views */}
            {weakTags && weakTags.weak_tags.length > 0 && (
              <>
                <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                  <TagsRadarChart
                    tags={weakTags.weak_tags}
                    overallMedian={weakTags.overall_median_rating}
                    type="weak"
                  />
                </div>
                <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                  <TagsChart
                    tags={weakTags.weak_tags}
                    overallMedian={weakTags.overall_median_rating}
                    type="weak"
                  />
                </div>
              </>
            )}

            {/* Abandoned Problems by Tags */}
            {abandonedByTags && abandonedByTags.tags.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <AbandonedProblemsChart data={abandonedByTags.tags} type="tags" />
              </div>
            )}

            {/* Abandoned Problems by Ratings */}
            {abandonedByRatings && abandonedByRatings.ratings.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <AbandonedProblemsChart data={abandonedByRatings.ratings} type="ratings" />
              </div>
            )}
          </>
        )}
      </main>

      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-300">
            Built with React, TypeScript, and Chart.js | Data from Codeforces API
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
