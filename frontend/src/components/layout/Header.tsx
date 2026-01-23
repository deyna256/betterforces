import { FormEvent } from 'react';

interface HeaderProps {
  handle: string;
  onHandleChange: (handle: string) => void;
}

export function Header({ handle, onHandleChange }: HeaderProps) {
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

          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              name="handle"
              placeholder="Codeforces handle"
              defaultValue={handle}
              className="px-4 py-2 rounded-lg bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-white text-cf-blue rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Analyze
            </button>
          </form>
        </div>
      </div>
    </header>
  );
}
