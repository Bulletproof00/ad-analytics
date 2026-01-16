'use client';

import { useEffect, useState } from 'react';

export default function AntiBlueprintsPage() {
  const [items, setItems] = useState<any[]>([]);

  const load = async () => {
    const res = await fetch('/api/backend/api/anti-blueprints');
    const data = await res.json();
    setItems(data.items || []);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <h1>Anti-Blueprints</h1>
      <p><strong>Hinweis:</strong> Dies sind proxy-basierte Failure-Muster.</p>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Ad</th>
              <th>Runtime Days</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.ad_id}>
                <td>{item.ad_id}</td>
                <td>{item.runtime_days}</td>
                <td>{item.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
