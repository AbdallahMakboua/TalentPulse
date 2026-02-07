'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { api, EmployeeSummary } from '@/lib/api';
import Link from 'next/link';
import { ScoreBadge } from '@/components/ScoreBadge';

export default function EmployeesPage() {
  const params = useSearchParams();
  const teamFilter = params.get('team');
  const [employees, setEmployees] = useState<EmployeeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.employees({ risk_filter: riskFilter || undefined, team: teamFilter || undefined })
      .then(setEmployees)
      .finally(() => setLoading(false));
  }, [riskFilter, teamFilter]);

  const filtered = employees.filter(e =>
    e.name.toLowerCase().includes(search.toLowerCase()) ||
    e.role.toLowerCase().includes(search.toLowerCase()) ||
    e.team_name.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div className="animate-pulse text-lg">Loading employees...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Employees</h1>
          <p className="text-slate-500">
            {teamFilter ? `Team: ${teamFilter}` : 'All employees'} • {filtered.length} results
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search by name, role, or team..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-pulse-500 focus:border-transparent"
        />
        <select
          value={riskFilter}
          onChange={e => setRiskFilter(e.target.value)}
          className="px-4 py-2 border border-slate-300 rounded-lg"
        >
          <option value="">All Risk Levels</option>
          <option value="High">🔴 High Risk</option>
          <option value="Medium">🟡 Medium Risk</option>
          <option value="Low">🟢 Low Risk</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Employee</th>
              <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Team</th>
              <th className="text-center px-6 py-3 text-xs font-medium text-slate-500 uppercase">Burnout Risk</th>
              <th className="text-center px-6 py-3 text-xs font-medium text-slate-500 uppercase">Pressure</th>
              <th className="text-center px-6 py-3 text-xs font-medium text-slate-500 uppercase">Potential</th>
              <th className="text-center px-6 py-3 text-xs font-medium text-slate-500 uppercase">Performance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map((emp) => (
              <tr key={emp.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4">
                  <Link href={`/employees/${emp.id}`} className="hover:text-pulse-600">
                    <div className="font-medium text-slate-900">{emp.name}</div>
                    <div className="text-sm text-slate-500">{emp.role} • {emp.seniority}</div>
                  </Link>
                </td>
                <td className="px-6 py-4 text-sm text-slate-600">{emp.team_name}</td>
                <td className="px-6 py-4 text-center">
                  <ScoreBadge score={emp.burnout_risk} label={emp.burnout_label} />
                </td>
                <td className="px-6 py-4 text-center">
                  <ScoreBadge score={emp.high_pressure} label={emp.pressure_label} />
                </td>
                <td className="px-6 py-4 text-center">
                  <ScoreBadge score={emp.high_potential} label={emp.potential_label} reversed />
                </td>
                <td className="px-6 py-4 text-center">
                  <ScoreBadge score={emp.performance_degradation} label={emp.degradation_label} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
