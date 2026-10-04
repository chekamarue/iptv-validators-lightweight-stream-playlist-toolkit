from iptv_validators.parser import M3UParser


def test_parse_valid_m3u():
    content = """#EXTM3U
#EXTINF:-1 tvg-id="ABC1" tvg-name="ABC" group-title="News",ABC News
http://example.com/abc.m3u8
#EXTINF:-1 tvg-id="XYZ" tvg-name="XYZ" group-title="Movies",XYZ Movies
http://example.com/xyz.m3u8
"""
    entries = M3UParser.parse(content)
    assert len(entries) == 2
    assert entries[0].channel_name == "ABC News"
    assert entries[0].tvg_id == "ABC1"
    assert entries[0].group_title == "News"
    assert entries[1].channel_name == "XYZ Movies"
    assert entries[1].stream_url == "http://example.com/xyz.m3u8"

def test_parse_malformed_m3u():
    content = """#EXTM3U
#EXTINF:-1,Missing URL
#EXTINF:-1 tvg-id="A",A
http://example.com/a.m3u8
"""
    entries = M3UParser.parse(content)
    # "Missing URL" line is a comment, and the next line is another #EXTINF.
    # The first #EXTINF is orphaned/malformed. The parser should only find 1 valid entry.
    assert len(entries) == 1
    assert entries[0].stream_url == "http://example.com/a.m3u8"
