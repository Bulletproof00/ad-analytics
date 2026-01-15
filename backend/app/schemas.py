from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScanRequest(StrictBase):
    keywords: list[str]
    country: str = "DE"
    since_days: int = 90
    status: str = "ALL"
    max_results_per_keyword: int = 2000


class ScanStatusResponse(StrictBase):
    state: str
    keywords_total: int
    keywords_done: int
    ads_upserted: int
    pages_discovered: int
    errors: list[str]
    started_at: datetime | None
    finished_at: datetime | None


class SettingPayload(StrictBase):
    key: str
    value: dict[str, Any]


class AgentRunRequest(StrictBase):
    agent_name: str
    params: dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(StrictBase):
    id: str
    agent_name: str
    status: str
    output: dict[str, Any]
    evidence: dict[str, Any]
    created_at: datetime


class KPIImportRequest(StrictBase):
    name: str
    csv_text: str
    mapping: dict[str, str]


class ExportRequest(StrictBase):
    niche: str
    funnel_type: str
    budget: int
    objective: str
    test_queue_ids: list[str] = Field(default_factory=list)
