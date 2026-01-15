from .scan import router as scan_router
from .ads import router as ads_router
from .hooks import router as hooks_router
from .stats import router as stats_router
from .analytics import router as analytics_router
from .settings import router as settings_router
from .agents import router as agents_router
from .funnels import router as funnels_router
from .kpi import router as kpi_router
from .export import router as export_router
from .alerts import router as alerts_router

__all__ = [
    "scan_router",
    "ads_router",
    "hooks_router",
    "stats_router",
    "analytics_router",
    "settings_router",
    "agents_router",
    "funnels_router",
    "kpi_router",
    "export_router",
    "alerts_router",
]
