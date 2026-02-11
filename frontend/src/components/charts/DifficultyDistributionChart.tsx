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

function getRatingColor(rating: number, isDark: boolean): string {
  if (rating < 1200) return isDark ? '#A0A0A0' : '#808080';
  if (rating < 1400) return isDark ? '#00C000' : '#008000';
  if (rating < 1600) return isDark ? '#10D0C4' : '#03A89E';
  if (rating < 1900) return isDark ? '#5555FF' : '#0000FF';
  if (rating < 2100) return isDark ? '#CC55CC' : '#AA00AA';
  if (rating < 2400) return isDark ? '#FFA040' : '#FF8C00';
  return isDark ? '#FF4444' : '#FF0000';
}

interface DifficultyDistributionChartProps {
  ranges: RatingRange[];
  totalSolved: number;
  isDark?: boolean;
}

export function DifficultyDistributionChart({
  ranges,
  totalSolved,
  isDark = false,
}: DifficultyDistributionChartProps) {
  const sortedRanges = [...ranges].sort((a, b) => a.rating - b.rating);

  const labels = sortedRanges.map((range) => range.rating.toString());
  const counts = sortedRanges.map((range) => range.problem_count);
  const percentages = sortedRanges.map(
    (range) => ((range.problem_count / totalSolved) * 100).toFixed(1)
  );

  const textColor = isDark ? '#e5e7eb' : '#374151';
  const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

  const backgroundColors = sortedRanges.map((range) => {
    const hex = getRatingColor(range.rating, isDark);
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, 0.7)`;
  });
  const borderColors = sortedRanges.map((range) => getRatingColor(range.rating, isDark));

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Problems Solved',
        data: counts,
        backgroundColor: backgroundColors,
        borderColor: borderColors,
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
        text: 'Difficulty Distribution',
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
          color: textColor,
        },
        grid: { color: gridColor },
        title: {
          display: true,
          text: 'Number of Problems',
          color: textColor,
        },
      },
      x: {
        ticks: { color: textColor },
        grid: { color: gridColor },
        title: {
          display: true,
          text: 'Rating',
          color: textColor,
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
