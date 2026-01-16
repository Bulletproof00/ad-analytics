'use client';

import { useState } from 'react';

export default function IntegrationsPage() {
  const [csvText, setCsvText] = useState('campaign,leads,cpl\\nTest,10,25');
  const [mapping, setMapping] = useState('{\"campaign\":\"name\",\"leads\":\"leads\",\"cpl\":\"cpl\"}');
  const [result, setResult] = useState<any>(null);

  const importCsv = async () => {
    const res = await fetch('/api/backend/api/kpi/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'CSV Import', csv_text: csvText, mapping: JSON.parse(mapping) }),
    });
    const data = await res.json();
    setResult(data);
  };

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Integrationen</h1>
        <p className="page-subtitle">CSV Import und künftige Datenquellen.</p>
      </div>
      <div className="card">
        <h2 className="section-title">CSV KPI Import</h2>
        <textarea className="textarea" rows={6} value={csvText} onChange={(e) => setCsvText(e.target.value)} />
        <input className="input" value={mapping} onChange={(e) => setMapping(e.target.value)} />
        <button className="button" style={{ marginTop: 12 }} onClick={importCsv}>CSV importieren</button>
        {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
      </div>
    </div>
  );
}
