'use client';

import { useState } from 'react';

export default function CreativeEvolutionPage() {
  const [advertiserId, setAdvertiserId] = useState('');
  const [data, setData] = useState<any | null>(null);

  const load = async () => {
    const res = await fetch(`/api/backend/api/creative-evolution?advertiser_id=${advertiserId}`);
    setData(await res.json());
  };

  return (
    <div className="grid">
      <h1>Creative Evolution</h1>
      <p><strong>Hinweis:</strong> Alle Metriken sind proxy-basiert.</p>
      <div className="card">
        <input className="input" placeholder="Advertiser ID" value={advertiserId} onChange={(e) => setAdvertiserId(e.target.value)} />
        <button className="button" style={{ marginTop: 12 }} onClick={load}>Load Lineage</button>
      </div>
      {data && (
        <div className="card">
          {data.lineage?.map((group: any) => (
            <div key={group.hook} style={{ marginBottom: 16 }}>
              <h3>{group.hook}</h3>
              <ul>
                {group.versions.map((version: any) => (
                  <li key={version.ad_id}>
                    {version.ad_id} — similarity: {version.copy_similarity ?? 'n/a'}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
