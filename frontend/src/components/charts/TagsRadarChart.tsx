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

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface TagsRadarChartProps {
  tags: TagInfo[];
  type: 'all' | 'weak';
}

export function TagsRadarChart({ tags, type }: TagsRadarChartProps) {
  // Select top tags for radar (max 10 for readability)
  const topTags =
    type === 'all'
      ? [...tags].sort((a, b) => b.problem_count - a.problem_count).slice(0, 10)
      : [...tags].slice(0, 10);

  const labels = topTags.map((tag) => tag.tag);
  const medianRatings = topTags.map((tag) => tag.median_rating);
  const averageRatings = topTags.map((tag) => tag.average_rating);

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
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(26, 115, 232, 1)',
      },
      {
        label: 'Average Rating',
        data: averageRatings,
        backgroundColor: 'rgba(0, 200, 83, 0.2)',
        borderColor: 'rgba(0, 200, 83, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(0, 200, 83, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
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
      },
      title: {
        display: true,
        text:
          type === 'all'
            ? 'Tag Performance Radar (Top 10)'
            : 'Weak Tags Radar',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            const index = context.dataIndex;
            const tag = topTags[index];
            return `Problems: ${tag.problem_count}`;
          },
        },
      },
    },
    scales: {
      r: {
        beginAtZero: false,
        ticks: {
          stepSize: 200,
        },
      },
    },
  };

  return (
    <div className="h-[500px] w-full">
      <Radar data={chartData} options={options} />
    </div>
  );
}
