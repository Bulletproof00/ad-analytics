from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import AgentRun, HookLibrary, Score, Feature, Ad, TestQueueItem
from app.services.analytics import top_hooks_growth, kpi_snapshot


def run_agent(db: Session, agent_name: str, params: dict) -> AgentRun:
    evidence = {}
    output = {}
    if agent_name == "market_pattern":
        hooks = top_hooks_growth(db, params.get("days", 14))
        output = {"summary": "Top rising hooks based on reuse_count.", "hooks": hooks}
        evidence = {"hook_hashes": [h["hook_hash"] for h in hooks]}
    elif agent_name == "hook_generator":
        base = db.execute(select(HookLibrary).order_by(HookLibrary.reuse_count.desc()).limit(3)).scalars().all()
        suggestions = []
        for hook in base:
            suggestions.append({"original": hook.hook_text, "variation": f"{hook.hook_text} – jetzt sichern"})
        output = {"suggestions": suggestions}
        evidence = {"hook_hashes": [hook.hook_hash for hook in base]}
    elif agent_name == "winner_prediction":
        winners = db.execute(select(Score).order_by(Score.score_total.desc()).limit(5)).scalars().all()
        output = {
            "predictions": [
                {"ad_id": str(score.ad_id), "score_total": score.score_total, "risk": "low"}
                for score in winners
            ]
        }
        evidence = {"ad_ids": [str(score.ad_id) for score in winners]}
    elif agent_name == "strategy_budget":
        settings = params.get("budget", 100)
        output = {
            "plan": "Run microtests with tight kill rules",
            "recommended_budget": settings,
        }
    elif agent_name == "explainability":
        output = {"notes": "Scores are derived from runtime, variants, reuse, funnel fit."}
    elif agent_name == "market_saturation":
        output = {"notes": "Monitor saturation_index in score explanations."}
    elif agent_name == "differentiation":
        output = {"ideas": ["Positionierung gegen Preis-Schock", "Emotionaler Fokus auf Fürsorge"]}
    else:
        output = {"error": "unknown_agent"}

    run = AgentRun(
        agent_name=agent_name,
        status="completed",
        input=params,
        output=output,
        evidence=evidence,
        created_at=datetime.utcnow(),
    )
    db.add(run)
    db.flush()
    return run


def build_test_queue_item(db: Session, title: str, payload: dict) -> TestQueueItem:
    item = TestQueueItem(
        title=title,
        payload=payload,
        predicted_success=payload.get("predicted_success", 0),
        recommended_budget=payload.get("recommended_budget"),
        risk_notes=payload.get("risk_notes"),
        kill_rules=payload.get("kill_rules"),
    )
    db.add(item)
    db.flush()
    return item
