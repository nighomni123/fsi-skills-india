---
name: dd-checklist
description: Generate and track comprehensive due diligence checklists tailored to the target company's sector, deal type, and complexity. Covers all major workstreams with request lists, status tracking, and red flag escalation. Use when kicking off diligence, organizing a data room review, or tracking outstanding items. Triggers on "dd checklist", "due diligence tracker", "diligence request list", "what do we still need", or "data room review".
---

# Due Diligence Checklist

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

### Step 1: Scope the Diligence

Ask the user for:
- **Target company**: Name, sector, business model
- **Deal type**: Platform acquisition, add-on, growth equity, recap, carve-out
- **Deal size / complexity**: Determines depth of diligence
- **Key concerns**: Any known issues to prioritize (customer concentration, regulatory, environmental, etc.)
- **Timeline**: When is LOI / close targeted?

### Step 2: Generate Workstream Checklists

Generate a checklist across all major workstreams, tailored to the sector:

**Financial Due Diligence**
- Quality of earnings (QoE) — revenue and EBITDA adjustments
- Working capital analysis — normalized vs. actual
- Debt and debt-like items
- Capital expenditure (maintenance vs. growth)
- Tax structure and exposure
- Audit history and accounting policies
- Pro forma adjustments (run-rate, synergies)

**Commercial Due Diligence**
- Market size and growth (TAM/SAM/SOM)
- Competitive positioning and market share
- Customer analysis — concentration, retention, NPS
- Pricing power and contract structure
- Sales pipeline and backlog
- Go-to-market effectiveness

**Legal Due Diligence**
- Corporate structure and org chart
- Material contracts (customer, supplier, partnership)
- Litigation history and pending claims
- IP portfolio and protection
- Regulatory compliance
- Employment agreements and non-competes

**Operational Due Diligence**
- Management team assessment
- Organizational structure and key person risk
- IT systems and infrastructure
- Supply chain and vendor dependencies
- Facilities and real estate
- Insurance coverage

**HR / People Due Diligence**
- Org chart and headcount trends
- Compensation benchmarking
- Benefits and pension obligations
- Key employee retention risk
- Culture assessment
- Union/labor agreements

**IT / Technology Due Diligence** (for tech-enabled businesses)
- Technology stack and architecture
- Technical debt assessment
- Cybersecurity posture
- Data privacy compliance (GDPR, CCPA, SOC2)
- Product roadmap and R&D spend
- Scalability assessment

**Environmental / ESG** (where applicable)
- Environmental liabilities
- Regulatory compliance history
- ESG risks and opportunities

### Step 3: Status Tracking

For each item, track:

| Item | Workstream | Priority | Status | Owner | Notes |
|------|-----------|----------|--------|-------|-------|
| QoE report | Financial | P0 | Pending | | |
| Customer interviews | Commercial | P0 | In Progress | | 3 of 10 complete |

Status options: Not Started → Requested → Received → In Review → Complete → Red Flag

### Step 4: Red Flag Summary

Maintain a running list of red flags discovered during diligence:
- What was found
- Which workstream
- Severity (deal-breaker / significant / manageable)
- Mitigant or path to resolution
- Impact on valuation or deal terms

### Step 5: Output

- Excel workbook with tabs per workstream (default)
- Summary dashboard: % complete by workstream, outstanding items, red flags
- Weekly status update format for deal team

## Sector-Specific Additions

Automatically add relevant items based on sector:
- **Software/SaaS**: ARR quality, cohort analysis, hosting costs, SOC2
- **Healthcare**: Regulatory approvals, reimbursement risk, payor mix
- **Industrial**: Equipment condition, environmental remediation, safety record
- **Financial services**: Regulatory capital, compliance history, credit quality
- **Consumer**: Brand health, channel mix, seasonality, inventory management

## Important Notes

- Prioritize P0 items that are gating to LOI or close
- Flag items where the seller is slow to respond — may indicate issues
- Cross-reference data room contents against the checklist to identify gaps
- Update the checklist as diligence progresses — it's a living document

- **Runbook:** [`references/runbook-dd-checklist.md`](references/runbook-dd-checklist.md) — the end-to-end walkthrough (which skills to load in what order, and the output contract).
