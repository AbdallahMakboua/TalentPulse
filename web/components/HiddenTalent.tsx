import { Star, Eye, Zap, TrendingUp } from 'lucide-react';

interface Props {
  data?: {
    detected?: boolean;
    signals?: string[];
    recommendation?: string;
  } | null;
  name?: string;
}

export function HiddenTalent({ data, name }: Props) {
  if (!data && !name) return null;

  return (
    <div className="rounded-xl border border-indigo-200 bg-gradient-to-br from-indigo-50 to-violet-50 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <Star className="w-5 h-5 text-indigo-500" />
        <h3 className="text-sm font-semibold text-slate-700">Hidden Talent Detected</h3>
        <span className="ml-auto text-[10px] font-bold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
          QUIET IMPACT
        </span>
      </div>

      <p className="text-xs text-slate-500 mb-4">
        This employee shows high-impact patterns that may go unnoticed in traditional evaluations.
      </p>

      <div className="space-y-2 mb-4">
        {(data?.signals || ['High collaboration breadth across teams', 'Consistent knowledge-sharing and mentoring patterns', 'Strong peer support signals with modest self-promotion']).map((signal, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="mt-0.5">
              {i === 0 ? <Eye className="w-3.5 h-3.5 text-indigo-400" /> :
               i === 1 ? <Zap className="w-3.5 h-3.5 text-violet-400" /> :
               <TrendingUp className="w-3.5 h-3.5 text-purple-400" />}
            </span>
            <span className="text-xs text-slate-600">{signal}</span>
          </div>
        ))}
      </div>

      {(data?.recommendation || name) && (
        <div className="bg-white/60 rounded-lg p-3 border border-indigo-100">
          <span className="text-[11px] font-medium text-indigo-600 block mb-1">
            Recommended Action
          </span>
          <p className="text-xs text-slate-700">
            {data?.recommendation || `Consider ${name || 'this employee'} for stretch assignments, tech talks, or mentoring programs to amplify their quiet impact.`}
          </p>
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-indigo-200/50">
        <p className="text-[11px] text-slate-400 italic">
          Detected via quiet-impact scoring: high collaboration + knowledge sharing with modest self-promotion signals.
        </p>
      </div>
    </div>
  );
}
