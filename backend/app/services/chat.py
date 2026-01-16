from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import Ad, Blueprint, Advertiser
from app.services.hook_extractor import hook_preview


def chat_search(db: Session, query: str) -> dict:
    query_lower = query.lower()
    ad_matches = db.execute(
        select(Ad).join(Advertiser).where(Advertiser.page_name.ilike(f"%{query}%"))
    ).scalars().all()
    blueprint_matches = db.execute(
        select(Blueprint).where(Blueprint.title.ilike(f"%{query}%"))
    ).scalars().all()

    sources = []
    for ad in ad_matches[:5]:
        sources.append(
            {
                "type": "ad",
                "id": str(ad.id),
                "label": ad.advertiser.page_name or "Unknown",
            }
        )
    for blueprint in blueprint_matches[:5]:
        sources.append(
            {
                "type": "blueprint",
                "id": str(blueprint.id),
                "label": blueprint.title,
            }
        )

    if not sources:
        answer = "Keine direkten Treffer. Versuche andere Keywords oder filtere in Ads/Blueprints."
    else:
        answer = f"Gefundene Treffer für '{query_lower}': {len(sources)}."

    return {"answer": answer, "sources": sources}
