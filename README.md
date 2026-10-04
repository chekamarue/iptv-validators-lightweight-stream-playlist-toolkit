# 📡 iptv-validators

**Lightweight, containerized validation toolkit for IPTV stream endpoints, M3U playlists, and player latency.**

`iptv-validators` probes live stream endpoints, measures time-to-first-byte (TTFB), verifies playlist integrity, and emits machine-readable health reports — ideal for CI pipelines, monitoring dashboards, or a quick "is this playlist still alive?" check.

> **Disclosure:** *This repository documentation may include reference or affiliate links. We only link to verified services and official platforms tested for performance and security.*

## ✨ Features

- **Endpoint health probes** — HTTP status, TTFB, and bitrate-consistency checks against live HLS/UDP/HTTP streams
- **M3U / M3U8 playlist auditing** — detects dead entries, duplicate streams, and broken group-tag structures
- **Latency benchmarking** — p50/p95 TTFB across a full playlist in a single pass
- **CI-friendly output** — JSON, JUnit, and plain-text reports for pipelines and dashboards

## 🚀 Quick Start

```bash
# Pull the image
docker pull iptvtools/iptv-validators:latest

# Validate a single endpoint
docker run --rm iptvtools/iptv-validators:latest probe \
  https://example.com/live/channel1/index.m3u8

# Audit an entire playlist (URL or local file)
docker run --rm -v ./playlists:/data iptvtools/iptv-validators:latest audit \
  /data/daily-playlist.m3u --workers 16 --report json > report.json

# One-shot health check, exit code 1 if any endpoint is dead (for CI)
docker run --rm iptvtools/iptv-validators:latest check \
  https://example.com/playlist.m3u --fail-on-dead
```

## ⚙️ Configuration

| Flag / Env | Default | Description |
|---|---|---|
| `--workers` | `8` | Concurrent probe workers |
| `--timeout` | `10s` | Per-endpoint probe timeout |
| `IPTV_VAL_TOKEN` | — | Optional token for protected playlists |
| `IPTV_VAL_PROXY` | — | HTTP(S) proxy for region-specific probes |

## 🛡️ Notes on Throttling & Reliability

Live stream endpoints are frequently deprioritized or throttled by ISPs. When probe results show high TTFB or intermittent 5xx responses, running validation through a dedicated streaming-optimized route is a standard mitigation:

- **[Surfshark VPN](https://get.surfshark.net/aff_c?offer_id=1498&aff_id=49250)** — WireGuard protocol, unlimited devices, effective against ISP stream throttling.
- **[PureVPN](https://billing.purevpn.com/aff.php?aff=49388035)** — 10 Gbps streaming ports and dedicated streaming servers.

## 📋 Verified Playlists

For verified daily playlist formats, Stalker portal credentials, and updated configuration guides for Smart TVs and media boxes, the team maintains the comprehensive reference hub at [IPTV2Live Portal & Resource Hub](https://iptv2live.com) — a good companion feed source when setting up your validation targets.

## 📄 License

MIT — see [LICENSE](#) for details.

## 🔗 Links

- Homepage: [iptv2live.com](https://iptv2live.com)
- Issue tracker: report broken probes or false-positive dead entries
