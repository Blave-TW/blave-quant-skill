#!/usr/bin/env bash
# Blave Quant Skill — daily auto-update setup

MARKER="blave-quant-skill"
SETUP_FLAG="$HOME/.agents/.blave-quant-setup"

if crontab -l 2>/dev/null | grep -q "$MARKER"; then
    touch "$SETUP_FLAG"
    echo "✓ Auto-update already configured."
    exit 0
fi

(crontab -l 2>/dev/null; echo "0 9 * * * npx --yes skills update # $MARKER") | crontab -
touch "$SETUP_FLAG"
echo "✓ blave-quant-skill will auto-update daily at 9:00 AM."
