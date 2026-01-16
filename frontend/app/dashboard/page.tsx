'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, PieChart, Pie, Cell } from 'recharts';
import KpiCard from '../../components/KpiCard';

const COLORS = ['#1a4fd8', '#14b8a6', '#f97316', '#e11d48'];

interface OverviewResponse {
  kpis: {
    total_ads: number;
    total_pages: number;
    new_ads: number;
    active_ads: number;
    winners: number;
    market_velocity: number;
    saturation_avg: number;
    coverage_health: number;
  };
  trends: { date: string; new_ads: number }[];
  funnel_share: { funnel_type: string; count: number; share: number }[];
  top_hooks: { hook_hash: string; hook_text: string; reuse_count: number }[];
  alerts: { id: string; severity: string; title: string; message: string }[];
}

export default function DashboardPage() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [winners, setWinners] = useState<any[]>([]);
  const [range, setRange] = useState(30);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`/api/backend/api/analytics/overview?days=${range}`, { cache: 'no-store' });
      const data = await res.json();
      setOverview(data);
      const winnersRes = await fetch('/api/backend/api/ads?min_score=75&page_size=10', { cache: 'no-store' });
      const winnersJson = await winnersRes.json();
      setWinners(winnersJson.items || []);
    };
    load();
  }, [range]);

  const trendData = useMemo(() => overview?.trends ?? [], [overview]);
  const funnelData = useMemo(() => overview?.funnel_share ?? [], [overview]);

  return (
    <div className="grid">
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ marginBottom: 4 }}>Command Center</h1>
          <p style={{ color: '#6b7280' }}>Meta Ads Marktgedächtnis für DE</p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <select className="select" value={range} onChange={(e) => setRange(Number(e.target.value))}>
            <option value={7}>7d</option>
            <option value={14}>14d</option>
            <option value={30}>30d</option>
            <option value={90}>90d</option>
            <option value={365}>365d</option>
          </select>
          <Link className="button" href="/scan">Run Scan</Link>
        </div>
      </div>

      <div className="grid grid-2">
        <KpiCard title="Total Ads" value={overview?.kpis.total_ads ?? '-'} delta="+3%" />
        <KpiCard title="New Ads" value={overview?.kpis.new_ads ?? '-'} delta="+5%" />
        <KpiCard title="Active Ads" value={overview?.kpis.active_ads ?? '-'} delta="+1%" />
        <KpiCard title="Unique Pages" value={overview?.kpis.total_pages ?? '-'} />
        <KpiCard title="Winners" value={overview?.kpis.winners ?? '-'} />
        <KpiCard title="Market Velocity" value={overview?.kpis.market_velocity ?? '-'} />
        <KpiCard title="Saturation Avg" value={overview?.kpis.saturation_avg ?? '-'} />
        <KpiCard title="Coverage Health" value={overview?.kpis.coverage_health ?? '-'} />
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>New Ads Trend</h2>
          <div style={{ width: '100%', height: 240 }}>
            <ResponsiveContainer>
              <LineChart data={trendData}>
                <XAxis dataKey="date" hide />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="new_ads" stroke="#1a4fd8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <h2>Funnel Share</h2>
          <div style={{ width: '100%', height: 240 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={funnelData} dataKey="count" nameKey="funnel_type" outerRadius={80}>
                  {funnelData.map((entry, index) => (
                    <Cell key={entry.funnel_type} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>What Changed</h2>
          <ul>
            {overview?.top_hooks.map((hook) => (
              <li key={hook.hook_hash} style={{ marginBottom: 8 }}>
                <strong>{hook.hook_text}</strong> — Reuse {hook.reuse_count}
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h2>Alerts</h2>
          <ul>
            {overview?.alerts.map((alert) => (
              <li key={alert.id} style={{ marginBottom: 8 }}>
                <strong>{alert.severity.toUpperCase()}</strong> {alert.title}
                <p style={{ margin: 0, color: '#6b7280' }}>{alert.message}</p>
              </li>
            ))}
            {!overview?.alerts.length && <p>No open alerts.</p>}
          </ul>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Top Winners</h2>
          <Link className="button" href="/ads">Open Ads Explorer</Link>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Score</th>
              <th>Page</th>
              <th>Hook</th>
              <th>Funnel</th>
              <th>Reuse</th>
              <th>Variants</th>
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
                <td>{item.score_reuse}</td>
                <td>{item.score_variants}</td>
                <td>
                  <Link href={`/ads/${item.id}`}>Open</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
