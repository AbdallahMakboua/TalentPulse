import { Flame, TrendingUp, AlertTriangle, Clock } from 'lucide-react';

interface BurnoutPrediction {
  alert?: string;
  message?: string;
  current_score: number;
  projected_weeks?: number;
  pattern_signals?: Record<string, number>;
  confidence?: number;
  uncertainty?: string;
  recommended_action?: string;
  at_risk?: boolean;
  score?: number;
  label?: string;
  factors?: string[];
  trend?: string;
  weeks_to_critical?: number;
}

interface Props {
  prediction?: BurnoutPrediction | null;
  data?: BurnoutPrediction | null;
}

export function PredictiveBurnout({ prediction, data }: Props) {
  const p = prediction || data;
  if (!p) return null;

  // Normalize fields
  const score = p.score ?? p.current_score ?? 0;
  const risk = p.at_risk ?? (p.alert === 'high' || score > 65);
  const factors = p.factors || (p.pattern_signals ? Object.entries(p.pattern_signals).map(([k, v]) => `${k}: ${v}`) : []);
  if (p.recommended_action && factors.length === 0) factors.push(p.recommended_action);
  const bgColor = risk ? 'bg-gradient-to-br from-red-50 to-orange-50' : 'bg-gradient-to-br from-green-50 to-emerald-50';
  const borderColor = risk ? 'border-red-200' : 'border-green-200';
  const iconColor = risk ? 'text-red-500' : 'text-green-500';

  return (
    <div className={`rounded-xl border ${borderColor} ${bgColor} p-6 shadow-sm`}>
      <div className="flex items-center gap-2 mb-3">
        <Flame className={`w-5 h-5 ${iconColor}`} />
        <h3 className="text-sm font-semibold text-slate-700">Predictive Burnout Alert</h3>
        {risk && (
          <span className="ml-auto text-[10px] font-bold bg-red-100 text-red-700 px-2 py-0.5 rounded-full animate-pulse">
            AT RISK
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className={`text-2xl font-bold ${risk ? 'text-red-600' : 'text-green-600'}`}>
            {score.toFixed(0)}
          </div>
          <div className="text-[11px] text-slate-500">Risk Score</div>
        </div>
        <div className="text-center">
          <div className="flex items-center justify-center gap-1">
            <TrendingUp className={`w-4 h-4 ${
              (p.trend || p.alert) === 'increasing' ? 'text-red-500' :
              (p.trend || p.alert) === 'decreasing' ? 'text-green-500' : 'text-slate-400'
            }`} />
            <span className="text-sm font-medium text-slate-700 capitalize">{p.trend || p.alert || 'steady'}</span>
          </div>
          <div className="text-[11px] text-slate-500">Trend</div>
        </div>
        <div className="text-center">
          {(p.weeks_to_critical || p.projected_weeks) ? (
            <>
              <div className="flex items-center justify-center gap-1">
                <Clock className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-bold text-amber-600">{p.weeks_to_critical || p.projected_weeks}w</span>
              </div>
              <div className="text-[11px] text-slate-500">Est. Critical</div>
            </>
          ) : (
            <>
              <div className="text-sm font-medium text-green-600">Stable</div>
              <div className="text-[11px] text-slate-500">No ETA</div>
            </>
          )}
        </div>
      </div>

      {factors.length > 0 && (
        <div>
          <div className="flex items-center gap-1 mb-2">
            <AlertTriangle className="w-3 h-3 text-amber-500" />
            <span className="text-[11px] font-medium text-slate-600">Contributing Factors</span>
          </div>
          <ul className="space-y-1">
            {factors.map((f, i) => (
              <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                <span className="mt-1.5 w-1 h-1 rounded-full bg-slate-400 shrink-0" />
                {f}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-slate-200/60">
        <p className="text-[11px] text-slate-400 italic">
          Prediction based on 8-week signal trends and cohort comparison. Not a diagnosis.
        </p>
      </div>
    </div>
  );
}
