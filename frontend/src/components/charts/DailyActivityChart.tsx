import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions,
} from 'chart.js';
import type { DailyActivityItem } from '../../types/api';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend, Filler);

interface DailyActivityChartProps {
  days: DailyActivityItem[];
  isDark?: boolean;
}

export function DailyActivityChart({ days, isDark = false }: DailyActivityChartProps) {
  const labels = days.map((d) => d.date);

  const textColor = isDark ? '#e5e7eb' : '#374151';
  const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Solved',
        data: days.map((d) => d.solved_count),
        borderColor: isDark ? '#60a5fa' : '#2563eb',
        backgroundColor: isDark ? 'rgba(96,165,250,0.15)' : 'rgba(37,99,235,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: days.length > 60 ? 0 : 3,
        pointHoverRadius: 5,
      },
      {
        label: 'Attempts',
        data: days.map((d) => d.attempt_count),
        borderColor: isDark ? '#f97316' : '#ea580c',
        backgroundColor: isDark ? 'rgba(249,115,22,0.15)' : 'rgba(234,88,12,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: days.length > 60 ? 0 : 3,
        pointHoverRadius: 5,
      },
    ],
  };

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: { color: textColor },
      },
      title: {
        display: true,
        text: 'Daily Activity',
        color: textColor,
        font: { size: 16, weight: 'bold' },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { precision: 0, color: textColor },
        grid: { color: gridColor },
        title: { display: true, text: 'Count', color: textColor },
      },
      x: {
        ticks: {
          color: textColor,
          maxTicksLimit: 15,
          maxRotation: 45,
        },
        grid: { color: gridColor },
        title: { display: true, text: 'Date', color: textColor },
      },
    },
  };

  return (
    <div className="h-96 w-full">
      <Line data={chartData} options={options} />
    </div>
  );
}
