'use client';

import { useEffect, useState } from 'react';

interface StrengthRow {
  feature: string;
  avg_score: number;
  lift: number;
  sample: number;
}

export default function IntelligencePage() {
  const [strength, setStrength] = useState<{ hook_type: StrengthRow[]; destination_type: StrengthRow[] } | null>(null);
  const [combos, setCombos] = useState<any[]>([]);
  const [trends, setTrends] = useState<{ top_hooks: [string, number][]; top_funnels: [string, number][] } | null>(null);

  const load = async () => {
    const strengthRes = await fetch('/api/backend/api/intelligence/parameter-strength');
    const strengthData = await strengthRes.json();
    setStrength(strengthData);

    const combosRes = await fetch('/api/backend/api/intelligence/pattern-combos');
    const combosData = await combosRes.json();
    setCombos(combosData.items || []);

    const trendsRes = await fetch('/api/backend/api/intelligence/trends');
    const trendsData = await trendsRes.json();
    setTrends(trendsData);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <h1>Intelligence</h1>
      <p><strong>Hinweis:</strong> Alle Metriken sind proxy-basiert, keine echten Lead-Zahlen.</p>

      <div className="card">
        <h2>Parameter Strength</h2>
        <a href="/api/backend/api/intelligence/parameter-strength.csv" target="_blank" rel="noreferrer">Export CSV</a>
        <h3>Hook Types</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Feature</th>
              <th>Avg Score</th>
              <th>Lift</th>
              <th>Sample</th>
            </tr>
          </thead>
          <tbody>
            {strength?.hook_type.map((row) => (
              <tr key={row.feature}>
                <td>{row.feature}</td>
                <td>{row.avg_score}</td>
                <td>{row.lift}</td>
                <td>{row.sample}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Top Pattern Combos</h2>
        <a href="/api/backend/api/intelligence/pattern-combos.csv" target="_blank" rel="noreferrer">Export CSV</a>
        <table className="table">
          <thead>
            <tr>
              <th>Hook</th>
              <th>Destination</th>
              <th>Count</th>
            </tr>
          </thead>
          <tbody>
            {combos.map((combo) => (
              <tr key={`${combo.hook_type}-${combo.destination_type}`}>
                <td>{combo.hook_type}</td>
                <td>{combo.destination_type}</td>
                <td>{combo.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Trends</h2>
        <h3>Top Hooks</h3>
        <ul>
          {trends?.top_hooks.map(([hook, count]) => (
            <li key={hook}>{hook}: {count}</li>
          ))}
        </ul>
        <h3>Top Funnels</h3>
        <ul>
          {trends?.top_funnels.map(([funnel, count]) => (
            <li key={funnel}>{funnel}: {count}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
