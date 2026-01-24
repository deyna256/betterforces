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
import type { RatingRange } from '../../types/api';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface DifficultyRadarChartProps {
  ranges: RatingRange[];
  totalSolved: number;
}

export function DifficultyRadarChart({ ranges, totalSolved }: DifficultyRadarChartProps) {
  // Sort and take meaningful rating ranges
  const sortedRanges = [...ranges]
    .sort((a, b) => a.rating - b.rating)
    .filter((r) => r.rating >= 800 && r.rating <= 3000); // Focus on common rating ranges

  const labels = sortedRanges.map((range) => range.rating.toString());
  const counts = sortedRanges.map((range) => range.problem_count);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Problems Solved',
        data: counts,
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
        text: 'Difficulty Distribution Radar',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.parsed.r;
            const percentage = ((value / totalSolved) * 100).toFixed(1);
            return `${value} problems (${percentage}%)`;
          },
        },
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        ticks: {
          stepSize: 50,
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
