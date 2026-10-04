from iptv_validators.models import HealthStatus
from iptv_validators.probe import ProbeEngine


async def test_probe_healthy(mock_server):
    engine = ProbeEngine(timeout=2.0, ssrf_protection=False)
    result = await engine.probe_url(f"{mock_server}/healthy.m3u8")
    assert result.health_status == HealthStatus.HEALTHY
    assert result.status_code == 200
    assert result.ttfb_ms is not None

async def test_probe_http_error(mock_server):
    engine = ProbeEngine(timeout=2.0, ssrf_protection=False)
    result = await engine.probe_url(f"{mock_server}/error.m3u8")
    assert result.health_status == HealthStatus.HTTP_ERROR
    assert result.status_code == 500

async def test_probe_not_media(mock_server):
    engine = ProbeEngine(timeout=2.0, ssrf_protection=False)
    result = await engine.probe_url(f"{mock_server}/not_media")
    assert result.health_status == HealthStatus.NOT_MEDIA

async def test_probe_timeout(mock_server):
    engine = ProbeEngine(timeout=0.5, ssrf_protection=False)
    result = await engine.probe_url(f"{mock_server}/slow.m3u8")
    assert result.health_status == HealthStatus.TIMEOUT

async def test_ssrf_protection():
    engine = ProbeEngine(timeout=2.0, ssrf_protection=True)
    result = await engine.probe_url("http://127.0.0.1/healthy.m3u8")
    assert result.health_status == HealthStatus.INVALID
