from fastapi import FastAPI
from app.core.logging import configure_logging
from app.api.routes import scan, ads, hooks, stats


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="AdRadar API")
    app.include_router(scan.router)
    app.include_router(ads.router)
    app.include_router(hooks.router)
    app.include_router(stats.router)
    return app


app = create_app()
