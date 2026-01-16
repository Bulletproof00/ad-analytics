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
  const [minRuntime, setMinRuntime] = useState(0);
  const [minReuse, setMinReuse] = useState(0);
  const [minVariants, setMinVariants] = useState(0);

  const load = async () => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (minScore) params.set('min_score', String(minScore));
    if (winnerOnly) params.set('is_winner', 'true');
    if (funnelType) params.set('funnel_type', funnelType);
    if (offerType) params.set('offer_type', offerType);
    if (emotionTrigger) params.set('emotion_trigger', emotionTrigger);
    if (niche) params.set('niche', niche);
    if (minRuntime) params.set('min_runtime', String(minRuntime));
    if (minReuse) params.set('min_reuse', String(minReuse));
    if (minVariants) params.set('min_variants', String(minVariants));

    const res = await fetch(`/api/backend/api/ads?${params.toString()}`, { cache: 'no-store' });
    const data = await res.json();
    setItems(data.items || []);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Ads Explorer</h1>
        <p className="page-subtitle">Filtere, vergleiche und öffne einzelne Anzeigen.</p>
      </div>
      <div className="card">
        <h2 className="section-title">Filter</h2>
        <div className="filters">
          <input className="input" placeholder="Suche" value={query} onChange={(e) => setQuery(e.target.value)} />
          <input
            className="input"
            type="number"
            min={0}
            max={100}
            placeholder="Min. Score"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
          />
          <select className="select" value={funnelType} onChange={(e) => setFunnelType(e.target.value)}>
            <option value="">Funnel-Typ</option>
            <option value="whatsapp">WhatsApp</option>
            <option value="instant_form">Instant Form</option>
            <option value="landing_page">Landingpage</option>
            <option value="unknown">Unbekannt</option>
          </select>
          <select className="select" value={offerType} onChange={(e) => setOfferType(e.target.value)}>
            <option value="">Offer-Typ</option>
            <option value="price">Preis</option>
            <option value="bonus">Bonus</option>
            <option value="no_waiting">Ohne Wartezeit</option>
            <option value="testsieger">Testsieger</option>
            <option value="cost_shock">Kosten-Schock</option>
          </select>
          <select className="select" value={emotionTrigger} onChange={(e) => setEmotionTrigger(e.target.value)}>
            <option value="">Emotion</option>
            <option value="cost_shock">Kosten-Schock</option>
            <option value="fear">Angst</option>
            <option value="care">Fürsorge</option>
            <option value="relief">Erleichterung</option>
          </select>
          <select className="select" value={niche} onChange={(e) => setNiche(e.target.value)}>
            <option value="">Nische</option>
            <option value="dog">Hund</option>
            <option value="cat">Katze</option>
            <option value="pet">Haustier</option>
            <option value="zahn">Zahn</option>
            <option value="rs">RS</option>
            <option value="unknown">Unbekannt</option>
          </select>
          <input
            className="input"
            type="number"
            min={0}
            placeholder="Min. Laufzeit (Tage)"
            value={minRuntime}
            onChange={(e) => setMinRuntime(Number(e.target.value))}
          />
          <input
            className="input"
            type="number"
            min={0}
            placeholder="Min. Reuse"
            value={minReuse}
            onChange={(e) => setMinReuse(Number(e.target.value))}
          />
          <input
            className="input"
            type="number"
            min={0}
            placeholder="Min. Varianten"
            value={minVariants}
            onChange={(e) => setMinVariants(Number(e.target.value))}
          />
          <label>
            <input type="checkbox" checked={winnerOnly} onChange={(e) => setWinnerOnly(e.target.checked)} /> Nur Winners
          </label>
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={load}>Filter anwenden</button>
      </div>

      <div className="card">
        <h2 className="section-title">Ergebnisse</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Score</th>
              <th>Page</th>
              <th>Start</th>
              <th>Stop</th>
              <th>Hook</th>
              <th>Funnel</th>
              <th>Angebot</th>
              <th>Reuse</th>
              <th>Varianten</th>
              <th>Snapshot</th>
              <th>Öffnen</th>
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
                <td>{item.score_reuse ?? '-'}</td>
                <td>{item.score_variants ?? '-'}</td>
                <td>
                  {item.snapshot_url ? (
                    <a href={item.snapshot_url} target="_blank" rel="noreferrer">Link</a>
                  ) : (
                    '-'
                  )}
                </td>
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
