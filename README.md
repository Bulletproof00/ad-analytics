# AdRadar

AdRadar ist ein datengetriebenes Marktgedächtnis für Meta-Ads (Facebook/Instagram) in Deutschland. Es sammelt über die offizielle Meta Ad Library API Beobachtungsdaten zu Ads, Hooks, Offers und Funnel-Strukturen, um eine heuristische Erfolgswahrscheinlichkeit abzuleiten – ohne echte Performance-KPIs wie CPL/ROAS.

## Warum AdRadar?

Grundprinzip: Schlechte Ads werden abgeschaltet. Gute Ads laufen länger, werden variiert, repliziert und über mehrere Pages hinweg wiederverwendet. AdRadar misst dieses Verhalten systematisch und macht daraus verwertbare Signale.

**Was AdRadar beantwortet:**
1. Welche Ads laufen lange (Laufzeit als Erfolgssignal)?
2. Welche Ads werden in Varianten getestet (Winner-Optimization Signale)?
3. Welche Hooks/Offers tauchen seitenübergreifend auf (Marktvalidierung)?
4. Welche Funnel-Typen dominieren (WhatsApp vs Instant Form vs Landingpage)?
5. Welche emotionalen Trigger dominieren (Kosten-Schock, Angst, Fürsorge, Erleichterung)?

## Limitations

- Keine echten KPIs (CPL/ROAS/Spend) für normale Ads.
- Abdeckung ist nicht 100% garantiert; die Meta API ist keyword-basiert.
- Deep Crawl über Page-Filter ist eingeschränkt (falls der Parameter nicht verfügbar ist, nutzt das System breite Keyword-Cluster).

## Setup

1. `.env.example` kopieren:
   ```bash
   cp .env.example .env
   ```
2. `META_ACCESS_TOKEN` in `.env` setzen.
3. Start:
   ```bash
   docker compose up --build
   ```
4. UI öffnen: `http://localhost:3000`

## Example Keyword Sets (Tierkrankenversicherung DE)

```
tierkrankenversicherung
hundekrankenversicherung
katzenkrankenversicherung
op versicherung hund
op versicherung katze
tierarzt kosten
hund op kosten
katze op kosten
tierarzt rechnung
vierbeiner schutz
ohne wartezeit tier
ab 20 € tierkrankenversicherung
```

## Score-Logik (transparent & deterministic)

- Runtime: `score_runtime = min(100, runtime_days * 4)`
- Variants: `score_variants = min(100, variants_count * 20)`
- Reuse: `score_reuse = min(100, reuse_count * 25)`
- Funnel Fit: whatsapp=80, instant_form=70, landing_page=75, unknown=40
- Gesamt: `0.4*runtime + 0.3*variants + 0.2*reuse + 0.1*funnel_fit`

Die Erklärung wird im API-Response als `score.explanation` gespeichert.

## How to use outputs to build campaigns

- **Hook Library**: wiederkehrende Einstiege als Inspiration für neue Hooks.
- **Top Winners**: bieten Einblick in Offers, Funnel-Typen und Emotional Triggers.
- **Ad Detail**: Score-Breakdown für Kopie, Hook und Funnel-Einschätzung.

## API Overview (MVP)

- `POST /api/scan` startet Keyword-Cluster-Scans.
- `GET /api/scan/{scan_id}` zeigt Progress + Errors.
- `GET /api/ads` liefert Filter + Pagination.
- `GET /api/ads/{id}` zeigt Ad-Detail + Score.
- `POST /api/ads/{id}/tags` speichert manuelle Overrides.
- `GET /api/hooks` liefert Hook-Library.
- `GET /api/stats` liefert KPI Overview.

## Meta API Fields

Das System fragt defensive Felder an; nicht vorhandene Felder werden als `None` gespeichert. Unterstützte Felder:
- `ad_archive_id`, `page_id`, `page_name`
- `ad_delivery_start_time`, `ad_delivery_stop_time`
- `ad_snapshot_url`
- `ad_creative_bodies`, `ad_creative_link_titles`, `ad_creative_link_descriptions`, `ad_creative_link_captions`
- `publisher_platforms`, `platforms`, `languages`

## Struktur

```
backend/
  app/
    api/routes
    services
    db
    migrations
  tests/
frontend/
  app/
  components/
  lib/
```
