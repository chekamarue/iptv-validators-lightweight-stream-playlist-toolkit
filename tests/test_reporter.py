import json

from iptv_validators.models import AuditReport, AuditSummary, HealthStatus, ProbeResult
from iptv_validators.reporter import Reporter


def _make_summary(healthy: int, dead: int = 0) -> AuditSummary:
    return AuditSummary(
        total=1,
        healthy=healthy,
        dead=dead,
        timeout=0,
        http_error=0,
        invalid=0,
        not_media=0,
        auth_required=0,
        rate_limited=0,
        network_error=0,
    )


def test_report_json():
    report = AuditReport(
        summary=_make_summary(healthy=1),
        results=[ProbeResult(url="http://test.com", health_status=HealthStatus.HEALTHY)]
    )
    json_str = Reporter.to_json(report)
    data = json.loads(json_str)
    assert data["summary"]["total"] == 1
    assert data["results"][0]["url"] == "http://test.com"


def test_report_text():
    report = AuditReport(
        summary=_make_summary(healthy=1),
        results=[ProbeResult(url="http://test.com", health_status=HealthStatus.HEALTHY)]
    )
    text_str = Reporter.to_text(report)
    assert "Total: 1" in text_str
    assert "Healthy: 1" in text_str


def test_report_junit():
    report = AuditReport(
        summary=_make_summary(healthy=0, dead=1),
        results=[ProbeResult(url="http://test.com", health_status=HealthStatus.DEAD)]
    )
    junit_str = Reporter.to_junit(report)
    assert '<testsuite name="iptv-audit" tests="1" failures="1" errors="0">' in junit_str
