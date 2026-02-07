'use client';

import { AlertTriangle, TrendingDown, Flame, Eye } from 'lucide-react';
import Link from 'next/link';

interface Alert {
  employee_id?: number;
  employee_name?: string;
  employee?: string;
  team?: string;
  score?: number;
  type: string;
  severity?: string;
  message: string;
}

interface Props {
  alerts: Alert[];
}

const ICONS: Record<string, React.ReactNode> = {
  burnout_risk: <Flame className="w-4 h-4" />,
  performance_degradation: <TrendingDown className="w-4 h-4" />,
  high_pressure: <AlertTriangle className="w-4 h-4" />,
  default: <Eye className="w-4 h-4" />,
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'border-red-400 bg-red-50',
  high: 'border-orange-400 bg-orange-50',
  medium: 'border-amber-400 bg-amber-50',
  low: 'border-slate-300 bg-slate-50',
};

const SEVERITY_TEXT: Record<string, string> = {
  critical: 'text-red-700',
  high: 'text-orange-700',
  medium: 'text-amber-700',
  low: 'text-slate-600',
};

export function AlertsList({ alerts }: Props) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">Alerts</h3>
        <p className="text-slate-400 text-sm">No active alerts — looking good!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-700 mb-3">
        Alerts <span className="text-xs font-normal text-slate-400">({alerts.length})</span>
      </h3>
      <ul className="space-y-2 max-h-72 overflow-y-auto">
        {alerts.map((alert, i) => (
          <li
            key={`${alert.employee_id}-${alert.type}-${i}`}
            className={`flex items-start gap-3 p-3 rounded-lg border-l-4 ${
              SEVERITY_COLORS[alert.severity || 'medium'] || SEVERITY_COLORS.low
            }`}
          >
            <span className={SEVERITY_TEXT[alert.severity || 'medium'] || SEVERITY_TEXT.low}>
              {ICONS[alert.type] || ICONS.default}
            </span>
            <div className="flex-1 min-w-0">
              <Link
                href={alert.employee_id ? `/employees/${alert.employee_id}` : '#'}
                className="text-sm font-medium text-slate-800 hover:underline"
              >
                {alert.employee_name || alert.employee || 'Unknown'}
              </Link>
              <p className="text-xs text-slate-500 mt-0.5 truncate">{alert.message}</p>
            </div>
            <span
              className={`text-[10px] font-semibold uppercase tracking-wide ${
                SEVERITY_TEXT[alert.severity || 'medium'] || SEVERITY_TEXT.low
              }`}
            >
              {alert.severity || 'alert'}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
