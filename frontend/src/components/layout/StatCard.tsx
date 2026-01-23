interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: string;
  color?: 'blue' | 'green' | 'red' | 'orange';
}

const colorClasses = {
  blue: 'bg-blue-50 border-blue-200 text-blue-900',
  green: 'bg-green-50 border-green-200 text-green-900',
  red: 'bg-red-50 border-red-200 text-red-900',
  orange: 'bg-orange-50 border-orange-200 text-orange-900',
};

export function StatCard({ title, value, description, color = 'blue' }: StatCardProps) {
  return (
    <div className={`p-6 rounded-lg border-2 ${colorClasses[color]}`}>
      <h3 className="text-sm font-medium opacity-75 mb-2">{title}</h3>
      <p className="text-3xl font-bold mb-1">{value}</p>
      {description && <p className="text-sm opacity-75">{description}</p>}
    </div>
  );
}
