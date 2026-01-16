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
      <h1>Test Queue</h1>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Predicted Success</th>
              <th>Budget</th>
              <th>Risk</th>
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
