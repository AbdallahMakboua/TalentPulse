'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, unknown>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getSettings().then(setSettings);
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const updated = await api.updateSettings(settings);
      setSettings(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) { console.error(e); }
    setSaving(false);
  };

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 mt-1">Configure TalentPulse behavior and privacy controls</p>
      </div>

      <div className="bg-white rounded-xl border p-6 space-y-6">
        <h2 className="text-lg font-semibold">Working Hours</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Start Hour</label>
            <input
              type="number"
              min={0} max={23}
              value={settings.working_hours_start as number || 9}
              onChange={e => setSettings(s => ({ ...s, working_hours_start: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">End Hour</label>
            <input
              type="number"
              min={0} max={23}
              value={settings.working_hours_end as number || 18}
              onChange={e => setSettings(s => ({ ...s, working_hours_end: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Timezone</label>
          <input
            type="text"
            value={settings.timezone as string || 'America/New_York'}
            onChange={e => setSettings(s => ({ ...s, timezone: e.target.value }))}
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>

        <h2 className="text-lg font-semibold pt-4">Privacy & Data</h2>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Data Retention (days)</label>
          <input
            type="number"
            min={7} max={365}
            value={settings.data_retention_days as number || 90}
            onChange={e => setSettings(s => ({ ...s, data_retention_days: parseInt(e.target.value) }))}
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="demo_mode"
            checked={settings.demo_mode as boolean ?? true}
            onChange={e => setSettings(s => ({ ...s, demo_mode: e.target.checked }))}
            className="w-4 h-4"
          />
          <label htmlFor="demo_mode" className="text-sm text-slate-700">Demo Mode (synthetic data)</label>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="enable_graph"
            checked={settings.enable_graph as boolean ?? false}
            onChange={e => setSettings(s => ({ ...s, enable_graph: e.target.checked }))}
            className="w-4 h-4"
          />
          <label htmlFor="enable_graph" className="text-sm text-slate-700">
            Enable Microsoft Graph (metadata only)
          </label>
        </div>

        <button
          onClick={save}
          disabled={saving}
          className="px-6 py-2 bg-pulse-600 text-white rounded-lg hover:bg-pulse-700 disabled:opacity-50"
        >
          {saving ? 'Saving...' : saved ? '✅ Saved!' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
}
