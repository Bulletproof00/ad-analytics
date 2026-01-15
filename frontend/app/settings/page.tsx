'use client';

import { useEffect, useState } from 'react';

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>({});
  const [saving, setSaving] = useState(false);

  const load = async () => {
    const res = await fetch('/api/backend/api/settings');
    const data = await res.json();
    setSettings(data);
  };

  useEffect(() => {
    load();
  }, []);

  const updateSection = (key: string, value: any) => {
    setSettings({ ...settings, [key]: value });
  };

  const saveSection = async (key: string) => {
    setSaving(true);
    await fetch('/api/backend/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value: settings[key] }),
    });
    setSaving(false);
  };

  return (
    <div className="grid">
      <h1>Settings</h1>
      <div className="card">
        <h2>Scanning</h2>
        <textarea
          className="textarea"
          rows={6}
          value={(settings.scanning?.keyword_presets?.pet || []).join('\n')}
          onChange={(e) => updateSection('scanning', {
            ...settings.scanning,
            keyword_presets: { ...settings.scanning?.keyword_presets, pet: e.target.value.split('\n') },
          })}
        />
        <button className="button" style={{ marginTop: 12 }} onClick={() => saveSection('scanning')} disabled={saving}>
          Save Scanning
        </button>
      </div>
      <div className="card">
        <h2>Scoring</h2>
        <div className="filters">
          <input
            className="input"
            type="number"
            value={settings.scoring?.winner_threshold || 75}
            onChange={(e) => updateSection('scoring', { ...settings.scoring, winner_threshold: Number(e.target.value) })}
          />
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={() => saveSection('scoring')} disabled={saving}>
          Save Scoring
        </button>
      </div>
    </div>
  );
}
