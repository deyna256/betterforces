import { useState } from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import type { TagInfo } from '../../types/api';

const STANDARD_TAGS = [
  'implementation', 'math', 'greedy', 'dp', 'data structures',
  'brute force', 'constructive algorithms', 'sortings', 'binary search',
  'graphs', 'dfs and similar', 'strings', 'number theory',
  'geometry', 'trees',
];

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface TagsRadarChartProps {
  tags: TagInfo[];
  type: 'all';
  isDark?: boolean;
}

type RadarMode = 'personal' | 'standard';

export function TagsRadarChart({ tags, type, isDark = false }: TagsRadarChartProps) {
  const [mode, setMode] = useState<RadarMode>('personal');

  const tagMap = new Map(tags.map((t) => [t.tag, t]));

  const displayTags: TagInfo[] =
    mode === 'standard'
      ? STANDARD_TAGS.map(
          (name) => tagMap.get(name) ?? { tag: name, average_rating: 0, median_rating: 0, problem_count: 0 },
        )
      : type === 'all'
        ? [...tags].sort((a, b) => b.problem_count - a.problem_count).slice(0, 10)
        : [...tags].slice(0, 10);

  const labels = displayTags.map((tag) => tag.tag);
  const medianRatings = displayTags.map((tag) => tag.median_rating);
  const averageRatings = displayTags.map((tag) => tag.average_rating);

  const textColor = isDark ? '#e5e7eb' : '#374151';
  const gridColor = isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)';

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Median Rating',
        data: medianRatings,
        backgroundColor: 'rgba(26, 115, 232, 0.2)',
        borderColor: 'rgba(26, 115, 232, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(26, 115, 232, 1)',
        pointBorderColor: isDark ? '#1f2937' : '#fff',
        pointHoverBackgroundColor: isDark ? '#1f2937' : '#fff',
        pointHoverBorderColor: 'rgba(26, 115, 232, 1)',
      },
      {
        label: 'Average Rating',
        data: averageRatings,
        backgroundColor: 'rgba(0, 200, 83, 0.2)',
        borderColor: 'rgba(0, 200, 83, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(0, 200, 83, 1)',
        pointBorderColor: isDark ? '#1f2937' : '#fff',
        pointHoverBackgroundColor: isDark ? '#1f2937' : '#fff',
        pointHoverBorderColor: 'rgba(0, 200, 83, 1)',
      },
    ],
  };

  const options: ChartOptions<'radar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: textColor },
      },
      title: {
        display: true,
        text:
          type === 'all'
            ? mode === 'standard'
              ? 'Tag Performance Radar (Standard)'
              : 'Tag Performance Radar (Top 10)'
            : 'Weak Tags Radar',
        color: textColor,
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            const index = context.dataIndex;
            const tag = displayTags[index];
            return `Problems: ${tag.problem_count}`;
          },
        },
      },
    },
    scales: {
      r: {
        min: 0,
        max: 3000,
        ticks: {
          stepSize: 500,
          color: textColor,
          backdropColor: isDark ? '#1f2937' : '#fff',
        },
        grid: { color: gridColor },
        angleLines: { color: gridColor },
        pointLabels: { color: textColor },
      },
    },
  };

  return (
    <div className="w-full">
      {type === 'all' && (
        <div className="mb-2 flex justify-center gap-1">
          <button
            onClick={() => setMode('personal')}
            className={`rounded-l-md px-3 py-1 text-sm font-medium transition-colors ${
              mode === 'personal'
                ? 'bg-blue-600 text-white'
                : isDark
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            Personal
          </button>
          <button
            onClick={() => setMode('standard')}
            className={`rounded-r-md px-3 py-1 text-sm font-medium transition-colors ${
              mode === 'standard'
                ? 'bg-blue-600 text-white'
                : isDark
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            Standard
          </button>
        </div>
      )}
      <div className="h-[500px] w-full">
        <Radar data={chartData} options={options} />
      </div>
    </div>
  );
}
