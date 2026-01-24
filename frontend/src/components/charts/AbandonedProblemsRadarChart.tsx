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
import type { TagAbandoned, RatingAbandoned } from '../../types/api';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

interface AbandonedProblemsRadarChartProps {
  data: TagAbandoned[] | RatingAbandoned[];
  type: 'tags' | 'ratings';
  totalAbandoned: number;
}

export function AbandonedProblemsRadarChart({
  data,
  type,
  totalAbandoned,
}: AbandonedProblemsRadarChartProps) {
  // Sort and take top for radar (max 12 for readability)
  const sortedData = [...data].sort((a, b) => b.problem_count - a.problem_count).slice(0, 12);

  const labels =
    type === 'tags'
      ? (sortedData as TagAbandoned[]).map((item) => item.tag)
      : (sortedData as RatingAbandoned[]).map((item) => item.rating.toString());

  const problemsData = sortedData.map((item) => item.problem_count);
  const attemptsData = sortedData.map((item) => item.total_failed_attempts);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Abandoned Problems',
        data: problemsData,
        backgroundColor: 'rgba(211, 47, 47, 0.2)',
        borderColor: 'rgba(211, 47, 47, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(211, 47, 47, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(211, 47, 47, 1)',
      },
      {
        label: 'Total Failed Attempts',
        data: attemptsData,
        backgroundColor: 'rgba(255, 111, 0, 0.2)',
        borderColor: 'rgba(255, 111, 0, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(255, 111, 0, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(255, 111, 0, 1)',
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
        text: `Abandoned Problems by ${type === 'tags' ? 'Tags' : 'Rating'} (Top 12)`,
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
            const percentage = ((item.problem_count / totalAbandoned) * 100).toFixed(1);
            return `Problems: ${item.problem_count} (${percentage}%), Attempts: ${item.total_failed_attempts}`;
          },
        },
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        ticks: {
          stepSize: 10,
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
