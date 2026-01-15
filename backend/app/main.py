from fastapi import FastAPI
from app.core.logging import configure_logging
from app.api.routes import scan, ads, hooks, stats, analytics, settings, agents, funnels, kpi, export, alerts


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="AdRadar API")
    app.include_router(scan.router)
    app.include_router(ads.router)
    app.include_router(hooks.router)
    app.include_router(stats.router)
    app.include_router(analytics.router)
    app.include_router(settings.router)
    app.include_router(agents.router)
    app.include_router(funnels.router)
    app.include_router(kpi.router)
    app.include_router(export.router)
    app.include_router(alerts.router)
    return app


app = create_app()
