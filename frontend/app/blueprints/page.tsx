'use client';

import { useEffect, useState } from 'react';

interface BlueprintItem {
  id: string;
  title: string;
  industry: string;
  scaling_score: number;
  destination_type: string;
  created_at: string;
}

export default function BlueprintsPage() {
  const [items, setItems] = useState<BlueprintItem[]>([]);
  const [industry, setIndustry] = useState('');
  const [destination, setDestination] = useState('');
  const [minScore, setMinScore] = useState(0);

  const load = async () => {
    const params = new URLSearchParams();
    if (industry) params.set('industry', industry);
    if (destination) params.set('destination_type', destination);
    if (minScore) params.set('min_score', String(minScore));
    const res = await fetch(`/api/backend/api/blueprints?${params.toString()}`);
    const data = await res.json();
    setItems(data.items || []);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Blueprint-Bibliothek</h1>
        <p className="page-subtitle">Filtere und exportiere wiederverwendbare Kampagnenpläne.</p>
      </div>
      <div className="card">
        <h2 className="section-title">Filter</h2>
        <div className="filters">
          <input className="input" placeholder="Branche" value={industry} onChange={(e) => setIndustry(e.target.value)} />
          <select className="select" value={destination} onChange={(e) => setDestination(e.target.value)}>
            <option value="">Zieltyp</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="meta_lead_form">Lead-Formular</option>
            <option value="calculator_quiz">Rechner/Quiz</option>
            <option value="landing_page">Landingpage</option>
          </select>
          <input
            className="input"
            type="number"
            placeholder="Min Score"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
          />
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={load}>Filter anwenden</button>
      </div>
      <div className="card">
        <h2 className="section-title">Blueprints</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Titel</th>
              <th>Branche</th>
              <th>Zieltyp</th>
              <th>Scaling-Score</th>
              <th>Export</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.title}</td>
                <td>{item.industry}</td>
                <td>{item.destination_type}</td>
                <td>{item.scaling_score}</td>
                <td>
                  <a href={`/api/backend/api/blueprints/${item.id}/export.json`} target="_blank" rel="noreferrer">JSON</a>{' '}
                  <a href={`/api/backend/api/blueprints/${item.id}/export.csv`} target="_blank" rel="noreferrer">CSV</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
