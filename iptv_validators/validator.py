import asyncio

from .models import AuditReport, AuditSummary, HealthStatus, M3UEntry, ProbeResult
from .parser import M3UParser
from .probe import ProbeEngine
from .utils import normalize_url


class PlaylistValidator:
    """
    High-level orchestrator for playlist auditing.
    """

    def __init__(self, probe_engine: ProbeEngine, max_workers: int = 10):
        self.probe_engine = probe_engine
        self.max_workers = max_workers
        self.semaphore = None

    async def validate_playlist(self, content: str) -> AuditReport:
        """
        Validates a playlist from its content string.
        """
        entries = M3UParser.parse(content)

        # Deduplicate based on normalized URL
        seen_urls: set[str] = set()
        unique_entries: list[M3UEntry] = []
        for entry in entries:
            norm_url = normalize_url(entry.stream_url)
            if norm_url not in seen_urls:
                seen_urls.add(norm_url)
                unique_entries.append(entry)

        # Run probes
        results = await self._probe_entries(unique_entries)

        # Aggregate
        summary = self._aggregate(results)

        return AuditReport(summary=summary, results=results)

    async def _probe_entries(self, entries: list[M3UEntry]) -> list[ProbeResult]:
        """
        Probes the list of entries with bounded concurrency.
        """
        self.semaphore = asyncio.Semaphore(self.max_workers)
        results = [None] * len(entries)

        async def probe_index(index: int, entry: M3UEntry):
            async with self.semaphore:
                results[index] = await self.probe_engine.probe_url(entry.stream_url)

        tasks = [probe_index(i, entry) for i, entry in enumerate(entries)]
        await asyncio.gather(*tasks)

        return results

    def _aggregate(self, results: list[ProbeResult]) -> AuditSummary:
        """
        Calculates aggregate statistics from probe results.
        """
        status_counts = {status: 0 for status in HealthStatus}
        valid_ttfbs = []

        for result in results:
            status_counts[result.health_status] += 1
            if result.ttfb_ms is not None and result.health_status == HealthStatus.HEALTHY:
                valid_ttfbs.append(result.ttfb_ms)

        # Sort TTFBs for percentiles
        if valid_ttfbs:
            valid_ttfbs.sort()
            p50 = valid_ttfbs[int(len(valid_ttfbs) * 0.50)] if len(valid_ttfbs) > 0 else 0
            p95 = valid_ttfbs[int(len(valid_ttfbs) * 0.95)] if len(valid_ttfbs) > 0 else 0
            avg = sum(valid_ttfbs) / len(valid_ttfbs)
            min_ttfb = min(valid_ttfbs)
            max_ttfb = max(valid_ttfbs)
        else:
            p50 = p95 = avg = min_ttfb = max_ttfb = None

        return AuditSummary(
            total=len(results),
            healthy=status_counts.get(HealthStatus.HEALTHY, 0),
            dead=status_counts.get(HealthStatus.DEAD, 0),
            timeout=status_counts.get(HealthStatus.TIMEOUT, 0),
            http_error=status_counts.get(HealthStatus.HTTP_ERROR, 0),
            invalid=status_counts.get(HealthStatus.INVALID, 0),
            not_media=status_counts.get(HealthStatus.NOT_MEDIA, 0),
            auth_required=status_counts.get(HealthStatus.AUTH_REQUIRED, 0),
            rate_limited=status_counts.get(HealthStatus.RATE_LIMITED, 0),
            network_error=status_counts.get(HealthStatus.NETWORK_ERROR, 0),
            p50_ttfb_ms=p50,
            p95_ttfb_ms=p95,
            avg_ttfb_ms=avg,
            min_ttfb_ms=min_ttfb,
            max_ttfb_ms=max_ttfb
        )
