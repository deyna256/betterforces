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
  DataMetadata,
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

  // Metadata state
  const [dataMetadata, setDataMetadata] = useState<DataMetadata>({
    isStale: false,
  });

  const fetchAllData = async (userHandle: string, preferFresh = false) => {
    setLoading(true);
    setError(null);

    try {
      const [abandonedTagsRes, abandonedRatingsRes, difficultyRes, tagsRes] = await Promise.all([
        codeforcesApi.getAbandonedProblemsByTags(userHandle, preferFresh),
        codeforcesApi.getAbandonedProblemsByRatings(userHandle, preferFresh),
        codeforcesApi.getDifficultyDistribution(userHandle, preferFresh),
        codeforcesApi.getTagRatings(userHandle, preferFresh),
      ]);

      setAbandonedByTags(abandonedTagsRes.data);
      setAbandonedByRatings(abandonedRatingsRes.data);
      setDifficultyDist(difficultyRes.data);
      setTagRatings(tagsRes.data);

      // Use metadata from difficulty distribution (they should all be the same)
      setDataMetadata(difficultyRes.metadata);
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

  const handleRefresh = () => {
    if (handle) {
      fetchAllData(handle, true); // Force fresh data
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

        {/* Stale Data Warning */}
        {!loading && !error && dataMetadata.isStale && (
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6 mb-8 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <svg
                className="w-6 h-6 text-yellow-600"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <h3 className="text-yellow-900 font-semibold text-lg">Data May Be Outdated</h3>
                <p className="text-yellow-800">
                  This data is{' '}
                  {dataMetadata.dataAge
                    ? `${Math.floor(dataMetadata.dataAge / 3600)} hours old`
                    : 'older than 4 hours'}
                  . Fresh data is being fetched in the background.
                </p>
              </div>
            </div>
            <button
              onClick={handleRefresh}
              className="bg-yellow-600 hover:bg-yellow-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg whitespace-nowrap"
            >
              Refresh Now
            </button>
          </div>
        )}

        {!loading && !error && difficultyDist && tagRatings && (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
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
              <TagsRadarChart tags={tagRatings.tags} type="all" />
            </div>

            {/* Tag Ratings - Bar Chart */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <TagsChart
                tags={tagRatings.tags}
                overallMedian={tagRatings.overall_median_rating}
                type="all"
              />
            </div>

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
            <a
              href="https://github.com/deyna256/betterforces"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-cf-blue transition-colors underline"
            >
              GitHub
            </a>
            {' | Data from '}
            <a
              href="https://codeforces.com/apiHelp"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-cf-blue transition-colors underline"
            >
              Codeforces API
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
