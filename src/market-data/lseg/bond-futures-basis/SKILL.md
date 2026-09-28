---
name: bond-futures-basis
description: Assess Treasury bond futures basis and carry, relating futures pricing to cash bond analytics and the short-end curve. Use for CTD and basis discussion, implied repo, and cheap/rich futures analysis. Free-source edition — CTD and conversion-factor data are connector-gated, so this covers the carry-and-curve framing rather than a true basis.
---

# Bond Futures Basis Analysis

You are an expert in bond futures and basis trading. Combine futures pricing, cash bond analytics, yield curve data, and historical tracking to assess basis trade opportunities. Focus on routing data from free data sources into a coherent basis analysis — you compute the metrics, you interpret and present.

## Core Principles

The basis sits at the intersection of cash bond pricing, repo markets, and delivery mechanics. Always start by pricing the future to identify the CTD and delivery basket, then price the CTD bond separately, compute basis metrics from the two outputs, and overlay yield curve context. The net basis represents embedded delivery option value — compare implied repo to market repo to assess whether futures are rich or cheap.

## Data sources (free)

> **⚠️ Partially connector-gated.** This skill's core analysis needs bond futures pricing with CTD identification and conversion factors, and single-name cash bond pricing. The free
> stack below covers the yield curve and repo-rate context on the short end, but the gap does not. If the missing input is
> unavailable, **stop and say so** — do not substitute an approximation silently
> and present it as the real thing.
- **Risk-free curve / short-end repo proxy** — US Treasury daily par yield CSV and the 1M/3M
  bills (no key).
- **Futures proxy** — `yfinance` for the listed Treasury futures contracts. **The symbol form is
  unverified** — confirm `ZN=F`/`ZF=F`/`ZT=F`/`ZB=F` resolve before relying on them; fall back to
  curve math if they do not.
- **Cash bond proxy** — `yfinance` for a CTD candidate, or the CTD ETF ladder (SHY/IEF/TLT).

Not covered: true CTD identification, conversion factors, and delivery-basket mechanics. Without a
real CTD and conversion factor you cannot compute a true basis or implied repo — so **do not
present one**. Either obtain the contract specs, or report only the carry-and-curve analysis and say
the basis itself is unavailable.
## Workflow

1. **Price the Future:** Pull the futures price via `yfinance` (symbol unverified) or fall back to curve math with the contract RIC. Extract CTD bond identifier, conversion factors, delivery basket, contract DV01, delivery dates.
2. **Price the CTD Bond:** Pull the cash bond proxy via `yfinance` for the CTD identified in step 1. Extract clean/dirty price, yield, duration, DV01.
3. **Compute Basis Metrics:** From the two outputs, compute gross basis, carry, net basis (BNOC), and implied repo rate. Compare implied repo to market short-term rate.
4. **Yield Curve Context:** Pull the short end from the Treasury bill-rate series for the future's currency. Use short-end rate as repo proxy for the implied repo comparison.
5. **Historical Context:** Pull historical prices via `yfinance` for both the future and CTD bond (3M daily). Assess basis trend, volatility, and current percentile.
6. **Sovereign Credit (optional):** Pull the ICE BofA OAS series for credit context for the relevant sovereign to check for credit-driven basis distortions.

## Data integrity (non-negotiable)

**Never fabricate a market datum.** A plausible-looking yield, spread, or option
vol is worse than no number, because it is indistinguishable from a real one to
whoever reads the output. If a field cannot be sourced:

1. State that it is unavailable and name the blocker (no free source / rate limit / needs a key).
2. Ask the user for it, or mark the cell `n/a — <reason>`.
3. Carry the provenance (source + retrieval date) on every figure, per `market-data-sources`.

All free sources here are EOD or delayed — none are real-time. Say so in the output rather than
letting the tables imply live pricing.

## Output Format

### Future Summary
| Field | Value |
|-------|-------|
| Contract | ... |
| Fair Price | ... |
| CTD Bond | ... |
| Conversion Factor | ... |
| Contract DV01 | ... |

### CTD Bond Analytics
| Field | Value |
|-------|-------|
| Clean Price | ... |
| YTM | ... |
| Duration | ... |
| DV01 | ... |

### Basis Calculation
| Metric | Value |
|--------|-------|
| Gross Basis | ... ticks |
| Carry | ... ticks |
| Net Basis | ... ticks |
| Implied Repo | ...% |
| Market Repo (approx) | ...% |
| Assessment | Rich / Fair / Cheap |

### Historical Basis Context
| Metric | Current | 3M Avg | 6M Avg | Percentile |
|--------|---------|--------|--------|------------|
| Net Basis | ... | ... | ... | ...th |
| Implied Repo | ... | ... | ... | ...th |

Lead with the basis trade assessment (long/short/neutral) and implied repo comparison. Follow with detailed analytics tables.
