#!/usr/bin/env bash
# Builds an example composition and VERIFIES the result, like the private build helper does.
#
#   ./build.sh compositions/showcase-ai-en.tex     # → out/showcase-ai-en.pdf
#   ./build.sh all                                  # every composition
#
# Fails on: LaTeX errors, any "Missing character" (a glyph the PDF cannot show nor an ATS extract),
# more than MAX_PAGES pages, or a PDF whose text cannot be extracted. Needs lualatex; pdftotext and
# pdfinfo (poppler) for the checks. Run from examples/latex/.
set -euo pipefail
cd "$(dirname "$0")"
MAX_PAGES=${MAX_PAGES:-2}
mkdir -p out

build() {
  local tex=$1 name; name=$(basename "$tex" .tex)
  [ "$name" = cv ] && name=$(basename "$(dirname "$tex")")
  lualatex -interaction=nonstopmode -halt-on-error -jobname="$name" -output-directory=out "$tex" > "out/$name.console.txt" \
    || { tail -20 "out/$name.log"; echo "✗ $tex: LaTeX error"; return 1; }
  if grep -q "Missing character" "out/$name.log"; then echo "✗ $tex: missing glyphs"; return 1; fi
  local pages; pages=$(pdfinfo "out/$name.pdf" | awk '/^Pages:/{print $2}')
  [ "$pages" -le "$MAX_PAGES" ] || { echo "✗ $tex: $pages pages (max $MAX_PAGES)"; return 1; }
  local text; text=$(pdftotext "out/$name.pdf" -)
  [[ $text == *"Example Candidate"* ]] || { echo "✗ $tex: text not extractable"; return 1; }
  echo "✓ out/$name.pdf · $pages page(s) · text extractable"
}

if [ "${1:-all}" = all ]; then
  for t in compositions/*.tex compositions/applications/*/cv.tex; do build "$t"; done
else
  build "$1"
fi
