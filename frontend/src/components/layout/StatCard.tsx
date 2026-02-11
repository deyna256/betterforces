interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: string;
  color?: 'blue' | 'green' | 'red' | 'orange';
}

const colorClasses = {
  blue: 'from-blue-500 to-indigo-600 bg-blue-500 text-blue-100 shadow-blue-500/25 border-blue-400',
  green: 'from-green-500 to-teal-600 bg-green-500 text-green-100 shadow-green-500/25 border-green-400',
  red: 'from-red-500 to-pink-600 bg-red-500 text-red-100 shadow-red-500/25 border-red-400',
  orange: 'from-orange-500 to-amber-600 bg-orange-500 text-orange-100 shadow-orange-500/25 border-orange-400',
};

const gradientClasses = {
  blue: 'from-blue-100 to-indigo-200 dark:from-blue-900 dark:to-indigo-900',
  green: 'from-green-100 to-teal-200 dark:from-green-900 dark:to-teal-900',
  red: 'from-red-100 to-pink-200 dark:from-red-900 dark:to-pink-900',
  orange: 'from-orange-100 to-amber-200 dark:from-orange-900 dark:to-amber-900',
};

export function StatCard({ title, value, description, color = 'blue' }: StatCardProps) {
  return (
    <div className="relative group">
      <div className={`absolute -inset-0.5 bg-gradient-to-r ${colorClasses[color]} rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-300`}></div>
      <div className="relative bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 transform hover:scale-105 transition-all duration-300">
        {/* Header */}
        <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${gradientClasses[color]} shadow-lg mb-4`}>
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${colorClasses[color]} flex items-center justify-center shadow-lg`}>
            {color === 'blue' && (
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            )}
            {color === 'green' && (
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            {color === 'red' && (
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            )}
            {color === 'orange' && (
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 tracking-wider uppercase">
            {title}
          </h3>
          <p className="text-4xl font-black text-gray-900 dark:text-white leading-none mb-1 transform group-hover:scale-110 transition-transform duration-300">
            {value}
          </p>
          {description && (
            <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">
              {description}
            </p>
          )}
        </div>

        {/* Glow effect */}
        <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${colorClasses[color]} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
      </div>
    </div>
  );
}
