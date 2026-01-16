'use client';

import { useEffect, useState } from 'react';
import CopyButton from '../../../components/CopyButton';
import { AdDetail } from '../../../lib/types';

export default function AdDetailPage({ params }: { params: { id: string } }) {
  const [ad, setAd] = useState<AdDetail | null>(null);
  const [saving, setSaving] = useState(false);
  const [tags, setTags] = useState<AdDetail['tags'] | null>(null);
  const [blueprint, setBlueprint] = useState<any | null>(null);
  const [blueprintLoading, setBlueprintLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`/api/backend/api/ads/${params.id}`, { cache: 'no-store' });
      const data = await res.json();
      setAd(data);
      setTags(data.tags);
      const bpRes = await fetch(`/api/backend/api/blueprints?source_ad_id=${params.id}`);
      const bpData = await bpRes.json();
      setBlueprint(bpData.items?.[0] || null);
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

  const createBlueprint = async () => {
    setBlueprintLoading(true);
    const res = await fetch('/api/backend/api/blueprints', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sourceAdId: params.id }),
    });
    const data = await res.json();
    const bpRes = await fetch(`/api/backend/api/blueprints/${data.id}`);
    const bpData = await bpRes.json();
    setBlueprint(bpData);
    setBlueprintLoading(false);
  };

  const saveBlueprintSection = async (section: string, payload: any) => {
    if (!blueprint) return;
    const endpoint = section ? `/api/backend/api/blueprints/${blueprint.id}/${section}` : `/api/backend/api/blueprints/${blueprint.id}`;
    await fetch(endpoint, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const refreshed = await fetch(`/api/backend/api/blueprints/${blueprint.id}`);
    setBlueprint(await refreshed.json());
  };

  const captureSnapshot = async () => {
    if (!blueprint?.funnel?.click_url) return;
    await fetch(`/api/backend/api/blueprints/${blueprint.id}/snapshot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: blueprint.funnel.click_url }),
    });
    const refreshed = await fetch(`/api/backend/api/blueprints/${blueprint.id}`);
    setBlueprint(await refreshed.json());
  };

  if (!ad || !tags) return <div className="card">Loading...</div>;

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Anzeige Detail</h1>
        <p className="page-subtitle">Analyse, Tags und Blueprint für diese Anzeige.</p>
      </div>
      <div className="card">
        <h2>{ad.page_name}</h2>
        <p>Ad Archive ID: {ad.ad_archive_id}</p>
        <p>Start: {ad.start_time?.slice(0, 10)} | Ende: {ad.stop_time?.slice(0, 10) || '-'}</p>
        {ad.snapshot_url && (
          <a href={ad.snapshot_url} target="_blank" rel="noreferrer" className="button">
            Snapshot öffnen
          </a>
        )}
      </div>

      <div className="card">
        <h2 className="section-title">Score Breakdown</h2>
        <p>Total: <strong>{ad.score.score_total}</strong></p>
        <ul>
          <li>Runtime: {ad.score.score_runtime}</li>
          <li>Variants: {ad.score.score_variants}</li>
          <li>Reuse: {ad.score.score_reuse}</li>
          <li>Funnel Fit: {ad.score.score_funnel_fit}</li>
          <li>Saturation Index: {ad.score.saturation_index ?? 0}</li>
        </ul>
        <pre>{JSON.stringify(ad.score.explanation, null, 2)}</pre>
      </div>

      <div className="card">
        <h2 className="section-title">Hook</h2>
        <p>{ad.hook ?? '-'}</p>
        {ad.hook && <CopyButton text={ad.hook} />}
        <p>Reuse Count: {ad.reuse_count}</p>
        <p>Variants Count: {ad.variants_count}</p>
      </div>

      <div className="card">
        <h2 className="section-title">Copy Texte</h2>
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
        <h2 className="section-title">Tags (Override)</h2>
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
      <div className="card">
        <h2 className="section-title">Copy Analytics</h2>
        <pre>{JSON.stringify(ad.features || {}, null, 2)}</pre>
      </div>
      <div className="card">
        <h2 className="section-title">Kampagnen-Blueprint</h2>
        {!blueprint && (
          <button className="button" onClick={createBlueprint} disabled={blueprintLoading}>
            {blueprintLoading ? 'Erstelle...' : 'Blueprint erstellen'}
          </button>
        )}
        {blueprint && (
          <div className="grid">
            <div>
              <label>Branche</label>
              <input
                className="input"
                defaultValue={blueprint.industry}
                onBlur={(e) => saveBlueprintSection('', { industry: e.target.value })}
              />
            </div>
            <div>
              <label>Hook-Typ</label>
              <input
                className="input"
                defaultValue={blueprint.creative?.hook_type || 'unknown'}
                onBlur={(e) => saveBlueprintSection('creative-analysis', { hook_type: e.target.value })}
              />
            </div>
            <div>
              <label>CTA-Typ</label>
              <input
                className="input"
                defaultValue={blueprint.creative?.cta_type || 'unknown'}
                onBlur={(e) => saveBlueprintSection('creative-analysis', { cta_type: e.target.value })}
              />
            </div>
          <div>
            <label>Ziel-URL</label>
            <input
              className="input"
              defaultValue={blueprint.funnel?.click_url || ''}
              onBlur={(e) => saveBlueprintSection('funnel-analysis', { click_url: e.target.value })}
            />
          </div>
          <div>
            <button
              className="button secondary"
              onClick={captureSnapshot}
            >
              Snapshot erfassen
            </button>
          </div>
            <div>
              <label>Friction-Level</label>
              <select
                className="select"
                defaultValue={blueprint.funnel?.friction_level || 'unknown'}
                onChange={(e) => saveBlueprintSection('funnel-analysis', { friction_level: e.target.value })}
              >
                <option value="low">niedrig</option>
                <option value="medium">mittel</option>
                <option value="high">hoch</option>
                <option value="unknown">unbekannt</option>
              </select>
            </div>
            <div>
              <label>Primär-Frame</label>
              <input
                className="input"
                defaultValue={blueprint.offer?.primary_frame || 'unknown'}
                onBlur={(e) => saveBlueprintSection('offer-psychology', { primary_frame: e.target.value })}
              />
            </div>
            <div>
              <label>Scaling-Score</label>
              <p>{blueprint.success?.scaling_score ?? 0}</p>
            </div>
            <div>
              <a href={`/api/backend/api/blueprints/${blueprint.id}/export.json`} target="_blank" rel="noreferrer">JSON Export</a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
