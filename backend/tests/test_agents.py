from app.services.agents import run_agent
from app.db.models import HookLibrary


def test_agent_rules_output(db_session):
    hook = HookLibrary(hook_text="Hallo", hook_hash="hash", reuse_count=2)
    db_session.add(hook)
    db_session.commit()
    run = run_agent(db_session, "hook_generator", {})
    assert "suggestions" in run.output
