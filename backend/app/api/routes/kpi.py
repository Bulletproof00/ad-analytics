import csv
import io
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import OwnCampaign
from app.db.session import get_db
from app.schemas import KPIImportRequest

router = APIRouter(prefix="/api/kpi", tags=["kpi"], dependencies=[Depends(require_basic_auth)])


@router.post("/import")
def import_kpi(payload: KPIImportRequest, db: Session = Depends(get_db)) -> dict:
    csv_file = io.StringIO(payload.csv_text)
    reader = csv.DictReader(csv_file)
    rows = []
    for row in reader:
        mapped = {target: row.get(source) for source, target in payload.mapping.items()}
        rows.append(mapped)

    campaign = OwnCampaign(name=payload.name, metrics={"rows": rows})
    db.add(campaign)
    db.commit()
    return {"id": str(campaign.id), "rows": len(rows)}
