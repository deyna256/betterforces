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
  isDark: boolean;
}

export function TimePeriodSelector({ value, onChange, isDark }: TimePeriodSelectorProps) {
  return (
    <div className="flex justify-center gap-1 mb-8">
      {OPTIONS.map(({ label, value: optionValue }, index) => {
        const isActive = value === optionValue;
        const isFirst = index === 0;
        const isLast = index === OPTIONS.length - 1;
        const rounded = isFirst ? 'rounded-l-md' : isLast ? 'rounded-r-md' : '';

        return (
          <button
            key={optionValue}
            onClick={() => onChange(optionValue)}
            className={`${rounded} px-3 py-1 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-blue-600 text-white'
                : isDark
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}
