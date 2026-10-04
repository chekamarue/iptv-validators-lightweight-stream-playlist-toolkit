# iptv-validators

A lightweight, production-quality CLI toolkit for validating IPTV stream endpoints, HLS playlists, and M3U playlists.

## Features

- **Probe Engine**: Validates individual HTTP/HTTPS stream endpoints.
- **M3U/HLS Parsing**: Robust parsing of M3U and M3U8 playlists.
- **Audit Pipeline**: Bounded concurrent validation of entire playlists.
- **SSRF Protection**: Prevents validation requests to internal or loopback addresses.
- **Reporting**: Supports `text`, `json`, and `junit` output formats.
- **CI/CD Friendly**: Deterministic exit codes and structured reports.

## Installation

### From PyPI (when available)
```bash
pip install iptv-validators
```

### From Source
```bash
git clone https://github.com/chekamarue/iptv-validators.git
cd iptv-validators
pip install .
```

## Docker

```bash
docker pull chekamarue/iptv-validators:latest
```

## Usage

### Probing a single endpoint

```bash
iptv-validators probe https://example.com/live/channel.m3u8
```

Output (text):
```
Status: healthy
URL: https://example.com/live/channel.m3u8
HTTP Status: 200
Final URL: https://example.com/live/channel.m3u8
Content Type: application/vnd.apple.mpegurl
TTFB: 120.5 ms
Total Time: 125.3 ms
Response Size: 512 bytes
```

Output (json):
```bash
iptv-validators probe https://example.com/live/channel.m3u8 --report json
```

### Auditing a playlist

```bash
iptv-validators audit playlist.m3u --workers 16 --report text
```

Output (text):
```
IPTV Playlist Audit Report
========================================
Total: 100
Healthy: 95
Dead: 2
Timeout: 3
...
========================================
Detailed Results:
  [HEALTHY] http://... (Status: 200, TTFB: 120.5 ms)
  [DEAD] http://... (Status: N/A, TTFB: N/A ms)
```

Output (json):
```bash
iptv-validators audit playlist.m3u --report json
```

Output (junit):
```bash
iptv-validators audit playlist.m3u --report junit
```

### Checking a playlist

Checks for duplicates and malformed entries without performing network probes.

```bash
iptv-validators check playlist.m3u
```

## Configuration

- `--workers`: Maximum number of concurrent workers (default: 10).
- `--timeout`: Timeout in seconds (default: 10.0).
- `--report`: Output format (`text`, `json`, `junit` for audit; `text`, `json` for probe).
- `--fail-on-dead`: Exit with code 1 if any streams are dead or timeout.
- `--proxy`: Proxy URL to use.
- `--no-ssrf`: Disable SSRF protection.

## Exit Codes

- `0`: Success (healthy or no issues).
- `1`: Failure (dead streams, timeout, or duplicates found).
- `2`: Error (failed to fetch playlist, etc.).

## Development

### Setting up the environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install .[dev]
```

### Running tests
```bash
pytest
```

### Linting
```bash
ruff check .
```

## License

MIT
