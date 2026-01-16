from collections import defaultdict
from difflib import SequenceMatcher
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Ad, Feature, Advertiser
from app.services.hook_extractor import extract_hook


def _copy_text(ad: Ad) -> str:
    if not ad.copy_bodies:
        return ""
    if isinstance(ad.copy_bodies, dict):
        return " ".join([str(v) for v in ad.copy_bodies.values()])
    if isinstance(ad.copy_bodies, list):
        return " ".join([str(v) for v in ad.copy_bodies])
    return ""


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def creative_lineage(db: Session, advertiser_id: str) -> dict:
    ads = db.execute(select(Ad).where(Ad.advertiser_id == advertiser_id)).scalars().all()
    lineage = defaultdict(list)
    for ad in ads:
        hook = extract_hook(ad.copy_bodies) or "unknown"
        lineage[hook].append(ad)

    output = []
    for hook, group in lineage.items():
        group_sorted = sorted(group, key=lambda a: a.start_time or a.created_at)
        versions = []
        for idx, ad in enumerate(group_sorted):
            copy = _copy_text(ad)
            similarity = None
            if idx > 0:
                prev_copy = _copy_text(group_sorted[idx - 1])
                similarity = round(_similarity(prev_copy, copy), 3)
            versions.append(
                {
                    "ad_id": str(ad.id),
                    "start_time": ad.start_time,
                    "stop_time": ad.stop_time,
                    "hook": hook,
                    "copy_similarity": similarity,
                }
            )
        output.append({"hook": hook, "versions": versions})
    return {"advertiser_id": advertiser_id, "lineage": output}
