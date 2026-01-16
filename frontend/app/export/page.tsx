'use client';

import { useState } from 'react';

export default function ExportPage() {
  const [niche, setNiche] = useState('pet');
  const [funnel, setFunnel] = useState('whatsapp');
  const [budget, setBudget] = useState(500);
  const [objective, setObjective] = useState('Leads');
  const [exportResult, setExportResult] = useState<any>(null);

  const buildExport = async () => {
    const res = await fetch('/api/backend/api/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ niche, funnel_type: funnel, budget, objective, test_queue_ids: [] }),
    });
    const data = await res.json();
    setExportResult(data);
  };

  return (
    <div className="grid">
      <h1>Autopilot Export</h1>
      <div className="card">
        <div className="filters">
          <input className="input" value={niche} onChange={(e) => setNiche(e.target.value)} placeholder="Niche" />
          <input className="input" value={funnel} onChange={(e) => setFunnel(e.target.value)} placeholder="Funnel" />
          <input className="input" type="number" value={budget} onChange={(e) => setBudget(Number(e.target.value))} />
          <input className="input" value={objective} onChange={(e) => setObjective(e.target.value)} />
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={buildExport}>Generate Export</button>
      </div>
      {exportResult && (
        <div className="card">
          <h2>Export Package</h2>
          <pre>{JSON.stringify(exportResult, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
