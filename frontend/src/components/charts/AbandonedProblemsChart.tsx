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
import type { TagAbandoned, RatingAbandoned } from '../../types/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface AbandonedProblemsChartProps {
  data: TagAbandoned[] | RatingAbandoned[];
  type: 'tags' | 'ratings';
  isDark?: boolean;
}

export function AbandonedProblemsChart({ data, type, isDark = false }: AbandonedProblemsChartProps) {
  const sortedData = [...data].sort((a, b) => b.problem_count - a.problem_count).slice(0, 15);

  const labels =
    type === 'tags'
      ? (sortedData as TagAbandoned[]).map((item) => item.tag)
      : (sortedData as RatingAbandoned[]).map((item) => item.rating.toString());

  const textColor = isDark ? '#e5e7eb' : '#374151';
  const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Abandoned Problems',
        data: sortedData.map((item) => item.problem_count),
        backgroundColor: 'rgba(211, 47, 47, 0.7)',
        borderColor: 'rgba(211, 47, 47, 1)',
        borderWidth: 1,
      },
      {
        label: 'Failed Attempts',
        data: sortedData.map((item) => item.total_failed_attempts),
        backgroundColor: 'rgba(255, 111, 0, 0.7)',
        borderColor: 'rgba(255, 111, 0, 1)',
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
        labels: { color: textColor },
      },
      title: {
        display: true,
        text: `Abandoned Problems by ${type === 'tags' ? 'Tags' : 'Rating'} (Top 15)`,
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
            const item = sortedData[index];
            return `Total attempts: ${item.total_failed_attempts}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
          color: textColor,
        },
        grid: { color: gridColor },
      },
      x: {
        ticks: { color: textColor },
        grid: { color: gridColor },
      },
    },
  };

  return (
    <div className="h-96 w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
}
