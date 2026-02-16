import type { TimePeriod } from '../../types/api';

const OPTIONS: { label: string; value: TimePeriod }[] = [
  { label: '1D', value: 'day' },
  { label: '1W', value: 'week' },
  { label: '1M', value: 'month' },
  { label: '6M', value: 'half_year' },
  { label: '1Y', value: 'year' },
  { label: 'All', value: 'all_time' },
];

interface TimePeriodSelectorProps {
  value: TimePeriod;
  onChange: (period: TimePeriod) => void;
}

export function TimePeriodSelector({ value, onChange }: TimePeriodSelectorProps) {
  return (
    <div className="inline-flex items-center gap-0.5 p-0.5 rounded-lg bg-gray-100 dark:bg-gray-700 border border-gray-200 dark:border-gray-600">
      {OPTIONS.map(({ label, value: optionValue }) => {
        const isActive = value === optionValue;

        return (
          <button
            key={optionValue}
            onClick={() => onChange(optionValue)}
            className={`px-2.5 py-1 rounded-md text-xs font-semibold tracking-wide transition-all duration-200 ${
              isActive
                ? 'bg-cf-blue text-white shadow-sm shadow-blue-500/25'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/60 dark:hover:bg-gray-600/60'
            }`}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}
