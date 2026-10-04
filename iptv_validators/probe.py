import time

import httpx

from .models import HealthStatus, ProbeResult
from .utils import is_ssrf_safe


class ProbeEngine:
    """
    Core engine for probing stream endpoints.
    """

    def __init__(
        self, timeout: float = 10.0, proxy: str | None = None, ssrf_protection: bool = True
    ):
        self.timeout = timeout
        self.proxy = proxy
        self.ssrf_protection = ssrf_protection

    async def probe_url(self, url: str) -> ProbeResult:
        """
        Probes a single URL and returns a ProbeResult.
        """
        if self.ssrf_protection and not is_ssrf_safe(url):
            return ProbeResult(
                url=url,
                error_category=HealthStatus.INVALID,
                health_status=HealthStatus.INVALID
            )

        start_time = time.perf_counter()
        ttfb_ms: float | None = None

        async with httpx.AsyncClient(
            proxy=self.proxy,
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        ) as client:
            try:
                # To measure TTFB, we use a stream and wait for the first byte of headers
                async with client.stream("GET", url) as response:
                    ttfb_ms = (time.perf_counter() - start_time) * 1000

                    # Read a small chunk to check content and size
                    content_chunk = b""
                    async for chunk in response.aiter_bytes(chunk_size=1024*64): # 64KB
                        content_chunk = chunk
                        break
                    total_time_ms = (time.perf_counter() - start_time) * 1000

                    # Determine health
                    health_status, error_category = self._classify_response(
                        response.status_code,
                        response.headers.get("content-type", ""),
                        content_chunk
                    )

                    return ProbeResult(
                        url=url,
                        status_code=response.status_code,
                        final_url=str(response.url),
                        content_type=response.headers.get("content-type"),
                        ttfb_ms=ttfb_ms,
                        total_time_ms=total_time_ms,
                        response_size=len(content_chunk),
                        health_status=health_status,
                        error_category=(
                            error_category if health_status != HealthStatus.HEALTHY else None
                        )
                    )

            except httpx.TimeoutException:
                return ProbeResult(
                    url=url,
                    error_category=HealthStatus.TIMEOUT,
                    health_status=HealthStatus.TIMEOUT
                )
            except httpx.HTTPStatusError as exc:
                return ProbeResult(
                    url=url,
                    status_code=exc.response.status_code,
                    error_category=HealthStatus.HTTP_ERROR,
                    health_status=HealthStatus.HTTP_ERROR
                )
            except httpx.RequestError:
                return ProbeResult(
                    url=url,
                    error_category=HealthStatus.NETWORK_ERROR,
                    health_status=HealthStatus.NETWORK_ERROR
                )
            except Exception as exc:
                import sys
                print(f"Exception probing {url}: {exc}", file=sys.stderr)
                return ProbeResult(
                    url=url,
                    error_category=HealthStatus.INVALID,
                    health_status=HealthStatus.INVALID
                )

    def _classify_response(
        self, status_code: int, content_type: str, content: bytes
    ) -> tuple[HealthStatus, HealthStatus | None]:
        """
        Classifies the response based on status code, content type, and content.
        """
        # 1. Check for HTTP error status
        if status_code >= 400:
            if status_code == 429:
                return HealthStatus.RATE_LIMITED, HealthStatus.RATE_LIMITED
            if status_code in (401, 403):
                return HealthStatus.AUTH_REQUIRED, HealthStatus.AUTH_REQUIRED
            return HealthStatus.HTTP_ERROR, HealthStatus.HTTP_ERROR

        # 2. Check if it's actually media
        # Common media content types for IPTV
        media_types = ("video/", "audio/", "application/x-mpegurl", "application/vnd.apple.mpegurl")
        is_media = any(mt in content_type.lower() for mt in media_types)

        if not is_media:
            # It might be an error page in HTML even if 200 OK
            if "text/html" in content_type.lower():
                # Check for common error keywords in the body
                body_lower = content.decode("utf-8", errors="ignore").lower()
                error_keywords = ("error", "not found", "forbidden", "access denied", "invalid")
                if any(kw in body_lower for kw in error_keywords):
                    return HealthStatus.NOT_MEDIA, HealthStatus.NOT_MEDIA
                return HealthStatus.NOT_MEDIA, HealthStatus.NOT_MEDIA
            return HealthStatus.NOT_MEDIA, HealthStatus.NOT_MEDIA

        # 3. Check if content is empty
        if len(content) == 0:
            return HealthStatus.INVALID, HealthStatus.INVALID

        # 4. Otherwise, healthy
        return HealthStatus.HEALTHY, None
