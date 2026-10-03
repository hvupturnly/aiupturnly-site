#!/usr/bin/env python3
"""AIU-4 weekly measurement loop.

Prints the week-over-week table for the ten published pieces and writes the
enquiry column derived from the AIU-5 lead log.

Sources, and what each one is allowed to say:

  impressions / clicks  GitHub's own Pages traffic API for this repo. That API
                        counts *requests to the site*, not search impressions —
                        so the "impressions" column below is honestly a pageview
                        count and the header says so. There is no free,
                        credential-holding source of true search-impression data
                        for a brand-new domain, and inventing one is the failure
                        mode this loop exists to prevent.

  enquiries             Counted from the AIU-5 lead log, joined on source_piece.
                        Never typed by hand.

Usage:
    gh auth login                       # once, needs repo scope
    python3 measurement/measure.py      # current 14 days
    python3 measurement/measure.py --since 2026-09-27 --until 2026-10-03
"""

import argparse
import json
import subprocess
import sys
import urllib.parse
import urllib.request

SITE = "https://hvupturnly.github.io/aiupturnly-site"
REPO = "hvupturnly/aiupturnly-site"
DEFAULT_LEAD_LOG = "inbox/lead-log.jsonl"

PIECES = [
    "piece-01-the-enquiry-that-died-overnight",
    "piece-02-monday-morning-you-find-out-you-were-hired",
    "piece-03-the-owner-is-the-bottleneck",
    "piece-04-six-enquiries-no-record",
    "piece-05-no-time-to-post",
    "piece-06-why-you-are-invisible-in-search",
    "piece-07-the-review-you-never-asked-for",
    "piece-08-your-competitor-answers-in-two-minutes",
    "piece-09-the-website-is-not-your-problem",
    "piece-10-one-page-that-earns-its-keep",
]


def gh(endpoint):
    out = subprocess.run(
        ["gh", "api", f"repos/{REPO}/traffic/{endpoint}"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise SystemExit(f"gh api failed for {endpoint}: {out.stderr.strip()}")
    return json.loads(out.stdout)


def requests_total():
    """Total page requests over the 14 days GitHub retains.

    `gh api traffic/views` wraps the daily series in a "views" key, unlike
    popular/paths which returns a bare list.
    """
    payload = gh("views")
    series = payload.get("views", []) if isinstance(payload, dict) else payload
    return sum(d["count"] for d in series)


def clicks_by_piece():
    """Path -> request count. GitHub popular/paths only returns top 10, so a
    piece missing from it is recorded as 0, never as 'unknown'."""
    paths = {}
    for row in gh("popular/paths"):
        path = urllib.parse.urlparse(row["path"]).path
        paths[path.lstrip("/")] = row["count"]
    return paths


def enquiries_by_piece(lead_log):
    """Join the lead log on source_piece. Dry-run rows carry _dry_run and are
    counted separately: leaving them in would report week-1 enquiries that never
    happened."""
    counts = {}
    dry = {}
    try:
        handle = open(lead_log, encoding="utf-8")
    except FileNotFoundError:
        return counts, dry, 0
    with handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                lead = json.loads(line)
            except json.JSONDecodeError:
                continue
            slug = lead.get("source_piece")
            if not slug:
                continue
            target = dry if lead.get("_dry_run") else counts
            target[slug] = target.get(slug, 0) + 1
    return counts, dry, sum(dry.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lead-log", default=DEFAULT_LEAD_LOG)
    ap.add_argument("--since")
    ap.add_argument("--until")
    args = ap.parse_args()

    total = requests_total()
    paths = clicks_by_piece()
    counts, dry, dry_total = enquiries_by_piece(args.lead_log)

    print(f"# AIU-4 weekly measurement — site {SITE}")
    print(f"# Measured {args.since or 'last 14 days'} to {args.until or 'today'}")
    print()
    print("| piece | url | pageviews (= 'impressions') | enquiries |")
    print("|---|---|---|---|")
    for slug in PIECES:
        clicks = paths.get(f"{slug}.html", 0)
        print(f"| {slug} | {SITE}/{slug}.html | {clicks} | {counts.get(slug, 0)} |")
    print(f"| **total (10 pieces)** | | **{sum(paths.get(f'{s}.html', 0) for s in PIECES)}** | **{sum(counts.values())}** |")
    print()
    print(f"whole-site requests, 14d: {total}")
    print(f"dry-run leads excluded from the enquiry column: {dry_total}")
    print()
    print("Reading notes, so the numbers are not over-read:")
    print("- GitHub Pages traffic covers requests to the site only. A piece that")
    print("  ranks in Google is not counted here. Zero here does not prove zero")
    print("  search impressions; it proves zero measured traffic.")
    print("- GitHub retains 14 days. Weekly cadence fits exactly; daily does not.")
    print("- The enquiry column is derived from the lead log on source_piece.")
    print("  If the CTA mailbox is not live, no enquiry can exist and the column")
    print("  will read zero for a reason that has nothing to do with the writing.")


if __name__ == "__main__":
    sys.exit(main())