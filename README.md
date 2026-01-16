# AdRadar OS Pro

AdRadar OS Pro ist ein datengetriebenes Operating System für profitable Meta-Leadgenerierung in Deutschland (DE). Es sammelt Markt-Ads aus der offiziellen Meta Ad Library API, extrahiert Features, berechnet erklärbare Proxy-Scores und liefert ein starkes Analytics-Dashboard mit Agenten, Test-Queue und Autopilot-Export (Human-in-the-loop).

## Phasen-Überblick

1. **Market Memory**: Ads ingest, Features extrahieren, Scores, Hook Library, Scan-Coverage.
2. **Deep Analytics**: Zeitachsen, Copy Analytics, Funnel Trends, Sättigung, Korrelationen.
3. **KI-Agenten (rules-first)**: Muster, Hook-Varianten, Winner Prediction, Budget/Strategy, Explainability.
4. **Own KPI Integration**: CSV Import + Calibration (Proxy Score ↔ CPL-Bänder).
5. **Autopilot Export**: Kampagnenpakete mit Freigabe, kein Live-Publishing.

## Grenzen (Compliance)

- **Kein Scraping**: Nur offizielle Meta Ad Library API.
- **Keine fremden KPIs**: CPL/ROAS werden nicht geschätzt.
- **Erklärbarkeit**: Jede Empfehlung trägt Evidence (ad_ids, hook_hash, deltas).
- **Human-in-the-loop**: Autopilot liefert nur Exportpakete.

## Setup

```bash
cp .env.example .env
# META_ACCESS_TOKEN setzen

docker compose up --build
```

UI: `http://localhost:3000`

## Erste Schritte

1. Öffne **/settings** und prüfe Keyword-Presets.
2. Starte **/scan** mit dem Preset für Tierkrankenversicherung.
3. Öffne **/dashboard** und prüfe KPIs, Trends, Alerts.
4. Nutze **/ads** für Filter/Drilldowns, **/hooks** für Hook Library.

## Keyword Preset (Tierkrankenversicherung DE)

- tierkrankenversicherung
- hundekrankenversicherung
- katzenkrankenversicherung
- op versicherung hund
- op versicherung katze
- tierarzt kosten
- hund op kosten
- katze op kosten
- tierarzt rechnung
- vierbeiner schutz
- ohne wartezeit tier
- ab 20 € tierkrankenversicherung

## Score-Logik

```
score_total = 0.4*runtime + 0.3*variants + 0.2*reuse + 0.1*funnel_fit
runtime = min(100, runtime_days*4)
variants = min(100, variants_count*20)
reuse = min(100, reuse_count*25)
funnel_fit = whatsapp 80 | instant_form 70 | landing_page 75 | unknown 40
```

Zusätzlich wird ein **saturation_index** berechnet (Hook-Reuse + Wachstumsrate der Pages in den letzten 14 Tagen). Dieser Index wirkt sich auf Empfehlungen aus, nicht auf `score_total`.

## Dashboard-Guide

- **Command Center**: KPI-Karten + Trendpanel + Alerts.
- **Ads Explorer**: filterbar nach Score, Runtime, Reuse, Variants, Emotion, Funnel.
- **Hook Library**: Hooks nach Reuse, Beispiele, Copy-Buttons.
- **Analytics Hub**: Zeitreihen & Marktverlauf.
- **Agents**: Rules-first Reports, optional LLM für Textvarianten.
- **Test Queue**: Kandidaten für Microtests.
- **Export**: Campaign-Bundle als JSON/Markdown.
- **Blueprints**: Campaign Blueprint Engine (CBE) mit Creative/Funnel/Offer Analysis.

## Campaign Blueprint Engine (CBE)

Die CBE erweitert AdRadar um wiederverwendbare Kampagnen-Blaupausen:
- **Creative Analysis**: Hook, Story-Struktur, POV, CTA, Emotionen.
- **Funnel Analysis**: Destination-Typ, Friction-Level, Snapshot (HTML).
- **Offer & Psychology**: Preis, Bonus, Urgency, Framing.
- **Success Signals**: Laufzeit, Varianten, Scaling-Score mit Breakdown.

Snapshots sind **user-triggered** und werden mit SSRF-Schutz gespeichert. HTML wird lokal unter `/data/snapshots/` abgelegt.

## MVP vs Next

**MVP**: Rule-based Tagging, HTML-Snapshots, JSON/CSV Export, einfache Filter.

**Next**: OCR/Screenshot, Hook-Cluster, Compare-Mode, Auto-Insights.

## Agents (rules-first)

Agenten liefern strukturierte, erklärbare Outputs und speichern Runs:
- Market Pattern
- Hook Generator
- Winner Prediction
- Strategy & Budget
- Explainability
- Market Saturation
- Differentiation

## CSV KPI Import (Phase 4 MVP)

`POST /api/kpi/import` akzeptiert CSV + Mapping. Ergebnisse werden in `own_campaigns` gespeichert.

## Architektur

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

## Meta API Felder

Das System fragt defensive Felder an; missing fields werden als `None` gespeichert:
- ad_archive_id, page_id, page_name
- ad_delivery_start_time, ad_delivery_stop_time
- ad_snapshot_url
- ad_creative_bodies, ad_creative_link_titles, ad_creative_link_descriptions, ad_creative_link_captions
- publisher_platforms, platforms, languages

## Roadmap

- Meta Insights API für eigene KPIs (optional)
- Advanced Cohort Analytics + Survival Curves
- UI Vergleichsmodi für Hooks & Funnels
