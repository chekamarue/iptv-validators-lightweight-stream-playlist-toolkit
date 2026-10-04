from iptv_validators.probe import ProbeEngine
from iptv_validators.validator import PlaylistValidator


async def test_validate_playlist_deduplication(mock_server):
    engine = ProbeEngine(timeout=2.0, ssrf_protection=False)
    validator = PlaylistValidator(probe_engine=engine, max_workers=5)

    content = f"""#EXTM3U
#EXTINF:-1,Ch1
{mock_server}/healthy.m3u8
#EXTINF:-1,Ch1_Dup
{mock_server}/healthy.m3u8
"""
    report = await validator.validate_playlist(content)
    assert report.summary.total == 1 # Deduplicated
    assert report.summary.healthy == 1

async def test_validate_playlist_statistics(mock_server):
    engine = ProbeEngine(timeout=2.0, ssrf_protection=False)
    validator = PlaylistValidator(probe_engine=engine, max_workers=5)

    content = f"""#EXTM3U
#EXTINF:-1,Ch1
{mock_server}/healthy.m3u8
#EXTINF:-1,Ch2
{mock_server}/error.m3u8
"""
    report = await validator.validate_playlist(content)
    assert report.summary.total == 2
    assert report.summary.healthy == 1
    assert report.summary.http_error == 1
    assert report.summary.p50_ttfb_ms is not None
