import { Info, ShieldCheck } from 'lucide-react';

interface Explanation {
  dimension?: string;
  score_name?: string;
  score: number;
  label: string;
  top_factors?: string[];
  top_contributors?: Array<{ signal: string; value: number; direction: string; delta: string }>;
  bias_note?: string;
  fairness_warning?: string;
  trend_explanation?: string;
  confidence?: number;
  limitations?: string;
}

interface Props {
  explanations?: Explanation[];
  card?: Explanation;
}

const DIM_COLORS: Record<string, string> = {
  burnout_risk: 'border-red-200 bg-red-50',
  high_pressure: 'border-orange-200 bg-orange-50',
  high_potential: 'border-emerald-200 bg-emerald-50',
  performance_degradation: 'border-amber-200 bg-amber-50',
};

const DIM_LABELS: Record<string, string> = {
  burnout_risk: 'Burnout Risk',
  high_pressure: 'High Pressure',
  high_potential: 'High Potential',
  performance_degradation: 'Performance Trend',
};

export function ExplainCard({ explanations, card }: Props) {
  // Support both array mode and single card mode
  const items: Explanation[] = explanations || (card ? [card] : []);
  if (items.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <Info className="w-4 h-4 text-indigo-500" />
        <h3 className="text-sm font-semibold text-slate-700">Explainability</h3>
      </div>
      <p className="text-xs text-slate-400 mb-4">
        Every score is transparent. Here&apos;s exactly what drives each dimension.
      </p>
      <div className="grid gap-3">
        {items.map((exp) => {
          const dim = exp.dimension || exp.score_name || 'unknown';
          const factors = exp.top_factors || exp.top_contributors?.map(c => `${c.signal}: ${c.value} (${c.direction} ${c.delta})`) || [];
          const biasNote = exp.bias_note || exp.fairness_warning;
          return (
            <div
              key={dim}
              className={`rounded-lg border-l-4 p-4 ${
                DIM_COLORS[dim] || 'border-slate-200 bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-700">
                  {DIM_LABELS[dim] || dim.replace(/_/g, ' ')}
                </span>
                <span className="text-xs font-semibold bg-white/80 px-2 py-0.5 rounded-full shadow-sm">
                  {exp.score.toFixed(0)} — {exp.label}
                </span>
              </div>
              {exp.trend_explanation && (
                <p className="text-xs text-slate-500 mb-2 italic">{exp.trend_explanation}</p>
              )}
              <ul className="space-y-1">
                {factors.map((factor, i) => (
                  <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                    <span className="mt-1 w-1 h-1 rounded-full bg-slate-400 shrink-0" />
                    {factor}
                  </li>
                ))}
              </ul>
              {biasNote && (
                <div className="flex items-start gap-1.5 mt-2 text-[11px] text-indigo-600">
                  <ShieldCheck className="w-3 h-3 mt-0.5 shrink-0" />
                  <span>{biasNote}</span>
                </div>
              )}
              {exp.confidence !== undefined && (
                <div className="text-[11px] text-slate-400 mt-2">
                  Confidence: {(exp.confidence * 100).toFixed(0)}%
                  {exp.limitations && ` · ${exp.limitations}`}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
