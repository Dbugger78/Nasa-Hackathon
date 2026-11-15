"""Cached Mars surface imagery from the NASA Image and Video Library.

The old Mars Rover Photos API is no longer dependable, and it also
returned Curiosity (Gale Crater) pictures for a Jezero mission. This
client searches the public NASA Image Library instead, needs no API
key, caches results, and never fabricates images: if NASA is
unreachable it serves the last good result or reports "unavailable".
"""

from __future__ import annotations

import logging
import re
import threading
import time
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

SEARCH_URL = "https://images-api.nasa.gov/search"
DEFAULT_QUERY = "Perseverance Jezero Mastcam-Z"


class ImageryService:
    def __init__(self, ttl_seconds: int = 3600, timeout: float = 8.0, session=None):
        self.ttl = ttl_seconds
        self.timeout = timeout
        self.session = session or requests.Session()
        self._lock = threading.Lock()
        self._images: list[dict] = []
        self._fetched_at: float | None = None

    @property
    def has_cache(self) -> bool:
        return self._fetched_at is not None

    @staticmethod
    def _safe_https(url: str) -> str | None:
        """Only allow https links on nasa.gov hosts."""
        parsed = urlparse(url.replace("http://", "https://", 1))
        host = parsed.hostname or ""
        if parsed.scheme == "https" and (host == "nasa.gov" or host.endswith(".nasa.gov")):
            return parsed.geturl()
        return None

    def _fetch(self, query: str, limit: int) -> list[dict]:
        resp = self.session.get(
            SEARCH_URL,
            params={"q": query, "media_type": "image", "page_size": 25},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        items = resp.json().get("collection", {}).get("items", [])
        images: list[dict] = []
        for item in items:
            data = (item.get("data") or [{}])[0]
            links = item.get("links") or []
            src = self._safe_https(links[0].get("href", "")) if links else None
            if not src:
                continue
            larger = re.sub(r"~(thumb|small)\.jpg$", "~medium.jpg", src)
            images.append(
                {
                    "img_src": larger,
                    "fallback_src": src,
                    "title": data.get("title", "Mars surface image"),
                    "date": (data.get("date_created") or "")[:10],
                    "nasa_id": data.get("nasa_id", ""),
                }
            )
            if len(images) >= limit:
                break
        return images

    def get(self, query: str = DEFAULT_QUERY, limit: int = 6) -> dict:
        """Return {"status", "fetched_at", "images"}; never raises."""
        with self._lock:
            fresh = self._fetched_at is not None and time.time() - self._fetched_at < self.ttl
            if fresh:
                return self._result("live")
            try:
                self._images = self._fetch(query, limit)
                self._fetched_at = time.time()
                return self._result("live")
            except (requests.RequestException, ValueError) as exc:
                logger.warning("NASA imagery fetch failed: %s", exc)
                return self._result("stale" if self._images else "unavailable")

    def _result(self, status: str) -> dict:
        return {
            "status": status,
            "source": "NASA Image and Video Library",
            "fetched_at": self._fetched_at,
            "images": list(self._images),
        }
