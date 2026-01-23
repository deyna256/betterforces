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
import type { RatingRange } from '../../types/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface DifficultyDistributionChartProps {
  ranges: RatingRange[];
  totalSolved: number;
}

export function DifficultyDistributionChart({
  ranges,
  totalSolved,
}: DifficultyDistributionChartProps) {
  const sortedRanges = [...ranges].sort((a, b) => a.rating - b.rating);

  const labels = sortedRanges.map((range) => range.rating.toString());
  const counts = sortedRanges.map((range) => range.problem_count);
  const percentages = sortedRanges.map(
    (range) => ((range.problem_count / totalSolved) * 100).toFixed(1)
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Problems Solved',
        data: counts,
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
        text: 'Difficulty Distribution',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            const index = context.dataIndex;
            return `${percentages[index]}% of total`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
        title: {
          display: true,
          text: 'Number of Problems',
        },
      },
      x: {
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
