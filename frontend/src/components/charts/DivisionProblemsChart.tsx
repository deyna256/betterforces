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
import type { DivisionStats } from '../../types/api';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const DIVISION_COLORS: Record<string, { bg: string; border: string }> = {
  'Div. 1': { bg: 'rgba(255, 0, 0, 0.7)', border: '#FF0000' },
  'Div. 1+2': { bg: 'rgba(255, 140, 0, 0.7)', border: '#FF8C00' },
  'Div. 2': { bg: 'rgba(0, 0, 255, 0.7)', border: '#0000FF' },
  'Div. 3': { bg: 'rgba(3, 168, 158, 0.7)', border: '#03A89E' },
  'Div. 4': { bg: 'rgba(128, 128, 128, 0.7)', border: '#808080' },
};

const DEFAULT_COLORS = { bg: 'rgba(99, 102, 241, 0.7)', border: '#6366F1' };

interface DivisionProblemsChartProps {
  divisions: DivisionStats[];
  isDark?: boolean;
}

export function DivisionProblemsChart({ divisions, isDark = false }: DivisionProblemsChartProps) {
  const sorted = [...divisions].sort(
    (a, b) => b.average_problems_per_contest - a.average_problems_per_contest
  );

  const textColor = isDark ? '#e5e7eb' : '#374151';
  const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

  const backgroundColors = sorted.map((d) => (DIVISION_COLORS[d.division] ?? DEFAULT_COLORS).bg);
  const borderColors = sorted.map((d) => (DIVISION_COLORS[d.division] ?? DEFAULT_COLORS).border);

  const chartData = {
    labels: sorted.map((d) => d.division),
    datasets: [
      {
        label: 'Avg. Problems / Contest',
        data: sorted.map((d) => d.average_problems_per_contest),
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
        text: 'Average Problems Solved per Contest by Division',
        color: textColor,
        font: { size: 16, weight: 'bold' },
      },
      tooltip: {
        callbacks: {
          afterLabel: (context) => {
            const d = sorted[context.dataIndex];
            return [`Contests: ${d.contest_count}`, `Total solved: ${d.total_problems_solved}`];
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { color: textColor },
        grid: { color: gridColor },
        title: {
          display: true,
          text: 'Avg. Problems per Contest',
          color: textColor,
        },
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
