---
name: cim-builder
description: Structure and draft a Confidential Information Memorandum for sell-side M&A processes. Organizes company information into a professional, investor-ready document with consistent formatting and narrative flow. Use when preparing sell-side materials, drafting a CIM, or organizing company data for a sale process. Triggers on "CIM", "confidential information memorandum", "offering memorandum", "info memo", "draft CIM", or "sell-side materials".
---

# CIM Builder

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

### Step 1: Gather Source Materials

Ask for available inputs:
- Management presentations
- Historical financials (3-5 years)
- Budget/forecast
- Company website and marketing materials
- Customer data (anonymized if needed)
- Org chart
- Prior presentations or board decks
- Quality of earnings report (if available)

### Step 2: CIM Structure

Standard CIM table of contents:

**I. Executive Summary** (2-3 pages)
- Company overview — what they do, why they win
- Investment highlights (5-7 key selling points)
- Financial summary — headline revenue, EBITDA, growth, margins
- Transaction overview — what's being sold, indicative timeline

**II. Company Overview** (3-5 pages)
- History and founding story
- Mission and value proposition
- Products and services description
- Business model and revenue streams
- Key differentiators and competitive advantages

**III. Industry Overview** (3-5 pages)
- Market size and growth dynamics (TAM/SAM/SOM)
- Key industry trends and tailwinds
- Competitive landscape
- Regulatory environment
- Barriers to entry

**IV. Growth Opportunities** (2-3 pages)
- Organic growth levers (new products, markets, pricing)
- M&A / add-on opportunities
- Operational improvements
- Technology investments
- White space analysis

**V. Customers & Sales** (3-5 pages)
- Customer overview (number, segments, geography)
- Top customer analysis (anonymized if pre-LOI)
- Customer concentration and retention metrics
- Sales process and go-to-market strategy
- Pipeline and backlog

**VI. Operations** (2-3 pages)
- Organizational structure
- Key personnel
- Facilities and geographic footprint
- Technology and systems
- Supply chain / vendor relationships

**VII. Financial Overview** (5-8 pages)
- Historical income statement (3-5 years)
- Revenue analysis — by segment, geography, customer type
- EBITDA bridge and margin analysis
- Balance sheet overview
- Cash flow summary
- Capital expenditure history
- Working capital analysis
- Management forecast / budget (if included)

**VIII. Appendix**
- Detailed financial statements
- Customer list (anonymized)
- Product catalog
- Management bios

### Step 3: Drafting Guidelines

- **Tone**: Professional, factual, compelling but not hyperbolic
- **Narrative**: Tell a story — why this business is attractive, defensible, and positioned for growth
- **Data-driven**: Support every claim with data. "Strong growth" → "Revenue grew at a 15% CAGR from 2021-2024"
- **Visuals**: Charts and graphs for financial trends, market size, competitive positioning
- **Length**: 40-60 pages total — enough detail to inform first-round bids, not so long buyers won't read it
- **Confidentiality**: Include a disclaimer page. Anonymize sensitive customer data unless seller approves

### Step 4: Output

- Word document (.docx) with professional formatting
- Separate Excel appendix with detailed financials
- Charts and exhibits embedded in the document

## Important Notes

- The CIM is a sales document — lead with strengths, but don't hide material issues (buyers will find them in diligence)
- Investment highlights should address the 3 things every buyer cares about: growth potential, margin profile, and defensibility
- Financial normalization / pro forma adjustments should be clearly labeled and explained
- Work with legal on the confidentiality disclaimer and any regulatory disclosures
- Get management to review for factual accuracy before distribution
- The CIM sets expectations on valuation — make sure the narrative supports the asking price

- **Runbook:** [`references/runbook-cim.md`](references/runbook-cim.md) — the end-to-end walkthrough (which skills to load in what order, and the output contract).
