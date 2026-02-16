import { TimePeriodSelector } from './TimePeriodSelector';
import type { TimePeriod } from '../../types/api';

interface MetricCardProps {
  title: string;
  period: TimePeriod;
  onPeriodChange: (p: TimePeriod) => void;
  loading: boolean;
  children: React.ReactNode;
}

export function MetricCard({ title, period, onPeriodChange, loading, children }: MetricCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h2>
        <TimePeriodSelector value={period} onChange={onPeriodChange} />
      </div>
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/60 dark:bg-gray-800/60 rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cf-blue"></div>
          </div>
        )}
        <div className={loading ? 'opacity-50 pointer-events-none' : ''}>{children}</div>
      </div>
    </div>
  );
}
