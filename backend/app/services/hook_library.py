from collections import defaultdict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Ad, HookLibrary
from app.services.hook_extractor import collect_hooks


def update_hook_library(db: Session) -> None:
    ads = db.execute(select(Ad)).scalars().all()
    hook_map: dict[str, dict] = defaultdict(lambda: {
        "hook_text": None,
        "advertisers": set(),
        "ads": [],
    })

    for ad in ads:
        hook, hook_hash = collect_hooks(ad.copy_bodies)
        if not hook_hash or not hook:
            continue
        entry = hook_map[hook_hash]
        entry["hook_text"] = hook
        entry["advertisers"].add(ad.advertiser_id)
        entry["ads"].append(ad)

    now = datetime.utcnow()
    existing = {h.hook_hash: h for h in db.execute(select(HookLibrary)).scalars().all()}
    for hook_hash, data in hook_map.items():
        ads_sorted = sorted(
            data["ads"],
            key=lambda ad: (ad.score.score_total if ad.score else 0, ad.start_time or now),
            reverse=True,
        )
        example_ids = [str(ad.id) for ad in ads_sorted[:10]]
        hook = existing.get(hook_hash)
        if hook:
            hook.hook_text = data["hook_text"]
            hook.reuse_count = len(data["advertisers"])
            hook.example_ad_ids = example_ids
            hook.updated_at = now
        else:
            hook = HookLibrary(
                hook_text=data["hook_text"],
                hook_hash=hook_hash,
                reuse_count=len(data["advertisers"]),
                example_ad_ids=example_ids,
                created_at=now,
                updated_at=now,
            )
            db.add(hook)

    db.flush()
