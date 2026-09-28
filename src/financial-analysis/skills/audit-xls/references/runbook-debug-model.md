<!-- Source: financial-analysis/commands/debug-model.md (Claude Code slash command '/debug-model'), folded in for the DeepSeek Harness. -->

# Runbook: debug-model

Load the `audit-xls` skill with scope **model** and audit the specified financial model for broken formulas, balance sheet imbalances, hardcoded overrides, circular references, and logic errors — including the full model-integrity checks (BS balance, cash tie-out, roll-forwards, model-type-specific bugs).

If a file path is provided, use it. Otherwise ask the user for the model to review.
