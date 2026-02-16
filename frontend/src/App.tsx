import { useState } from 'react';
import { Header } from './components/layout/Header';
import { MetricCard } from './components/layout/MetricCard';
import { StatCard } from './components/layout/StatCard';
import { AbandonedProblemsChart } from './components/charts/AbandonedProblemsChart';
import { DailyActivityChart } from './components/charts/DailyActivityChart';
import { DifficultyDistributionChart } from './components/charts/DifficultyDistributionChart';
import { TagsChart } from './components/charts/TagsChart';
import { TagsRadarChart } from './components/charts/TagsRadarChart';
import { codeforcesApi } from './services/api';
import { useTheme } from './hooks/useTheme';
import { useMetricData } from './hooks/useMetricData';

function App() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  const [handle, setHandle] = useState<string>('tourist');

  const dailyActivity = useMetricData(handle, codeforcesApi.getDailyActivity);
  const difficulty = useMetricData(handle, codeforcesApi.getDifficultyDistribution);
  const tagRatingsRadar = useMetricData(handle, codeforcesApi.getTagRatings);
  const tagRatingsBar = useMetricData(handle, codeforcesApi.getTagRatings);
  const abandonedTags = useMetricData(handle, codeforcesApi.getAbandonedProblemsByTags);
  const abandonedRatings = useMetricData(handle, codeforcesApi.getAbandonedProblemsByRatings);

  const initialLoading =
    !difficulty.data && !tagRatingsRadar.data && (difficulty.loading || tagRatingsRadar.loading);

  const error =
    dailyActivity.error || difficulty.error || tagRatingsRadar.error || tagRatingsBar.error || abandonedTags.error || abandonedRatings.error;

  const staleMetadata =
    [dailyActivity, difficulty, tagRatingsRadar, tagRatingsBar, abandonedTags, abandonedRatings].find(
      (m) => m.metadata.isStale
    )?.metadata ?? null;

  const handleRefresh = () => {
    dailyActivity.refresh();
    difficulty.refresh();
    tagRatingsRadar.refresh();
    tagRatingsBar.refresh();
    abandonedTags.refresh();
    abandonedRatings.refresh();
  };

  const handleRetry = () => {
    dailyActivity.refresh();
    difficulty.refresh();
    tagRatingsRadar.refresh();
    tagRatingsBar.refresh();
    abandonedTags.refresh();
    abandonedRatings.refresh();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header handle={handle} onHandleChange={setHandle} theme={theme} onToggleTheme={toggleTheme} />

      <main className="container mx-auto px-4 py-8">
        {initialLoading && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-cf-blue mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400 text-lg">Loading analytics for {handle}...</p>
            </div>
          </div>
        )}

        {error && !initialLoading && (
          <div className="bg-red-50 dark:bg-red-900/30 border-2 border-red-200 dark:border-red-800 rounded-lg p-6 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-red-900 dark:text-red-300 font-semibold text-lg mb-2">Error</h3>
                <p className="text-red-700 dark:text-red-400 mb-4">{error}</p>
                <button
                  onClick={handleRetry}
                  className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {!initialLoading && !error && staleMetadata && (
          <div className="bg-yellow-50 dark:bg-yellow-900/30 border-2 border-yellow-300 dark:border-yellow-700 rounded-lg p-6 mb-8 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <svg
                className="w-6 h-6 text-yellow-600 dark:text-yellow-400"
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
                <h3 className="text-yellow-900 dark:text-yellow-300 font-semibold text-lg">Data May Be Outdated</h3>
                <p className="text-yellow-800 dark:text-yellow-400">
                  This data is{' '}
                  {staleMetadata.dataAge
                    ? `${Math.floor(staleMetadata.dataAge / 3600)} hours old`
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

        {!initialLoading && !error && difficulty.data && tagRatingsRadar.data && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
              <StatCard
                title="Total Solved"
                value={difficulty.allTimeData?.total_solved ?? difficulty.data.total_solved}
                description="Unique problems"
                color="green"
              />
              <StatCard
                title="Overall Median Rating"
                value={Math.round(
                  tagRatingsRadar.allTimeData?.overall_median_rating ??
                    tagRatingsRadar.data.overall_median_rating
                )}
                description="Across all problems"
                color="blue"
              />
              <StatCard
                title="Abandoned Problems"
                value={abandonedTags.allTimeData?.total_abandoned_problems ?? abandonedTags.data?.total_abandoned_problems ?? 0}
                description="Never solved after attempts"
                color="red"
              />
            </div>

            {dailyActivity.data && (
              <MetricCard
                title="Daily Activity"
                period={dailyActivity.period}
                onPeriodChange={dailyActivity.setPeriod}
                loading={dailyActivity.loading}
                emptyMessage={dailyActivity.data.days.length === 0 ? 'No submissions found for this period.' : undefined}
              >
                <DailyActivityChart days={dailyActivity.data.days} isDark={isDark} />
              </MetricCard>
            )}

            <MetricCard
              title="Difficulty Distribution"
              period={difficulty.period}
              onPeriodChange={difficulty.setPeriod}
              loading={difficulty.loading}
              emptyMessage={
                difficulty.data.ranges.length === 0
                  ? 'No solved problems for this period.'
                  : undefined
              }
            >
              <DifficultyDistributionChart
                ranges={difficulty.data.ranges}
                totalSolved={difficulty.data.total_solved}
                isDark={isDark}
              />
            </MetricCard>

            <MetricCard
              title="Tag Ratings — Radar"
              period={tagRatingsRadar.period}
              onPeriodChange={tagRatingsRadar.setPeriod}
              loading={tagRatingsRadar.loading}
              emptyMessage={
                tagRatingsRadar.data.tags.length === 0
                  ? 'No submissions found for this period.'
                  : tagRatingsRadar.data.tags.length < 3
                    ? 'Not enough data to build a radar chart (need at least 3 tags).'
                    : undefined
              }
            >
              <TagsRadarChart tags={tagRatingsRadar.data.tags} type="all" isDark={isDark} />
            </MetricCard>

            <MetricCard
              title="Tag Ratings — Bar"
              period={tagRatingsBar.period}
              onPeriodChange={tagRatingsBar.setPeriod}
              loading={tagRatingsBar.loading}
              emptyMessage={
                tagRatingsBar.data
                  ? tagRatingsBar.data.tags.length === 0
                    ? 'No submissions found for this period.'
                    : undefined
                  : 'No submissions found for this period.'
              }
            >
              {tagRatingsBar.data && (
                <TagsChart
                  tags={tagRatingsBar.data.tags}
                  overallMedian={tagRatingsBar.data.overall_median_rating}
                  type="all"
                  isDark={isDark}
                />
              )}
            </MetricCard>

            {abandonedTags.data && (
              <MetricCard
                title="Abandoned Problems by Tags"
                period={abandonedTags.period}
                onPeriodChange={abandonedTags.setPeriod}
                loading={abandonedTags.loading}
                emptyMessage={abandonedTags.data.tags.length === 0 ? 'No abandoned problems for this period.' : undefined}
              >
                <AbandonedProblemsChart data={abandonedTags.data.tags} type="tags" isDark={isDark} />
              </MetricCard>
            )}

            {abandonedRatings.data && (
              <MetricCard
                title="Abandoned Problems by Ratings"
                period={abandonedRatings.period}
                onPeriodChange={abandonedRatings.setPeriod}
                loading={abandonedRatings.loading}
                emptyMessage={abandonedRatings.data.ratings.length === 0 ? 'No abandoned problems for this period.' : undefined}
              >
                <AbandonedProblemsChart data={abandonedRatings.data.ratings} type="ratings" isDark={isDark} />
              </MetricCard>
            )}
          </>
        )}
      </main>

      <footer className="bg-gray-800 dark:bg-gray-950 text-white py-6 mt-12">
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
