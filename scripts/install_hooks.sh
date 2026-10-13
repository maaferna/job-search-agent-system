#!/usr/bin/env bash
# Installs a git pre-commit hook that runs the sanitization gate. Run once per clone.
# The full gate needs .sanitize-local.yaml (local only); without it only the static patterns run.
set -euo pipefail
hook="$(git rev-parse --git-dir)/hooks/pre-commit"
if [ -e "$hook" ] && ! grep -q sanitize_check "$hook"; then
  echo "✗ $hook already exists and is not ours; add ./scripts/sanitize_check.sh to it by hand" >&2
  exit 1
fi
cat > "$hook" <<'HOOK'
#!/usr/bin/env bash
./scripts/sanitize_check.sh || { echo "✗ sanitization gate failed: fix the text, never the patterns"; exit 1; }
HOOK
chmod +x "$hook"
echo "✓ pre-commit hook installed: $hook"
