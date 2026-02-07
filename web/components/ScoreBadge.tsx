interface Props {
  score: number;
  label: string;
  reversed?: boolean;
  large?: boolean;
}

export function ScoreBadge({ score, label, reversed = false, large = false }: Props) {
  let color = '';
  if (label === 'High') {
    color = reversed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  } else if (label === 'Medium') {
    color = 'bg-amber-100 text-amber-800';
  } else if (label === 'Low') {
    color = reversed ? 'bg-slate-100 text-slate-600' : 'bg-green-100 text-green-800';
  } else {
    color = 'bg-slate-100 text-slate-500';
  }

  return (
    <div className="inline-flex flex-col items-center gap-1">
      <span className={`${large ? 'text-2xl font-bold' : 'text-sm font-semibold'} font-mono`}>
        {score.toFixed(0)}
      </span>
      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>
        {label}
      </span>
    </div>
  );
}
