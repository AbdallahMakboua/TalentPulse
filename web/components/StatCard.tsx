interface Props {
  title: string;
  value: number | string;
  icon: string;
  subtitle?: string;
  variant?: 'default' | 'danger' | 'success';
}

export function StatCard({ title, value, icon, subtitle, variant = 'default' }: Props) {
  const bgColors = {
    default: 'bg-white',
    danger: 'bg-red-50 border-red-200',
    success: 'bg-green-50 border-green-200',
  };

  return (
    <div className={`rounded-xl border p-6 ${bgColors[variant]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500 font-medium">{title}</p>
          <p className="text-3xl font-bold text-slate-900 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}
