from datetime import datetime
import copy
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Setting

DEFAULT_SETTINGS = {
    "scanning": {
        "default_country": "DE",
        "default_since_days": 90,
        "status": "ALL",
        "max_results_per_keyword": 2000,
        "rate_limit_max_retries": 5,
        "rate_limit_base_sleep_ms": 500,
        "keyword_presets": {
            "pet": [
                "tierkrankenversicherung",
                "hundekrankenversicherung",
                "katzenkrankenversicherung",
                "op versicherung hund",
                "op versicherung katze",
                "tierarzt kosten",
                "hund op kosten",
                "katze op kosten",
                "tierarzt rechnung",
                "vierbeiner schutz",
                "ohne wartezeit tier",
                "ab 20 € tierkrankenversicherung",
            ]
        },
    },
    "scoring": {
        "weights": {"runtime": 0.4, "variants": 0.3, "reuse": 0.2, "funnel_fit": 0.1},
        "winner_threshold": 75,
        "funnel_fit": {"whatsapp": 80, "instant_form": 70, "landing_page": 75, "unknown": 40},
        "saturation_penalty": {"warn": 60, "critical": 80},
    },
    "analytics": {"trend_windows": [7, 14, 30], "cohort_bucket": "weekly"},
    "agents": {"rules_only": True, "language": "de", "enabled": [
        "market_pattern",
        "hook_generator",
        "winner_prediction",
        "strategy_budget",
        "explainability",
        "market_saturation",
        "differentiation",
    ]},
    "budget_rules": {
        "default_microtest_budget": 100,
        "kill_rules": [{"metric": "cpl", "operator": ">", "value": 80}],
        "scale_rules": [{"metric": "cpl", "operator": "<", "value": 40}],
    },
}


def get_settings(db: Session, scope: str = "global") -> dict:
    rows = db.execute(select(Setting).where(Setting.scope == scope)).scalars().all()
    settings = copy.deepcopy(DEFAULT_SETTINGS)
    for row in rows:
        settings.setdefault(row.key, row.value)
        settings[row.key] = row.value
    return settings


def upsert_setting(db: Session, key: str, value: dict, scope: str = "global") -> Setting:
    row = db.execute(
        select(Setting).where(Setting.scope == scope).where(Setting.key == key)
    ).scalar_one_or_none()
    now = datetime.utcnow()
    if row:
        row.value = value
        row.updated_at = now
        db.add(row)
        return row
    row = Setting(scope=scope, key=key, value=value, updated_at=now)
    db.add(row)
    return row
