import argparse
import asyncio
import os
import sys

from .probe import ProbeEngine
from .reporter import Reporter
from .validator import PlaylistValidator


def main():
    parser = argparse.ArgumentParser(
        description="IPTV Validators - Lightweight CLI toolkit for validating IPTV streams."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Probe command
    probe_parser = subparsers.add_parser("probe", help="Probe a single stream endpoint.")
    probe_parser.add_argument("url", help="URL to probe")
    probe_parser.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds")
    probe_parser.add_argument(
        "--report", choices=["json", "text"], default="text", help="Report format"
    )
    probe_parser.add_argument("--proxy", help="Proxy URL to use")
    probe_parser.add_argument("--no-ssrf", action="store_true", help="Disable SSRF protection")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit a playlist.")
    audit_parser.add_argument("playlist", help="Path to playlist file or URL")
    audit_parser.add_argument("--workers", type=int, default=10, help="Max concurrent workers")
    audit_parser.add_argument("--timeout", type=float, default=10.0, help="Timeout in seconds")
    audit_parser.add_argument(
        "--report", choices=["json", "text", "junit"], default="text", help="Report format"
    )
    audit_parser.add_argument(
        "--fail-on-dead", action="store_true",
        help="Exit with code 1 if any streams are dead"
    )
    audit_parser.add_argument("--proxy", help="Proxy URL to use")
    audit_parser.add_argument("--no-ssrf", action="store_true", help="Disable SSRF protection")

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Check playlist for duplicates and malformed entries."
    )
    check_parser.add_argument("playlist", help="Path to playlist file or URL")
    check_parser.add_argument(
        "--report", choices=["json", "text"], default="text", help="Report format"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "probe":
        asyncio.run(run_probe(args))
    elif args.command == "audit":
        asyncio.run(run_audit(args))
    elif args.command == "check":
        asyncio.run(run_check(args))


async def run_probe(args):
    engine = ProbeEngine(timeout=args.timeout, proxy=args.proxy, ssrf_protection=not args.no_ssrf)
    result = await engine.probe_url(args.url)

    if args.report == "json":
        print(result.model_dump_json(indent=2))
    else:
        print(f"Status: {result.health_status.value}")
        print(f"URL: {result.url}")
        print(f"HTTP Status: {result.status_code or 'N/A'}")
        print(f"Final URL: {result.final_url or 'N/A'}")
        print(f"Content Type: {result.content_type or 'N/A'}")
        print(f"TTFB: {result.ttfb_ms or 'N/A'} ms")
        print(f"Total Time: {result.total_time_ms or 'N/A'} ms")
        print(f"Response Size: {result.response_size or 'N/A'} bytes")

    # Exit code 0 if healthy, 1 otherwise
    sys.exit(0 if result.health_status.value == "healthy" else 1)


async def run_audit(args):
    # Load playlist
    if os.path.exists(args.playlist):
        with open(args.playlist, encoding="utf-8") as f:
            content = f.read()
    else:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(args.playlist)
                content = resp.text
        except Exception as e:
            print(f"Failed to fetch playlist: {e}", file=sys.stderr)
            sys.exit(2)

    engine = ProbeEngine(timeout=args.timeout, proxy=args.proxy, ssrf_protection=not args.no_ssrf)
    validator = PlaylistValidator(probe_engine=engine, max_workers=args.workers)

    try:
        report = await validator.validate_playlist(content)
    except Exception as e:
        print(f"Failed to validate playlist: {e}", file=sys.stderr)
        sys.exit(2)

    reporter = Reporter()
    reporter.print(report, format=args.report)

    if args.fail_on_dead:
        if report.summary.dead > 0 or report.summary.timeout > 0:
            sys.exit(1)
    else:
        sys.exit(0)


async def run_check(args):
    from .parser import M3UParser
    from .utils import normalize_url

    if os.path.exists(args.playlist):
        with open(args.playlist, encoding="utf-8") as f:
            content = f.read()
    else:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(args.playlist)
                content = resp.text
        except Exception as e:
            print(f"Failed to fetch playlist: {e}", file=sys.stderr)
            sys.exit(2)

    entries = M3UParser.parse(content)
    seen = set()
    duplicates = []

    for entry in entries:
        norm_url = normalize_url(entry.stream_url)
        if norm_url in seen:
            duplicates.append(entry)
        else:
            seen.add(norm_url)

    if args.report == "json":
        import json
        print(json.dumps({
            "total_entries": len(entries),
            "duplicates": len(duplicates),
            "duplicate_entries": [d.model_dump(mode="json") for d in duplicates]
        }, indent=2))
    else:
        print(f"Total entries: {len(entries)}")
        print(f"Duplicate entries: {len(duplicates)}")
        for d in duplicates:
            print(f"  Duplicate: {d.stream_url} (Channel: {d.channel_name})")

    sys.exit(0 if not duplicates else 1)


if __name__ == "__main__":
    main()
