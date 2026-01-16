import logging
import time
from datetime import datetime, timedelta
from typing import Any, Iterable
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)


class MetaClientError(Exception):
    pass


def _build_params(search_term: str, country: str, status: str, since_days: int) -> dict[str, Any]:
    fields = [
        "ad_archive_id",
        "page_id",
        "page_name",
        "ad_delivery_start_time",
        "ad_delivery_stop_time",
        "ad_snapshot_url",
        "ad_creative_bodies",
        "ad_creative_link_titles",
        "ad_creative_link_descriptions",
        "ad_creative_link_captions",
        "publisher_platforms",
        "platforms",
        "languages",
    ]
    since_date = (datetime.utcnow() - timedelta(days=since_days)).date().isoformat()
    return {
        "access_token": settings.meta_access_token,
        "search_terms": search_term,
        "ad_reached_countries": [country],
        "ad_active_status": status,
        "ad_delivery_date_min": since_date,
        "fields": ",".join(fields),
        "limit": 100,
    }


def fetch_ads(
    *,
    search_term: str,
    country: str,
    status: str,
    since_days: int,
    max_results: int,
) -> Iterable[dict[str, Any]]:
    if not settings.meta_access_token:
        raise MetaClientError("META_ACCESS_TOKEN is not configured")

    url = f"{settings.meta_base_url}/{settings.meta_api_version}/ads_archive"
    params = _build_params(search_term, country, status, since_days)

    fetched = 0
    after_cursor = None
    retries = 0

    while True:
        if after_cursor:
            params["after"] = after_cursor
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 429:
            if retries >= settings.rate_limit_max_retries:
                logger.error("rate_limit_max_retries_exceeded", extra={"search_term": search_term})
                break
            sleep_ms = settings.rate_limit_base_sleep_ms * (2 ** retries)
            logger.warning(
                "rate_limited",
                extra={"search_term": search_term, "sleep_ms": sleep_ms},
            )
            time.sleep(sleep_ms / 1000)
            retries += 1
            continue
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {"text": response.text}
            if response.status_code in (401, 403):
                raise MetaClientError(f"OAuth error: {payload}")
            if "ad_delivery_date_min" in str(payload):
                logger.warning("parameter_rejected", extra={"param": "ad_delivery_date_min"})
                params.pop("ad_delivery_date_min", None)
                response = requests.get(url, params=params, timeout=30)
                if response.status_code >= 400:
                    logger.error("meta_request_failed", extra={"status": response.status_code, "payload": payload})
                    break
            else:
                logger.error("meta_request_failed", extra={"status": response.status_code, "payload": payload})
                break

        data = response.json()
        results = data.get("data", [])
        for ad in results:
            yield ad
            fetched += 1
            if fetched >= max_results:
                return

        paging = data.get("paging", {})
        cursors = paging.get("cursors", {})
        after_cursor = cursors.get("after")
        if not after_cursor or not results:
            break
