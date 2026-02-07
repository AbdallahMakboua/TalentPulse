'use client';

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';

interface SignalRow {
  week_start: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

interface Props {
  signals: SignalRow[];
  metrics?: string[];
  title?: string;
}

const METRIC_COLORS: Record<string, string> = {
  emails_sent: '#3b82f6',
  emails_received: '#60a5fa',
  meeting_hours: '#f59e0b',
  focus_hours: '#22c55e',
  after_hours: '#ef4444',
  collab_hours: '#8b5cf6',
  msgs_sent: '#06b6d4',
  unique_collaborators: '#ec4899',
  manager_1on1_count: '#14b8a6',
  weekend_activity: '#f43f5e',
  late_night_events: '#dc2626',
  double_bookings: '#d946ef',
  short_meeting_ratio: '#a855f7',
  recurring_meeting_hours: '#6366f1',
  avg_response_time_hrs: '#0ea5e9',
  pr_commits: '#10b981',
  pr_reviews: '#34d399',
  pr_comments: '#6ee7b7',
  docs_edited: '#fbbf24',
  wiki_contributions: '#f97316',
  training_hours: '#84cc16',
};

const DEFAULT_METRICS = [
  'meeting_hours',
  'focus_hours',
  'after_hours',
  'collab_hours',
];

export function SignalChart({ signals, metrics, title = 'Weekly Signals' }: Props) {
  const displayMetrics = metrics || DEFAULT_METRICS;

  if (!signals || signals.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-700 mb-4">{title}</h3>
        <p className="text-sm text-slate-400">No signal data available yet.</p>
      </div>
    );
  }

  const data = signals.map((s) => ({
    ...s,
    week: s.week_start.slice(5),
  }));

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-700 mb-4">{title}</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="week" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: 12 }}
            />
            <Legend
              wrapperStyle={{ fontSize: 11 }}
              formatter={(value: string) => value.replaceAll('_', ' ')}
            />
            {displayMetrics.map((m) => (
              <Line
                key={m}
                type="monotone"
                dataKey={m}
                stroke={METRIC_COLORS[m] || '#94a3b8'}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
