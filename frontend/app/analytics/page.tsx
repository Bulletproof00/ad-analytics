'use client';

import { useEffect, useState } from 'react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface OverviewResponse {
  trends: { date: string; new_ads: number }[];
  funnel_share: { funnel_type: string; count: number; share: number }[];
}

export default function AnalyticsPage() {
  const [data, setData] = useState<OverviewResponse | null>(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch('/api/backend/api/analytics/overview?days=90', { cache: 'no-store' });
      const json = await res.json();
      setData(json);
    };
    load();
  }, []);

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Analytics Hub</h1>
        <p className="page-subtitle">Zeitreihen, Funnel-Verteilung und Markttrends.</p>
      </div>
      <div className="card">
        <h2 className="section-title">Marktübersicht</h2>
        <p className="helper-text">Funnel-Verteilung und Zeitreihen-Drilldowns.</p>
      </div>
      <div className="card">
        <h3 className="section-title">Neue Ads im Zeitverlauf</h3>
        <div style={{ width: '100%', height: 260 }}>
          <ResponsiveContainer>
            <LineChart data={data?.trends || []}>
              <XAxis dataKey="date" hide />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="new_ads" stroke="#1a4fd8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
