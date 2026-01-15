'use client';

import { useEffect, useState } from 'react';
import CopyButton from '../../../components/CopyButton';
import { AdDetail } from '../../../lib/types';

export default function AdDetailPage({ params }: { params: { id: string } }) {
  const [ad, setAd] = useState<AdDetail | null>(null);
  const [saving, setSaving] = useState(false);
  const [tags, setTags] = useState<AdDetail['tags'] | null>(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`/api/backend/api/ads/${params.id}`, { cache: 'no-store' });
      const data = await res.json();
      setAd(data);
      setTags(data.tags);
    };
    load();
  }, [params.id]);

  const updateTag = (field: keyof NonNullable<typeof tags>, value: string | boolean) => {
    if (!tags) return;
    setTags({ ...tags, [field]: value });
  };

  const saveTags = async () => {
    if (!tags) return;
    setSaving(true);
    await fetch(`/api/backend/api/ads/${params.id}/tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tags),
    });
    setSaving(false);
  };

  if (!ad || !tags) return <div className="card">Loading...</div>;

  return (
    <div className="grid">
      <h1>Ad Detail</h1>
      <div className="card">
        <h2>{ad.page_name}</h2>
        <p>Ad Archive ID: {ad.ad_archive_id}</p>
        <p>Start: {ad.start_time?.slice(0, 10)} | Stop: {ad.stop_time?.slice(0, 10) || '-'}</p>
        {ad.snapshot_url && (
          <a href={ad.snapshot_url} target="_blank" rel="noreferrer" className="button">
            Snapshot öffnen
          </a>
        )}
      </div>

      <div className="card">
        <h2>Score Breakdown</h2>
        <p>Total: <strong>{ad.score.score_total}</strong></p>
        <ul>
          <li>Runtime: {ad.score.score_runtime}</li>
          <li>Variants: {ad.score.score_variants}</li>
          <li>Reuse: {ad.score.score_reuse}</li>
          <li>Funnel Fit: {ad.score.score_funnel_fit}</li>
        </ul>
        <pre>{JSON.stringify(ad.score.explanation, null, 2)}</pre>
      </div>

      <div className="card">
        <h2>Hook</h2>
        <p>{ad.hook ?? '-'}</p>
        {ad.hook && <CopyButton text={ad.hook} />}
        <p>Reuse Count: {ad.reuse_count}</p>
        <p>Variants Count: {ad.variants_count}</p>
      </div>

      <div className="card">
        <h2>Copy Bodies</h2>
        {ad.copy_bodies ? (
          <ul>
            {Object.values(ad.copy_bodies).map((text) => (
              <li key={text} style={{ marginBottom: 8 }}>
                <p>{text}</p>
                <CopyButton text={text} />
              </li>
            ))}
          </ul>
        ) : (
          <p>-</p>
        )}
      </div>

      <div className="card">
        <h2>Tags (Override)</h2>
        <div className="filters">
          <input className="input" value={tags.niche} onChange={(e) => updateTag('niche', e.target.value)} />
          <input className="input" value={tags.funnel_type} onChange={(e) => updateTag('funnel_type', e.target.value)} />
          <input className="input" value={tags.offer_type} onChange={(e) => updateTag('offer_type', e.target.value)} />
          <input className="input" value={tags.emotion_trigger} onChange={(e) => updateTag('emotion_trigger', e.target.value)} />
          <label>
            <input
              type="checkbox"
              checked={tags.is_winner}
              onChange={(e) => updateTag('is_winner', e.target.checked)}
            /> Winner
          </label>
          <input className="input" value={tags.notes || ''} onChange={(e) => updateTag('notes', e.target.value)} />
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={saveTags} disabled={saving}>
          {saving ? 'Speichern...' : 'Speichern'}
        </button>
      </div>
    </div>
  );
}
