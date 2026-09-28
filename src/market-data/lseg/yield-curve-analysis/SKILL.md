---
name: yield-curve-analysis
description: Analyze the government yield curve — curve shape, 2s10s and 5s30s slopes, butterfly, and real-rate decomposition from the TIPS curve. Use for steepener/flattener/butterfly framing, curve roll-down, policy-expectation reads, and curve trade ideas. Free-source edition (US Treasury, ECB, FRED). This is the free replacement for the upstream swap-curve skill — swap spreads, basis, and swaption vols have no free source and are explicitly out of scope.
---

# Yield Curve Analysis

You are a rates strategist. Build the government curve from free sources, decompose real rates
against the TIPS curve, read curve shape, and frame curve trades.

> **Scope note — this is not a swap curve.** The upstream skill was built on the LSEG
> `ir_swap` connector: OIS/SOFR swap rates, swap spreads, and swaption vols. **None of those have a
> free programmatic source.** A Treasury par curve is not a swap curve — substituting one for the
> other and labelling the result "swap spreads" would be wrong, so this skill does not do it.
> If a user genuinely needs swap spreads, say so and stop; the answer is a paid feed.

## Core principles

The curve prices expected future short rates plus a term premium. Always work in this order:
establish the nominal curve, overlay the TIPS curve to get real rates, classify the shape, then
place the historical context before calling a trade. Curve metrics (2s10s, 5s30s, 2s5s10s butterfly)
mean little without knowing where they sit versus the last several years.

**Slope sign convention:** state it. "2s10s = −45bp" (inverted) and "10y-2y = +45bp" (steep) are the
same market described two ways. Pick one, label it, and keep it.

## Data sources (free)

| Need | Source |
|---|---|
| US nominal curve, 1M–30Y, daily | US Treasury daily par yield CSV, no key — exact URL in `market-data-sources` |
| US real curve (TIPS) | same feed, `type=daily_treasury_real_yield_curve` |
| Bills / long-term average | same feed, `_bill_rates` / `_long_term` |
| Euro curve | ECB `YC` SDMX, no key |
| Historical yields, keyless | FRED `fredgraph.csv?id=<SERIES>&cosd=…` |
| Macro context | FRED (`GDPC1`, `CPIAUCSL`, `UNRATE`, `DFF`, `SOFR`), IMF DataMapper, World Bank |

> **Verify a series id resolves before you use it** — a wrong FRED id returns a CSV of commas
> rather than an error, so an unchecked id looks like "flat rates".

## Data integrity (non-negotiable)

**Never fabricate a yield.** A plausible-looking curve point is worse than a gap, because nobody
downstream can tell it from a real one. If a tenor or date is unavailable: name the gap, leave the
cell empty, and do not interpolate across a hole without saying that you did.

All free sources are EOD or delayed — not real-time. Carry source + retrieval date on every table.

## Workflow

1. **Pull the nominal curve.** Treasury par yields (or ECB `YC`) for standard tenors:
   3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y. Note the as-of date and flag any missing tenor.
2. **Pull the real curve.** TIPS yields for the tenors that overlap. Where a tenor is missing on one
   side, say so rather than silently matching a different point.
3. **Classify the shape.** 2s10s, 5s30s, 3M-10Y, and the 2s5s10s butterfly. Name it: normal, flat,
   inverted, or humped.
4. **Decompose real rates.** Real rate = nominal − breakeven, per tenor. Assess whether real policy
   is accommodative or restrictive. **This replaces the upstream inflation-breakeven connector step**
   and is the correct free substitute.
5. **Historical context.** Pull the same series over 1–3 years. Where does the current slope sit
   versus that range — percentile, and has the shape been trending?
6. **Macro read.** Cross-check with FRED policy rates and inflation prints. Is the curve consistent
   with what the central bank is doing, or is it pricing something different?
7. **Synthesize.** Deliver the tables below, then frame curve trades — but size them off the
   **government** curve's DV01, and say plainly that swap-relative sizing is unavailable.

## Output format

### Curve table
| Tenor | Nominal (%) | TIPS Real (%) | Breakeven (bp) |
|-------|-------------|---------------|----------------|
| 2Y | | | |
| 5Y | | | |
| 10Y | | | |
| 30Y | | | |

### Curve metrics
| Metric | Current | 1Y ago | 3Y percentile |
|--------|---------|---------|---------------|
| 2s10s (bp) | | | |
| 5s30s (bp) | | | |
| 2s5s10s butterfly (bp) | | | |
| Shape | | | |

### Real-rate decomposition
| Tenor | Nominal | Breakeven | Real | Signal |
|-------|---------|-----------|------|--------|
| 2Y | | | | Accommodative / Restrictive |
| 10Y | | | | Accommodative / Restrictive |

### Trade framing
For each idea: structure (e.g. 2s10s steepener), the thesis in one or two sentences, what would
invalidate it, and DV01 sizing **against the government curve**. State explicitly that these are
Treasury-relative, not swap-relative.

## What this skill does not do

- Swap spreads, swap curve shape, basis, or swaption vols — no free source.
- Inflation breakeven curves as a separate feed — derived from nominal minus TIPS instead.
- Live pricing.

Say so rather than approximating. A labelled gap is a useful answer; a fabricated swap spread is not.
