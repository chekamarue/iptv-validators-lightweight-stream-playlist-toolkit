# iptv-validators

A lightweight, production-quality CLI toolkit for validating IPTV stream endpoints, HLS playlists, and M3U playlists.

Built for developers, IPTV operators, monitoring workflows, and CI/CD pipelines that need fast, deterministic stream and playlist validation.

## Features

* **Probe Engine** — Validates individual HTTP/HTTPS stream endpoints.
* **M3U/HLS Parsing** — Robust parsing of M3U and M3U8 playlists.
* **Audit Pipeline** — Bounded concurrent validation of entire playlists.
* **SSRF Protection** — Prevents validation requests to internal or loopback addresses.
* **Reporting** — Supports `text`, `json`, and `junit` output formats.
* **CI/CD Friendly** — Deterministic exit codes and structured reports.
* **Lightweight** — Designed to run efficiently in containers and automation environments.

## Installation

### From PyPI

```bash
pip install iptv-validators
```

### From Source

```bash
git clone https://github.com/chekamarue/iptv-validators-lightweight-stream-playlist-toolkit.git
cd iptv-validators-lightweight-stream-playlist-toolkit
pip install .
```

## Docker

Pull the latest image from Docker Hub:

```bash
docker pull chekamarue/iptv-validators-lightweight-stream-playlist-toolkit:latest
```

### Run a probe

```bash
docker run --rm \
  chekamarue/iptv-validators-lightweight-stream-playlist-toolkit:latest \
  probe https://example.com/live/channel.m3u8
```

### Audit a playlist

```bash
docker run --rm \
  -v ./playlists:/data \
  chekamarue/iptv-validators-lightweight-stream-playlist-toolkit:latest \
  audit /data/playlist.m3u --workers 16 --report json
```

## Usage

### Probing a single endpoint

```bash
iptv-validators probe https://example.com/live/channel.m3u8
```

Example output:

```text
Status: healthy
URL: https://example.com/live/channel.m3u8
HTTP Status: 200
Final URL: https://example.com/live/channel.m3u8
Content Type: application/vnd.apple.mpegurl
TTFB: 120.5 ms
Total Time: 125.3 ms
Response Size: 512 bytes
```

JSON output:

```bash
iptv-validators probe \
  https://example.com/live/channel.m3u8 \
  --report json
```

## Auditing a Playlist

Validate every entry in an M3U/M3U8 playlist using bounded concurrency:

```bash
iptv-validators audit playlist.m3u --workers 16 --report text
```

Example output:

```text
IPTV Playlist Audit Report
========================================
Total: 100
Healthy: 95
Dead: 2
Timeout: 3
========================================
Detailed Results:
  [HEALTHY] http://... (Status: 200, TTFB: 120.5 ms)
  [DEAD] http://... (Status: N/A, TTFB: N/A ms)
```

JSON output:

```bash
iptv-validators audit playlist.m3u --report json
```

JUnit output for CI systems:

```bash
iptv-validators audit playlist.m3u --report junit
```

## Checking a Playlist

Check playlist structure, duplicates, and malformed entries without performing network probes:

```bash
iptv-validators check playlist.m3u
```

Use this mode when you only need to validate playlist integrity.

## Configuration

| Option           | Default | Description                                                |
| ---------------- | ------: | ---------------------------------------------------------- |
| `--workers`      |    `10` | Maximum number of concurrent workers.                      |
| `--timeout`      |  `10.0` | Timeout in seconds for individual requests.                |
| `--report`       |  `text` | Output format: `text`, `json`, or `junit` where supported. |
| `--fail-on-dead` |       — | Exit with code `1` if streams are dead or timeout.         |
| `--proxy`        |       — | Proxy URL to use for requests.                             |
| `--no-ssrf`      |       — | Disable SSRF protection.                                   |

## Exit Codes

| Code | Meaning                                                                   |
| ---: | ------------------------------------------------------------------------- |
|  `0` | Success — healthy results or no detected issues.                          |
|  `1` | Validation failure — dead streams, timeouts, or detected playlist issues. |
|  `2` | Execution error — for example, failure to fetch or process a playlist.    |

## CI/CD

The project is designed to work cleanly in automated pipelines.

Example:

```bash
iptv-validators audit playlist.m3u \
  --workers 16 \
  --report junit \
  --fail-on-dead
```

The deterministic exit codes allow CI systems to fail a build when playlist validation detects problems.

## Development

### Set up the environment

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```cmd
.venv\Scripts\activate
```

Install development dependencies:

```bash
pip install ".[dev]"
```

### Run tests

```bash
pytest
```

### Run linting

```bash
ruff check .
```

## Docker Image

Docker Hub:

https://hub.docker.com/r/chekamarue/iptv-validators-lightweight-stream-playlist-toolkit

Latest image:

```text
chekamarue/iptv-validators-lightweight-stream-playlist-toolkit:latest
```

## Related IPTV Resources

For IPTV playlist resources, streaming guides, setup information, and related tools, visit the official **IPTV2Live** website:

**https://iptv2live.com/**

## License

MIT
