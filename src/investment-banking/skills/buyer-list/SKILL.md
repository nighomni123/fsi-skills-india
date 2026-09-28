---
name: buyer-list
description: Build and organize a universe of potential acquirers for sell-side M&A processes. Identifies strategic and financial buyers, assesses fit, and prioritizes outreach. Use when preparing for a sell-side mandate, building a buyer universe, or evaluating potential partners. Triggers on "buyer list", "buyer universe", "potential acquirers", "who would buy this", "strategic buyers", or "financial sponsors".
---

# Buyer List

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

## Workflow

### Step 1: Understand the Target

- Company description, sector, and business model
- Revenue, EBITDA, and growth profile
- Key assets and capabilities (IP, customer relationships, geographic footprint, team)
- Expected valuation range
- Seller preferences (strategic vs. financial, management continuity, timeline)

### Step 2: Strategic Buyers

Identify strategic acquirers across categories:

**Direct Competitors**
- Companies in the same space that would gain market share
- Rationale: Revenue synergies, eliminate competitor, scale

**Adjacent Players**
- Companies in adjacent markets that could expand into the target's space
- Rationale: Product extension, cross-sell, new market entry

**Vertical Integrators**
- Customers or suppliers that could integrate vertically
- Rationale: Supply chain control, margin capture, strategic lock-in

**Platform Builders**
- Large companies building a platform in the space through M&A
- Rationale: Tuck-in acquisition, fill capability gap

For each strategic buyer, assess:

| Buyer | Sector | Revenue | Strategic Fit | Financial Capacity | M&A Track Record | Likelihood | Priority |
|-------|--------|---------|--------------|-------------------|------------------|------------|----------|
| | | | High/Med/Low | | Active/Moderate/None | | A/B/C |

### Step 3: Financial Sponsors

Identify PE/financial buyers:

**Platform Investors**
- Sponsors looking for a new platform in this sector
- Criteria: Fund size, sector focus, deal size range

**Add-on Buyers**
- Sponsors with existing portfolio companies that could acquire the target as a bolt-on
- Identify the specific portfolio company and synergy rationale

**Growth Equity**
- For earlier-stage or high-growth targets
- Minority vs. majority preference

For each sponsor:

| Sponsor | Fund Size | Sector Focus | Portfolio Overlap | Recent Activity | Priority |
|---------|-----------|-------------|-------------------|-----------------|----------|
| | | | | | A/B/C |

### Step 4: Prioritization

Tier the buyer list:

- **Tier 1 (5-10)**: Highest strategic fit, proven acquirers, clear rationale — contact first
- **Tier 2 (10-15)**: Good fit but less obvious — contact in second wave
- **Tier 3 (10-20)**: Possible but lower probability — contact if process needs broadening

### Step 5: Contact Mapping

For each Tier 1 buyer:
- Key decision maker (CEO, Corp Dev head, Partner)
- Relationship status (existing relationship, cold outreach, need introduction)
- Known preferences or constraints (size, geography, structure)
- Best approach channel

### Step 6: Output

- Excel workbook with:
  - Strategic buyers tab (sorted by tier)
  - Financial sponsors tab (sorted by tier)
  - Contact mapping for Tier 1
  - Summary statistics (total buyers by tier, by type)
- One-page buyer universe summary for the engagement letter or pitch

## Important Notes

- Quality over quantity — a focused list of 30-40 well-researched buyers beats a list of 200 names
- Research recent M&A activity — buyers who just did a deal in the space are either hungry for more or tapped out
- Check for antitrust concerns with direct competitors — flag any that might face regulatory issues
- Financial sponsors: check fund vintage and deployment pace — a fund nearing end of investment period may be more motivated
- Always ask the seller if there are buyers they want included or excluded
- Update the list as the process progresses — move buyers between tiers based on feedback

- **Runbook:** [`references/runbook-buyer-list.md`](references/runbook-buyer-list.md) — the end-to-end walkthrough (which skills to load in what order, and the output contract).
