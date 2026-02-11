import { FormEvent } from 'react';

interface HeaderProps {
  handle: string;
  onHandleChange: (handle: string) => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export function Header({ handle, onHandleChange, theme, onToggleTheme }: HeaderProps) {
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newHandle = formData.get('handle') as string;
    if (newHandle.trim()) {
      onHandleChange(newHandle.trim());
    }
  };

  return (
    <header className="bg-gradient-to-r from-cf-blue to-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">BetterForces</h1>
            <p className="text-blue-100 text-sm mt-1">
              Advanced Codeforces Analytics & Insights
            </p>
          </div>

          <div className="flex items-center gap-3">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                name="handle"
                placeholder="Codeforces handle"
                defaultValue={handle}
                className="px-4 py-2 rounded-lg bg-white/90 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-white dark:bg-gray-800 text-cf-blue dark:text-blue-400 rounded-lg font-semibold hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
              >
                Analyze
              </button>
            </form>

            <button
              onClick={onToggleTheme}
              className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
