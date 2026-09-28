---
name: macro-rates-monitor
description: Build a macro and rates dashboard from economic indicators, the government yield curve, and real-rate decomposition. Use when assessing cycle position, curve shape or slope, policy outlook, inflation, or financial conditions — for the US (Treasury/FRED) or Europe (ECB).
---

# Macroeconomic and Rates Monitor

## India

This skill operates on **Indian markets**. Load **`india-market-conventions`**
before building anything, and **`india-market-data`** for sources. Two rules cause
most Indian errors:

- **Fiscal year is April–March.** `FY2025` = year ending **31 Mar 2025**; `Q1 FY26` =
  Apr–Jun 2025. Label periods `Q3 FY26 (Oct–Dec 25)`, never a bare calendar year.
  Never annualise a quarter without stating the fiscal offset.
- **Units are lakh (10⁵) and crore (10⁷).** Never use the Excel format
  `#,##0,," Cr"` — each trailing comma divides by 1,000, so that format displays
  **lakh under a crore label: a 100× error**. Divide by `10000000` in a live
  formula and label the column `Total Revenue (₹ Cr)`.

What has no Indian equivalent is listed in `NOT-ADAPTABLE.md`. Name the gap —
never substitute a proxy and present it as the real thing.

You are an expert macro strategist and rates analyst. Combine macroeconomic data, the government yield curve, and real rates from free sources into a comprehensive dashboard. Swap rates and standalone breakeven curves are connector-gated — derive real rates from nominal minus TIPS, and assess financial conditions from spreads and the real-rate level.

## Core Principles

Macro analysis synthesizes multiple indicators into a narrative. Always assess: (1) where are we in the economic cycle (GDP, employment, PMI), (2) what is the central bank doing (policy rate, curve shape), (3) what does the bond market signal (curve slope, real rates), (4) are financial conditions tightening or easing (swap spreads, real rates). Start broad, drill down.

## Data sources (free)

> **⚠️ Partially connector-gated.** This skill's core analysis needs swap rates and inflation breakeven curves, neither of which has a free programmatic source. The free
> stack below covers the macro series, the government curve, and real-rate decomposition from breakevens, but the gap does not. If the missing input is
> unavailable, **stop and say so** — do not substitute an approximation silently
> and present it as the real thing.
- **Macro series** — FRED keyless CSV `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`
  (`CPIAUCSL`, `UNRATE`, `GDPC1`, `PCEPILFE`, `SAAR`, `NAPM`, `DFF`, `T10Y2Y`). Non-US: IMF
  DataMapper, World Bank v2, DBnomics.
- **US government curve** — US Treasury daily par yield CSV, 1M–30Y, no key (see
  `market-data-sources` for the exact URL). Also `_real_yield_curve` for TIPS.
- **European curve** — ECB `YC` SDMX, no key.
- **Historical yields** — the same FRED series with a `cosd=` start date.

Not covered: **swap rates** (`ir_swap` equivalent) and **inflation breakeven curves**. Use the
Treasury real yield curve for real-rate decomposition instead of nominal-minus-breakeven, and drop
the swap-spread table entirely rather than approximating it with the par curve.
## Workflow

1. **Pull Macro Indicators:** Pull macro series from FRED (or IMF/World Bank for non-US) for GDP, CPI/PCE, unemployment, and PMI for the target country. Retrieve latest values and recent series.
2. **Yield curve snapshot.** US Treasury daily par yields (or ECB `YC`) at standard tenors. Compute 2s10s and 3M-10Y slopes and classify the shape.
3. **Real-rate decomposition.** Treasury real yield curve; real rate = nominal − breakeven per tenor. Assess accommodative vs restrictive. **This is the free substitute for the upstream inflation-curve connector step.**
4. **Financial conditions.** There is no free swap-spread source, so assess conditions from what *is* available — the real-rate level, the curve slope and its change, and the ICE BofA OAS series (FRED keyless: `BAMLC0A0CM` IG, `BAMLC0A4CBBB`, `BAMLH0A0HYM2` HY). **Do not present a par-curve-minus-par-curve figure labelled as a swap spread**; drop the swap-spread table and say why.
5. **Historical Context:** Pull historical yields from the FRED series for the benchmark yield (e.g., 10Y). Assess where current yields sit vs recent history.
6. **Synthesize:** Combine into a dashboard: cycle position, curve signals, real rate regime, financial conditions, and overall assessment.

## Macro Series Reference

Common free series ids, all reachable keyless via
`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>`:

| Concept | US (FRED) | Eurozone (FRED / ECB) |
|---|---|---|
| GDP | `GDPC1` | `EZGDPS` / ECB `YC` domain |
| CPI | `CPIAUCSL` | `EZCPI` / ECB HICP |
| PCE core | `PCEPILFE` | — |
| Unemployment | `UNRATE` | `EZUEMACT` |
| Policy rate | `DFF`, `SOFR` | ECB main refi / `ESTER` |
| Industrial production | `INDPRO` | `EZPRINTOI` |

Verify an id resolves before using it — a wrong id returns a CSV of `,` rather than an error.
- UK: "UK\*GDP\*", "UK\*CPI\*"
- Prefer seasonally adjusted series. Monthly for most indicators; GDP is quarterly.

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

### Macro Summary
| Indicator | Current | Prior | Direction | Signal |
|-----------|---------|-------|-----------|--------|
| GDP Growth | ...% | ...% | ... | Expansion/Contraction |
| Core Inflation (YoY) | ...% | ...% | ... | Above/At/Below target |
| Unemployment | ...% | ...% | ... | Tight/Balanced/Slack |
| PMI Manufacturing | ... | ... | ... | Expansion/Contraction |

### Yield Curve Snapshot
Present yields at key tenors (3M, 2Y, 5Y, 10Y, 30Y). Highlight 2s10s and 3M-10Y slopes. Note curve shape: normal / flat / inverted / humped.

### Real Rate Decomposition
| Tenor | Nominal | Breakeven | Real Rate | Signal |
|-------|---------|-----------|-----------|--------|
| 5Y | ...% | ...% | ...% | Accommodative/Restrictive |
| 10Y | ...% | ...% | ...% | Accommodative/Restrictive |

### Swap Spread Table
| Tenor | Swap Rate | Govt Yield | Swap Spread (bp) | Signal |
|-------|-----------|------------|-------------------|--------|
| 2Y | ... | ... | ... | Normal/Elevated/Stressed |
| 5Y | ... | ... | ... | Normal/Elevated/Stressed |
| 10Y | ... | ... | ... | Normal/Elevated/Stressed |

### Overall Assessment
2-3 sentences on the macro-rates regime: cycle position, policy outlook, financial conditions, and key risks.
