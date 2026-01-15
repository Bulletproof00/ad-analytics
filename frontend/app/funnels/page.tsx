'use client';

import { useEffect, useState } from 'react';

interface FunnelItem {
  funnel_type: string;
  count: number;
}

export default function FunnelsPage() {
  const [items, setItems] = useState<FunnelItem[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await fetch('/api/backend/api/funnels', { cache: 'no-store' });
      const data = await res.json();
      setItems(data.items || []);
    };
    load();
  }, []);

  return (
    <div className="grid">
      <h1>Funnel Library</h1>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Funnel Type</th>
              <th>Count</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.funnel_type}>
                <td>{item.funnel_type}</td>
                <td>{item.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
