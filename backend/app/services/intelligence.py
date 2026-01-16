from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Blueprint, CreativeAnalysis, FunnelAnalysis, SuccessSignals

_CACHE: dict[str, dict] = {}


def _cache_get(key: str) -> dict | None:
    return _CACHE.get(key)


def _cache_set(key: str, value: dict) -> None:
    _CACHE[key] = value


def clear_cache() -> None:
    _CACHE.clear()


def parameter_strength(db: Session, industry: str | None = None) -> dict:
    cache_key = f"strength:{industry or 'all'}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    blueprints = db.execute(select(Blueprint)).scalars().all()
    rows = []
    for blueprint in blueprints:
        if industry and blueprint.industry != industry:
            continue
        if not blueprint.success:
            continue
        hook_type = blueprint.creative.hook_type if blueprint.creative else "unknown"
        dest = blueprint.funnel.destination_type if blueprint.funnel else "unknown"
        score = blueprint.success.scaling_score
        rows.append({"hook_type": hook_type, "destination_type": dest, "score": score})

    total_avg = sum(row["score"] for row in rows) / max(len(rows), 1)
    hook_stats: dict[str, list[int]] = {}
    dest_stats: dict[str, list[int]] = {}
    for row in rows:
        hook_stats.setdefault(row["hook_type"], []).append(row["score"])
        dest_stats.setdefault(row["destination_type"], []).append(row["score"])

    result = {
        "hook_type": [
            {
                "feature": key,
                "avg_score": round(sum(values) / len(values), 2),
                "lift": round(sum(values) / len(values) - total_avg, 2),
                "sample": len(values),
            }
            for key, values in hook_stats.items()
        ],
        "destination_type": [
            {
                "feature": key,
                "avg_score": round(sum(values) / len(values), 2),
                "lift": round(sum(values) / len(values) - total_avg, 2),
                "sample": len(values),
            }
            for key, values in dest_stats.items()
        ],
    }
    _cache_set(cache_key, result)
    return result


def pattern_combos(db: Session, industry: str | None = None) -> list[dict]:
    blueprints = db.execute(select(Blueprint)).scalars().all()
    combos = Counter()
    for blueprint in blueprints:
        if industry and blueprint.industry != industry:
            continue
        if not blueprint.success:
            continue
        hook_type = blueprint.creative.hook_type if blueprint.creative else "unknown"
        dest = blueprint.funnel.destination_type if blueprint.funnel else "unknown"
        key = (hook_type, dest)
        combos[key] += 1
    return [
        {"hook_type": key[0], "destination_type": key[1], "count": count}
        for key, count in combos.most_common(10)
    ]


def trend_overview(db: Session, days: int = 90) -> dict:
    start = datetime.utcnow() - timedelta(days=days)
    blueprints = db.execute(select(Blueprint)).scalars().all()
    hooks = Counter()
    funnels = Counter()
    for blueprint in blueprints:
        if blueprint.created_at < start:
            continue
        hooks[blueprint.creative.hook_type if blueprint.creative else "unknown"] += 1
        funnels[blueprint.funnel.destination_type if blueprint.funnel else "unknown"] += 1
    return {
        "top_hooks": hooks.most_common(5),
        "top_funnels": funnels.most_common(5),
    }
