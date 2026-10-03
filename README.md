# AI Upturnly — content engine

Ten pieces for owners of 5–50 person US service businesses (agencies, clinics,
trades) who personally handle sales and marketing. Live at
<https://hvupturnly.github.io/aiupturnly-site/>.

## What is here

| path | what |
|---|---|
| `index.html` | hub page linking all ten |
| `piece-*.html` | the ten published pieces |
| `piece-*.md` | markdown source of the same ten, also held as issue documents on AIU-4 |
| `measurement/measure.py` | weekly measurement loop — see below |
| `measurement/doc-put.sh` | writes an issue document via the Paperclip API (used to publish the record) |
| `inbox/lead-log.jsonl` | AIU-5 lead log; the enquiry column joins on `source_piece` |
| `sitemap.xml`, `robots.txt` | search plumbing |

Each piece's slug is byte-identical to the `source_piece` value the AIU-5 lead
log records, so attribution resolves without a lookup table.

## Measurement

```
gh auth login          # needs repo scope
python3 measurement/measure.py --since 2026-09-27 --until 2026-10-03
```

- pageviews come from GitHub's own Pages traffic API for this repo — these are
  *requests to the page*, not search impressions, and are labelled as such.
- enquiries are derived from `inbox/lead-log.jsonl` on `source_piece`. Dry-run
  rows carry `_dry_run` and are excluded; the script prints the excluded count.

The weekly record itself lives as the `weekly-log` document on
AIU-4, not only in this repo, so the board sees it without a GitHub account.

## Open dependency

The CTA on every page is `inbound@aiupturnly.com`. As of 2026-10-03 the domain
`aiupturnly.com` is unregistered (`whois` → no match, no NS, no MX), so that
address does not receive mail yet. Until the CEO provisions it, the enquiry
column reads zero for a reason unrelated to the writing.
