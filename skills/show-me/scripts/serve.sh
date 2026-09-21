#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="${SHOW_ME_CACHE:-$HOME/.cache/show-me}"
PAGES="$CACHE/pages"
PORT="${SHOW_ME_PORT:-4179}"
PIDFILE="$CACHE/serve.pid"
LOGFILE="$CACHE/serve.log"
OLD_PIDFILE="$ROOT/out/.serve.pid"

usage() {
  echo "usage: serve.sh /path/to/unique.md" >&2
  exit 1
}

MD="${1:-}"
[[ -n "$MD" && -f "$MD" ]] || usage

mkdir -p "$PAGES"

if command -v uuidgen >/dev/null 2>&1; then
  ID="$(uuidgen | tr '[:upper:]' '[:lower:]')"
else
  ID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
fi

DEST="$PAGES/$ID"
mkdir -p "$DEST"
cp "$ROOT/template.html" "$DEST/index.html"
cp "$MD" "$DEST/content.md"

URL="http://127.0.0.1:${PORT}/${ID}/"

listening() {
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1
}

alive_pid() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

stop_pidfile() {
  local file="$1"
  if [[ -f "$file" ]]; then
    local pid
    pid="$(cat "$file" 2>/dev/null || true)"
    if alive_pid "$pid"; then
      kill "$pid" 2>/dev/null || true
      sleep 0.2
    fi
    rm -f "$file"
  fi
}

# Previous skill versions served a shared out/ dir on this port.
stop_pidfile "$OLD_PIDFILE"

if [[ -f "$PIDFILE" ]] && ! alive_pid "$(cat "$PIDFILE" 2>/dev/null || true)"; then
  rm -f "$PIDFILE"
fi

# Drop a leftover serve on this port if it isn't the cache server we track.
if listening && ! alive_pid "$(cat "$PIDFILE" 2>/dev/null || true)"; then
  leftover="$(lsof -nP -iTCP:"$PORT" -sTCP:LISTEN -t | head -n 1 || true)"
  args="$(ps -p "${leftover:-0}" -o args= 2>/dev/null || true)"
  if [[ "$args" == *serve* ]]; then
    kill "$leftover" 2>/dev/null || true
    sleep 0.2
  fi
fi

start_serve() {
  mkdir -p "$CACHE"
  : >>"$LOGFILE"
  nohup npx --yes serve "$PAGES" \
    -l "tcp://127.0.0.1:${PORT}" \
    --no-clipboard \
    --no-port-switching \
    >>"$LOGFILE" 2>&1 </dev/null &
  echo $! >"$PIDFILE"
  disown $! 2>/dev/null || true

  for _ in $(seq 1 50); do
    if listening; then
      return 0
    fi
    sleep 0.2
  done
  return 1
}

if ! listening; then
  start_serve || true
fi

# Another agent may have bound the port first.
if ! listening; then
  sleep 0.4
fi

if ! listening; then
  echo "show-me: serve failed to bind http://127.0.0.1:${PORT}" >&2
  tail -n 40 "$LOGFILE" >&2 || true
  exit 1
fi

open "${URL}?t=$(date +%s)"
echo "$URL"
