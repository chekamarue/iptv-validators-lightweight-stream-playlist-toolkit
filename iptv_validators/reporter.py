import json

from .models import AuditReport, HealthStatus


class Reporter:
    """
    Handles the output formatting for audit reports.
    """

    @staticmethod
    def to_json(report: AuditReport) -> str:
        return json.dumps(report.model_dump(mode="json"), indent=2)

    @staticmethod
    def to_text(report: AuditReport) -> str:
        summary = report.summary
        lines = []
        lines.append("IPTV Playlist Audit Report")
        lines.append("=" * 40)
        lines.append(f"Total: {summary.total}")
        lines.append(f"Healthy: {summary.healthy}")
        lines.append(f"Dead: {summary.dead}")
        lines.append(f"Timeout: {summary.timeout}")
        lines.append(f"HTTP Error: {summary.http_error}")
        lines.append(f"Invalid: {summary.invalid}")
        lines.append(f"Not Media: {summary.not_media}")
        lines.append(f"Auth Required: {summary.auth_required}")
        lines.append(f"Rate Limited: {summary.rate_limited}")
        lines.append(f"Network Error: {summary.network_error}")
        lines.append("-" * 40)
        if summary.p50_ttfb_ms is not None:
            lines.append(f"P50 TTFB: {summary.p50_ttfb_ms:.2f} ms")
            lines.append(f"P95 TTFB: {summary.p95_ttfb_ms:.2f} ms")
            lines.append(f"Avg TTFB: {summary.avg_ttfb_ms:.2f} ms")
            lines.append(f"Min TTFB: {summary.min_ttfb_ms:.2f} ms")
            lines.append(f"Max TTFB: {summary.max_ttfb_ms:.2f} ms")

        lines.append("=" * 40)
        lines.append("Detailed Results:")
        for r in report.results:
            status = r.status_code or 'N/A'
            ttfb = r.ttfb_ms or 'N/A'
            prefix = f"  [{r.health_status.value.upper()}] {r.url}"
            lines.append(f"{prefix} (Status: {status}, TTFB: {ttfb} ms)")
        return "\n".join(lines)

    @staticmethod
    def to_junit(report: AuditReport, test_name: str = "iptv-audit") -> str:
        """
        Generates a JUnit XML report.
        """
        failures = 0
        errors = 0
        testcases = []

        # In JUnit, we can treat each entry as a test case.
        # Healthy = pass, others = fail or error.
        for r in report.results:
            time_str = f"{r.ttfb_ms/1000 if r.ttfb_ms else 0}"
            if r.health_status == HealthStatus.HEALTHY:
                testcases.append(
                    f'    <testcase name="{r.url}" classname="{test_name}" time="{time_str}"/>'
                )
            else:
                # Distinguish between errors (network, timeout) and failures (invalid, http error)
                if r.health_status in [HealthStatus.TIMEOUT, HealthStatus.NETWORK_ERROR]:
                    errors += 1
                    testcases.append(
                        f'    <testcase name="{r.url}" classname="{test_name}" time="{time_str}">\n'
                        f'      <error message="{r.health_status.value}"/>\n'
                        f'    </testcase>'
                    )
                else:
                    failures += 1
                    testcases.append(
                        f'    <testcase name="{r.url}" classname="{test_name}" time="{time_str}">\n'
                        f'      <failure message="{r.health_status.value}"/>\n'
                        f'    </testcase>'
                    )

        tests_count = len(report.results)
        xml = []
        xml.append('<?xml version="1.0" encoding="UTF-8"?>')
        xml.append(
            f'<testsuite name="{test_name}" tests="{tests_count}" failures="{failures}" '
            f'errors="{errors}">'
        )
        xml.extend(testcases)
        xml.append('</testsuite>')

        return "\n".join(xml)

    def print(self, report: AuditReport, format: str = "text"):
        if format == "json":
            print(self.to_json(report))
        elif format == "junit":
            print(self.to_junit(report))
        else:
            print(self.to_text(report))
