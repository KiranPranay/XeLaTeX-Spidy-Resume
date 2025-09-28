#!/usr/bin/env bash
set -euo pipefail

# Default config; override with: ./build.sh --config config/other.json
CONFIG="config/pranay.json"
if [[ "${1:-}" =~ ^(-c|--config)$ ]]; then
  CONFIG="${2:-$CONFIG}"
fi

# ---- sanity checks ----
command -v python3 >/dev/null 2>&1 || { echo "python3 not found"; exit 1; }
command -v latexmk >/dev/null 2>&1 || { echo "latexmk not found (install TeX Live)"; exit 1; }

# ---- render LaTeX from JSON+template (prints a meta JSON blob) ----
RENDER_JSON="$(python3 ./render.py --config "$CONFIG")" || exit $?

# ---- parse meta without jq (use Python for portability) ----
readarray -t META < <(python3 - "$RENDER_JSON" <<'PY'
import json, sys
m=json.loads(sys.argv[1])
print(m["tex_path"])
print(m["outdir"])
print(m["engine"])
print(m["output_basename"])
PY
)

TEX_PATH="${META[0]}"
OUT_DIR="${META[1]}"
ENGINE="${META[2]}"
OUT_BASE="${META[3]}"

# ---- latexmk options (write all intermediates to outputs/) ----
OPTS=(-silent -f -bibtex- -interaction=nonstopmode -halt-on-error "-outdir=$OUT_DIR" "-auxdir=$OUT_DIR")

# ---- compile with selected engine; fallback to the other if it fails ----
FAILED=0
if [[ "${ENGINE,,}" == "lualatex" ]]; then
  latexmk "${OPTS[@]}" -lualatex "$TEX_PATH" || FAILED=1
else
  latexmk "${OPTS[@]}" -xelatex "$TEX_PATH" || FAILED=1
fi

if [[ "$FAILED" -ne 0 ]]; then
  echo "First engine (${ENGINE}) failed — attempting fallback..." >&2
  if [[ "${ENGINE,,}" == "lualatex" ]]; then
    latexmk "${OPTS[@]}" -xelatex "$TEX_PATH" || FAILED=2
  else
    latexmk "${OPTS[@]}" -lualatex "$TEX_PATH" || FAILED=2
  fi
fi

if [[ "$FAILED" -ne 0 ]]; then
  LOG="$OUT_DIR/${OUT_BASE}.log"
  [[ -f "$LOG" ]] && { echo; echo "--- Last 80 lines of build log ---"; tail -n 80 "$LOG"; }
  exit $FAILED
fi

echo
echo "Build succeeded."
echo "PDF: $OUT_DIR/${OUT_BASE}.pdf"
