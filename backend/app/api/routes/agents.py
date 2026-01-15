from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.models import AgentRun, TestQueueItem
from app.db.session import get_db
from app.schemas import AgentRunRequest, AgentRunResponse
from app.services.agents import run_agent, build_test_queue_item

router = APIRouter(prefix="/api/agents", tags=["agents"], dependencies=[Depends(require_basic_auth)])


@router.post("/run", response_model=AgentRunResponse)
def run_agent_route(payload: AgentRunRequest, db: Session = Depends(get_db)) -> AgentRunResponse:
    run = run_agent(db, payload.agent_name, payload.params)
    db.commit()
    return AgentRunResponse(
        id=str(run.id),
        agent_name=run.agent_name,
        status=run.status,
        output=run.output or {},
        evidence=run.evidence or {},
        created_at=run.created_at,
    )


@router.get("")
def list_runs(db: Session = Depends(get_db)) -> dict:
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).limit(50).all()
    return {
        "items": [
            {
                "id": str(run.id),
                "agent_name": run.agent_name,
                "status": run.status,
                "created_at": run.created_at,
            }
            for run in runs
        ]
    }


@router.post("/test-queue")
def create_test_queue(payload: dict, db: Session = Depends(get_db)) -> dict:
    item = build_test_queue_item(db, payload.get("title", "Test Item"), payload)
    db.commit()
    return {"id": str(item.id)}


@router.get("/test-queue")
def list_test_queue(db: Session = Depends(get_db)) -> dict:
    items = db.query(TestQueueItem).order_by(TestQueueItem.created_at.desc()).all()
    return {
        "items": [
            {
                "id": str(item.id),
                "title": item.title,
                "status": item.status,
                "predicted_success": item.predicted_success,
                "recommended_budget": item.recommended_budget,
                "risk_notes": item.risk_notes,
            }
            for item in items
        ]
    }
