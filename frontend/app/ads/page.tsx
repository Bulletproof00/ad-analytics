'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AdListItem } from '../../lib/types';

export default function AdsPage() {
  const [items, setItems] = useState<AdListItem[]>([]);
  const [minScore, setMinScore] = useState(0);
  const [query, setQuery] = useState('');
  const [winnerOnly, setWinnerOnly] = useState(false);
  const [funnelType, setFunnelType] = useState('');
  const [offerType, setOfferType] = useState('');
  const [emotionTrigger, setEmotionTrigger] = useState('');
  const [niche, setNiche] = useState('');

  const load = async () => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (minScore) params.set('min_score', String(minScore));
    if (winnerOnly) params.set('is_winner', 'true');
    if (funnelType) params.set('funnel_type', funnelType);
    if (offerType) params.set('offer_type', offerType);
    if (emotionTrigger) params.set('emotion_trigger', emotionTrigger);
    if (niche) params.set('niche', niche);

    const res = await fetch(`/api/backend/api/ads?${params.toString()}`, { cache: 'no-store' });
    const data = await res.json();
    setItems(data.items || []);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <h1>Ads</h1>
      <div className="card">
        <div className="filters">
          <input className="input" placeholder="Search" value={query} onChange={(e) => setQuery(e.target.value)} />
          <input
            className="input"
            type="number"
            min={0}
            max={100}
            placeholder="Min Score"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
          />
          <select className="select" value={funnelType} onChange={(e) => setFunnelType(e.target.value)}>
            <option value="">Funnel Type</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="instant_form">Instant Form</option>
            <option value="landing_page">Landing Page</option>
            <option value="unknown">Unknown</option>
          </select>
          <select className="select" value={offerType} onChange={(e) => setOfferType(e.target.value)}>
            <option value="">Offer Type</option>
            <option value="price">Price</option>
            <option value="bonus">Bonus</option>
            <option value="no_waiting">No Waiting</option>
            <option value="testsieger">Testsieger</option>
            <option value="cost_shock">Cost Shock</option>
          </select>
          <select className="select" value={emotionTrigger} onChange={(e) => setEmotionTrigger(e.target.value)}>
            <option value="">Emotion Trigger</option>
            <option value="cost_shock">Cost Shock</option>
            <option value="fear">Fear</option>
            <option value="care">Care</option>
            <option value="relief">Relief</option>
          </select>
          <select className="select" value={niche} onChange={(e) => setNiche(e.target.value)}>
            <option value="">Niche</option>
            <option value="dog">Dog</option>
            <option value="cat">Cat</option>
            <option value="pet">Pet</option>
            <option value="zahn">Zahn</option>
            <option value="rs">RS</option>
            <option value="unknown">Unknown</option>
          </select>
          <label>
            <input type="checkbox" checked={winnerOnly} onChange={(e) => setWinnerOnly(e.target.checked)} /> Winner only
          </label>
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={load}>Filter anwenden</button>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Score</th>
              <th>Page</th>
              <th>Start</th>
              <th>Stop</th>
              <th>Hook</th>
              <th>Funnel</th>
              <th>Offer</th>
              <th>Snapshot</th>
              <th>Open</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.score_total}</td>
                <td>{item.page_name}</td>
                <td>{item.start_time?.slice(0, 10)}</td>
                <td>{item.stop_time?.slice(0, 10) || '-'}</td>
                <td>{item.hook_preview}</td>
                <td>{item.funnel_type}</td>
                <td>{item.offer_type}</td>
                <td>
                  {item.snapshot_url ? (
                    <a href={item.snapshot_url} target="_blank" rel="noreferrer">Link</a>
                  ) : (
                    '-'
                  )}
                </td>
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
