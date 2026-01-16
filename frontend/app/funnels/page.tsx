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
      <div>
        <h1 className="page-title">Funnel-Bibliothek</h1>
        <p className="page-subtitle">Übersicht der Funnel-Typen im Markt.</p>
      </div>
      <div className="card">
        <h2 className="section-title">Funnel Übersicht</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Funnel-Typ</th>
              <th>Anzahl</th>
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
