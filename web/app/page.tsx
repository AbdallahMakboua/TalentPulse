'use client';

import { useEffect, useState } from 'react';
import { api, OrgOverview } from '@/lib/api';
import { RiskDistribution } from '@/components/RiskDistribution';
import { AlertsList } from '@/components/AlertsList';
import { StatCard } from '@/components/StatCard';

export default function OrgPage() {
  const [data, setData] = useState<OrgOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const load = async () => {
    try {
      const d = await api.orgOverview();
      setData(d);
    } catch {
      // If no data, try syncing first
      setSyncing(true);
      try {
        await api.sync();
        const d = await api.orgOverview();
        setData(d);
      } catch (e) {
        console.error(e);
      }
      setSyncing(false);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  if (loading) return <div className="animate-pulse text-lg">Loading organization overview...</div>;
  if (!data) return <div className="text-red-600">Failed to load data. Is the API running?</div>;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Organization Overview</h1>
          <p className="text-slate-500 mt-1">AI-powered talent intelligence • Privacy-first • Explainable</p>
        </div>
        <button
          onClick={async () => { setSyncing(true); await api.sync(); await load(); setSyncing(false); }}
          disabled={syncing}
          className="px-4 py-2 bg-pulse-600 text-white rounded-lg hover:bg-pulse-700 disabled:opacity-50 transition-colors"
        >
          {syncing ? '⏳ Syncing...' : '🔄 Sync Data'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-6">
        <StatCard title="Employees" value={data.total_employees} icon="👥" />
        <StatCard title="Teams" value={data.total_teams} icon="🏢" />
        <StatCard
          title="Burnout Alerts"
          value={data.burnout_risk_distribution.High || 0}
          icon="🔴"
          subtitle={`${data.burnout_risk_distribution.Medium || 0} medium risk`}
          variant={data.burnout_risk_distribution.High > 0 ? 'danger' : 'default'}
        />
        <StatCard
          title="High Potentials"
          value={data.potential_distribution.High || 0}
          icon="⭐"
          subtitle={`${data.potential_distribution.Medium || 0} emerging`}
          variant="success"
        />
      </div>

      {/* Risk Distributions */}
      <div className="grid grid-cols-2 gap-6">
        <RiskDistribution title="Burnout Risk" data={data.burnout_risk_distribution} />
        <RiskDistribution title="Performance Pressure" data={data.pressure_distribution} />
        <RiskDistribution title="Growth Potential" data={data.potential_distribution} reversed />
        <RiskDistribution title="Performance Degradation" data={data.degradation_distribution} />
      </div>

      {/* Alerts */}
      {data.trending_alerts.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">🚨 Trending Alerts</h2>
          <AlertsList alerts={data.trending_alerts} />
        </div>
      )}

      {/* Overloaded Teams */}
      {data.overloaded_teams.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-amber-800 mb-3">⚠️ Overloaded Teams</h2>
          <div className="space-y-2">
            {data.overloaded_teams.map((t, i) => (
              <div key={i} className="flex justify-between items-center bg-white p-3 rounded-lg">
                <span className="font-medium">{t.team}</span>
                <span className="text-amber-700 font-mono">Avg workload: {t.avg_workload}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Privacy banner */}
      <div className="bg-pulse-50 border border-pulse-200 rounded-xl p-4 text-sm text-pulse-800">
        🔒 <strong>Privacy Notice:</strong> TalentPulse collects ONLY aggregated metadata (counts, durations, timestamps).
        No message content, email subjects, attachments, or screen activity is ever accessed.
      </div>
    </div>
  );
}
