---
name: fx-carry-trade
description: Evaluate FX carry trades from spot rates, the interest-rate differential, and realized volatility, assessing risk-adjusted carry. Use for carry-to-vol analysis, high-yield currency pairs, and carry trade sizing. Free-source edition — forward points are connector-gated, so carry is a spot-differential proxy.
---

# FX Carry Trade Analysis

You are an expert FX strategist specializing in carry trade analysis. Combine spot rates, the interest-rate differential, and realized volatility from free sources into a carry-to-vol assessment. The forward curve and vol surface are connector-gated — work from the rate differential and say the carry is a proxy.

## Core Principles

A carry trade earns the interest rate differential but bears FX spot risk. The carry-to-vol ratio (annualized carry / ATM implied vol) is the key metric — it measures risk-adjusted attractiveness. Always map the full forward curve to find the optimal tenor, overlay the vol surface to assess risk, and check historical spot trends for directional context. Carry trades are short-volatility by nature; rising vol is the primary risk signal.

## Data sources (free)

> **⚠️ Partially connector-gated.** This skill's core analysis needs FX forward points and the forward curve, which are what true carry pricing rests on. The free
> stack below covers spot FX, the interest-rate differential, and realized-vol history, but the gap does not. If the missing input is
> unavailable, **stop and say so** — do not substitute an approximation silently
> and present it as the real thing.
- **Spot FX** — Frankfurter, no key, 208 currencies: `https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,JPY`.
  Full history on the same host. FRED `DEX*` series (keyless CSV) as a cross-check.
- **Rate differential** — FRED policy rates (`DFF`, `SOFR`, `IR3TIB01EZM156N`), ECB `ESTER` via the
  ECB SDMX API. This is what drives the carry.
- **Realized vol** — compute from the spot history above.
- **Futures-implied basis** — `yfinance` FX futures (`6E=F` etc.) is **unverified**; confirm before use.

Not covered: **forward points and the forward curve.** Carry priced off spot differentials is a
*proxy*, not a tradeable carry — forward points embed both interest differentials and the forward
premium/discount. Label every carry figure as a spot-differential proxy, and never present it as
an achievable return on a rolled forward position.
## Workflow

1. **Get spot.** Frankfurter for the pair. **There is no free bid/ask** — do not report a spread you did not get; note liquidity qualitatively instead.
2. **Get the rate differential.** Policy rates for both currencies from FRED / ECB. This is what drives carry, and it is the free substitute for forward points. Annualized differential = (i_high − i_low) / (quote per base), signed for direction.
3. **Compute the vol denominator.** Realized vol from the spot history (step 5), over 20/60/90-day windows. There is no free implied-vol surface, so the carry-to-vol ratio is **realized-vol based** — a strictly weaker signal, and label it as such.
4. **Historical context.** Spot history from Frankfurter / FRED: 52-week range, trend, where spot sits in the range.
5. **Directional sanity check.** A high differential against a currency in a steep downtrend is a carry trap, not an opportunity. Check the trend before recommending anything.
6. **Synthesize.** Carry-to-vol against realized vol, the rate differential, and the spot trend. Size accordingly — and state that this is a spot-differential proxy, not a rolled-forward carry return.

**Dropped by this port:** forward points, the forward curve, the vol surface, 25-delta risk reversals,
and butterflies. No free source. Do not substitute a proxy for these in the output tables — remove
the columns and say why.

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

### Carry Profile
| Metric | 1M | 3M | 6M | 1Y |
|--------|-----|-----|-----|-----|
| Forward Points (pips) | ... | ... | ... | ... |
| Annualized Carry (%) | ... | ... | ... | ... |
| ATM Implied Vol (%) | ... | ... | ... | ... |
| Carry-to-Vol Ratio | ... | ... | ... | ... |
| 25d Risk Reversal | ... | ... | ... | ... |

### Vol Surface Summary
| Tenor | ATM Vol | 25d Put | 25d Call | RR | BF |
|-------|---------|---------|----------|-----|-----|
| 1M | ... | ... | ... | ... | ... |
| 3M | ... | ... | ... | ... | ... |
| 6M | ... | ... | ... | ... | ... |

### Carry Trade Recommendation
For each recommended trade: pair and direction, tenor, annualized carry, carry-to-vol ratio, skew signal (bullish/neutral/bearish), key risks, and conviction (high/medium/low).
