#!/bin/bash
# usage: doc-put.sh <issue-id> <key> <payload-file> [base-revision]
set -euo pipefail
api="${PAPERCLIP_API_URL%/}"
case "$api" in */api) ;; *) api="$api/api" ;; esac
issue="$1"; key="$2"; payload="$3"; base="${4:-null}"
jq -n --arg t "$(jq -r .title "$payload")" \
      --arg f "$(jq -r .format "$payload")" \
      --arg b "$(jq -r .body "$payload")" \
      --arg base "$base" \
      '{title:$t,format:$f,body:$b,baseRevisionId:(if $base=="null" then null else $base end)}' > /tmp/_doc_body.json
resp=$(curl -sS -X PUT "$api/issues/$issue/documents/$key" \
  -H "Authorization: Bearer $PAPERCLIP_API_KEY" \
  -H "X-Paperclip-Run-Id: $PAPERCLIP_RUN_ID" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/_doc_body.json -w $'\n%{http_code}')
code=$(printf '%s' "$resp" | tail -n1)
body=$(printf '%s' "$resp" | sed '$d')
echo "HTTP $code"
printf '%s' "$body" | jq -r '{key,title,latestRevisionId} // .' 2>/dev/null || printf '%s\n' "$body"