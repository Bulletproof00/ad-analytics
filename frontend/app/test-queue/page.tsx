'use client';

import { useEffect, useState } from 'react';

interface QueueItem {
  id: string;
  title: string;
  status: string;
  predicted_success: number;
  recommended_budget: number | null;
  risk_notes: string | null;
}

export default function TestQueuePage() {
  const [items, setItems] = useState<QueueItem[]>([]);

  const load = async () => {
    const res = await fetch('/api/backend/api/agents/test-queue');
    const data = await res.json();
    setItems(data.items || []);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Test-Queue</h1>
        <p className="page-subtitle">Kandidaten für Microtests und Freigaben.</p>
      </div>
      <div className="card">
        <h2 className="section-title">Pipeline</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Titel</th>
              <th>Status</th>
              <th>Erfolgschance</th>
              <th>Budget</th>
              <th>Risiko</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.title}</td>
                <td>{item.status}</td>
                <td>{item.predicted_success}</td>
                <td>{item.recommended_budget ?? '-'}</td>
                <td>{item.risk_notes ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
