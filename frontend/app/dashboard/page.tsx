'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AdListItem, StatsResponse } from '../../lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [winners, setWinners] = useState<AdListItem[]>([]);

  useEffect(() => {
    const load = async () => {
      const statsRes = await fetch('/api/backend/api/stats', { cache: 'no-store' });
      const statsJson = await statsRes.json();
      setStats(statsJson);

      const winnersRes = await fetch('/api/backend/api/ads?min_score=75&page_size=10', {
        cache: 'no-store',
      });
      const winnersJson = await winnersRes.json();
      setWinners(winnersJson.items || []);
    };
    load();
  }, []);

  return (
    <div className="grid">
      <h1>Dashboard</h1>
      <div className="grid grid-2">
        <div className="card">
          <h3>Total Ads</h3>
          <p>{stats?.total_ads ?? '-'}</p>
        </div>
        <div className="card">
          <h3>Total Pages</h3>
          <p>{stats?.total_pages ?? '-'}</p>
        </div>
        <div className="card">
          <h3>Winners</h3>
          <p>{stats?.winners_count ?? '-'}</p>
        </div>
        <div className="card">
          <h3>Neue Ads (7d)</h3>
          <p>{stats?.new_ads_last_7d ?? '-'}</p>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Top Winners</h2>
          <Link className="button" href="/scan">Neuer Scan</Link>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Score</th>
              <th>Page</th>
              <th>Hook</th>
              <th>Funnel</th>
              <th>Open</th>
            </tr>
          </thead>
          <tbody>
            {winners.map((item) => (
              <tr key={item.id}>
                <td>{item.score_total}</td>
                <td>{item.page_name}</td>
                <td>{item.hook_preview}</td>
                <td>{item.funnel_type}</td>
                <td>
                  <Link href={`/ads/${item.id}`}>Öffnen</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
