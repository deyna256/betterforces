import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import type { TagInfo } from '../../types/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TagsChartProps {
  tags: TagInfo[];
  overallMedian: number;
  type: 'all';
}

export function TagsChart({ tags, overallMedian, type }: TagsChartProps) {
  const sortedTags =
    type === 'all'
      ? [...tags].sort((a, b) => b.problem_count - a.problem_count).slice(0, 15)
      : [...tags].sort((a, b) => a.median_rating - b.median_rating);

  const labels = sortedTags.map((tag) => tag.tag);
  const medianRatings = sortedTags.map((tag) => tag.median_rating);
  const averageRatings = sortedTags.map((tag) => tag.average_rating);
  const problemCounts = sortedTags.map((tag) => tag.problem_count);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Median Rating',
        data: medianRatings,
        backgroundColor: 'rgba(26, 115, 232, 0.7)',
        borderColor: 'rgba(26, 115, 232, 1)',
        borderWidth: 1,
      },
      {
        label: 'Average Rating',
        data: averageRatings,
        backgroundColor: 'rgba(0, 200, 83, 0.7)',
        borderColor: 'rgba(0, 200, 83, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text:
          type === 'all'
            ? `Tag Ratings (Top 15 by Count) - Overall Median: ${Math.round(overallMedian)}`
            : `Weak Tags (Below Overall Median: ${Math.round(overallMedian)})`,
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            const index = context.dataIndex;
            return `Problems solved: ${problemCounts[index]}\nOverall median: ${Math.round(overallMedian)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Rating',
        },
      },
    },
  };

  return (
    <div className="h-96 w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
}
