'use client';

import { useEffect, useState } from 'react';
import { api, TeamSummary } from '@/lib/api';
import Link from 'next/link';

function TrendBadge({ trend }: { trend: string }) {
  const styles: Record<string, string> = {
    thriving: 'bg-green-100 text-green-800',
    stable: 'bg-slate-100 text-slate-700',
    concerning: 'bg-red-100 text-red-800',
  };
  const labels: Record<string, string> = {
    thriving: '↗ Thriving',
    stable: '→ Stable',
    concerning: '↘ Concerning',
  };
  return (
    <span className={`text-xs font-medium px-2 py-1 rounded-full ${styles[trend] || styles.stable}`}>
      {labels[trend] || trend}
    </span>
  );
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<TeamSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.teams().then(setTeams).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse text-lg">Loading teams...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-slate-900">Teams</h1>
      <p className="text-slate-500">Team-level health indicators with workload balance analysis</p>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {teams.map((team) => (
          <Link
            key={team.id}
            href={`/employees?team=${encodeURIComponent(team.name)}`}
            className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">{team.name}</h3>
                <p className="text-sm text-slate-500">{team.department} • {team.employee_count} people</p>
              </div>
              <TrendBadge trend={team.trend} />
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600">Burnout Risk</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${team.avg_burnout_risk > 55 ? 'bg-red-500' : team.avg_burnout_risk > 35 ? 'bg-amber-500' : 'bg-green-500'}`}
                      style={{ width: `${team.avg_burnout_risk}%` }}
                    />
                  </div>
                  <span className="text-sm font-mono w-8">{team.avg_burnout_risk.toFixed(0)}</span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600">Growth Potential</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-pulse-500 rounded-full"
                      style={{ width: `${team.avg_high_potential}%` }}
                    />
                  </div>
                  <span className="text-sm font-mono w-8">{team.avg_high_potential.toFixed(0)}</span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600">Workload Imbalance</span>
                <span className={`text-sm font-medium px-2 py-0.5 rounded ${team.workload_imbalance > 5 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}`}>
                  {team.workload_imbalance > 5 ? '⚠ High' : '✓ Balanced'}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
