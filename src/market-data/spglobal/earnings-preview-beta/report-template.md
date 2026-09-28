# HTML Report Template Reference

Use this template as the foundation for the single-company earnings preview HTML report. Customize the data, charts, and narrative content based on the research gathered in Phases 1-5.

## HTML Structure

The report is a single self-contained HTML file with:
- Embedded CSS (no external stylesheets)
- Chart.js loaded from CDN for interactive charts
- Print-friendly styles via `@media print`
- Responsive layout that works on screens and in print
- Target: 4-5 printed pages

## Complete Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Earnings Preview — [COMPANY] ([TICKER]) — [DATE]</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js" integrity="sha384-vsrfeLOOY6KuIYKDlmVH5UiBmgIdB1oEf7p01YgWHuqmOHfZr374+odEv96n9tNC" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.1.0/dist/chartjs-plugin-annotation.min.js" integrity="sha384-3N9GHhCtN3CQef6tNfqgZlv7sQLYIkcChN+uaTZ7xVdzKYp/SjBNPxa92+hM7EAY" crossorigin="anonymous"></script>
  <style>
    /* ── Reset & Base ── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { font-size: 15px; }
    body {
      font-family: 'Arial Narrow', Arial, sans-serif;
      color: #1a1a2e;
      background: #fff;
      line-height: 1.6;
    }

    /* ── Layout ── */
    .page {
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 48px;
    }
    .page-break {
      page-break-before: always;
      border-top: 2px solid #1a1a4e;
      margin-top: 48px;
      padding-top: 32px;
    }

    /* ── Header / Cover ── */
    .cover-header {
      border-bottom: 3px solid #1a1a4e;
      padding-bottom: 16px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    .cover-header .brand {
      font-size: 24px;
      font-weight: bold;
      color: #1a1a4e;
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    .cover-header .sector {
      font-size: 13px;
      color: #555;
    }
    .cover-header .date {
      font-size: 14px;
      color: #333;
      text-align: right;
    }
    .report-title {
      font-size: 26px;
      font-weight: bold;
      color: #1a1a2e;
      margin: 20px 0 16px 0;
      line-height: 1.3;
    }

    /* ── Executive Thesis ── */
    .executive-summary {
      font-size: 14px;
      line-height: 1.65;
      color: #222;
      margin-bottom: 16px;
    }
    .executive-summary p {
      margin-bottom: 10px;
      text-align: justify;
    }
    .executive-summary ul {
      margin: 8px 0 10px 20px;
      font-size: 13.5px;
    }
    .executive-summary ul li {
      margin-bottom: 5px;
      line-height: 1.5;
    }
    blockquote {
      border-left: 3px solid #b0b8c8;
      padding: 6px 14px;
      margin: 8px 0 8px 12px;
      font-style: italic;
      color: #444;
      background: #f9fafb;
      font-size: 12.5px;
      line-height: 1.5;
    }

    /* ── Data Provenance Line ── */
    .provenance {
      font-size: 10.5px;
      color: #444;
      background: #f4f5f9;
      border-left: 3px solid #1a1a4e;
      padding: 5px 10px;
      margin: 10px 0 4px 0;
      line-height: 1.45;
    }

    /* ── Section Headings ── */
    h2.section-title {
      font-size: 18px;
      font-weight: 700;
      color: #1a1a4e;
      border-bottom: 2px solid #1a1a4e;
      padding-bottom: 5px;
      margin: 28px 0 14px 0;
    }
    h3.subsection-title {
      font-size: 14px;
      font-weight: 600;
      color: #1a1a4e;
      margin: 16px 0 8px 0;
    }
    h4.figure-title {
      font-size: 12px;
      font-weight: 600;
      color: #444;
      margin: 14px 0 6px 0;
    }

    /* ── Tables ── */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      margin: 10px 0 16px 0;
    }
    thead th {
      background: #1a1a4e;
      color: #fff;
      padding: 7px 10px;
      text-align: left;
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    tbody td {
      padding: 6px 10px;
      border-bottom: 1px solid #e0e0e0;
    }
    tbody tr:nth-child(even) {
      background: #f9fafb;
    }
    tbody tr:hover {
      background: #eef0f5;
    }
    .num { text-align: right; font-variant-numeric: tabular-nums; }
    .pos { color: #0d7a3e; font-weight: 600; }
    .neg { color: #c0392b; font-weight: 600; }
    .neutral { color: #555; }
    .highlight-row { background: #e8eaf6 !important; font-weight: 600; }
    tfoot td { background: #f0f1f5; font-weight: 600; border-top: 2px solid #1a1a4e; }
    /* Consensus-basis tag: makes the IBES-vs-Yahoo distinction visible at the cell */
    .basis {
      display: inline-block;
      font-size: 9px;
      font-weight: 700;
      letter-spacing: 0.4px;
      text-transform: uppercase;
      color: #1a1a4e;
      background: #e8eaf6;
      border: 1px solid #c3c8dd;
      border-radius: 2px;
      padding: 0 4px;
      margin-left: 4px;
      vertical-align: 1px;
    }
    .source code {
      font-family: 'Courier New', monospace;
      font-size: 9.5px;
      background: #f0f1f5;
      padding: 0 3px;
      border-radius: 2px;
    }

    /* ── Chart Containers ── */
    .chart-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin: 12px 0 20px 0;
    }
    .chart-container {
      position: relative;
      background: #fafbfc;
      border: 1px solid #e8e8e8;
      border-radius: 4px;
      padding: 14px;
    }
    .chart-container canvas {
      max-height: 260px;
    }
    .chart-full {
      grid-column: 1 / -1;
    }

    /* ── Compact Lists ── */
    .key-metrics ul, .themes ul, .news-list ul {
      margin: 6px 0 6px 18px;
      font-size: 13px;
      line-height: 1.55;
    }
    .key-metrics li, .themes li, .news-list li {
      margin-bottom: 5px;
    }

    /* ── Data Reference Links ── */
    a.data-ref {
      color: #1a1a4e;
      text-decoration: none;
      border-bottom: 1px dotted transparent;
      transition: border-color 0.15s;
    }
    a.data-ref:hover {
      border-bottom-color: #1a1a4e;
    }

    /* ── Appendix ── */
    .appendix table {
      font-size: 10.5px;
    }
    .appendix thead th {
      font-size: 10px;
      padding: 5px 8px;
    }
    .appendix tbody td {
      padding: 4px 8px;
      font-size: 10.5px;
      vertical-align: top;
      line-height: 1.45;
    }
    .appendix .ref-id {
      font-weight: 600;
      color: #1a1a4e;
      white-space: nowrap;
    }
    .appendix .source-detail {
      font-size: 10px;
      color: #444;
    }
    .appendix .source-detail .formula {
      font-family: 'Courier New', monospace;
      font-size: 9.5px;
      color: #555;
    }
    .appendix .source-detail .excerpt {
      font-style: italic;
      color: #555;
    }
    .appendix .source-detail .src-label {
      font-weight: 600;
      color: #1a1a4e;
      font-size: 9.5px;
    }
    .appendix .source-detail a.data-ref {
      font-weight: 600;
    }
    .appendix a.src-url {
      color: #3366cc;
      text-decoration: underline;
      font-size: 10px;
      word-break: break-all;
    }
    .appendix a.src-url:hover {
      color: #1a1a4e;
    }
    .appendix .transcript-ref {
      font-weight: 600;
      color: #1a1a4e;
      font-size: 10px;
    }
    .appendix-group {
      font-size: 11px;
      font-weight: 700;
      color: #1a1a4e;
      background: #f0f1f5;
      padding: 4px 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* ── Source / Footer ── */
    .source {
      font-size: 10px;
      color: #999;
      margin-top: 3px;
      font-style: italic;
    }
    .ai-disclaimer {
      background-color: #fff3cd;
      border: 1px solid #ffc107;
      border-radius: 4px;
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 600;
      color: #664d03;
      text-align: center;
      margin-bottom: 12px;
    }
    .page-footer {
      border-top: 2px solid #1a1a4e;
      padding-top: 10px;
      margin-top: 32px;
      text-align: center;
    }
    .page-footer .footer-disclaimer {
      font-size: 11px;
      font-weight: 600;
      color: #664d03;
      background-color: #fff3cd;
      border: 1px solid #ffc107;
      border-radius: 4px;
      padding: 4px 10px;
      display: inline-block;
      margin-bottom: 4px;
    }
    .page-footer .footer-meta {
      font-size: 10px;
      color: #888;
    }

    /* ── Print Styles ── */
    @media print {
      body { font-size: 11px; }
      .page { padding: 16px; max-width: none; }
      .chart-container { break-inside: avoid; }
      table { break-inside: avoid; }
      .page-break { margin-top: 0; }
      .no-print { display: none; }
    }
  </style>
</head>
<body>
<div class="page">

  <!-- ════════════════════════════════════════════ -->
  <!-- PAGE 1: COVER & THESIS                       -->
  <!-- ════════════════════════════════════════════ -->
  <div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>
  <div class="cover-header">
    <div>
      <div class="brand">Earnings Preview</div>
      <div class="sector">[Industry] | [TICKER]</div>
    </div>
    <div class="date">[Full Date]</div>
  </div>

  <!-- Data provenance: MANDATORY. Consensus basis + retrieval date + latency caveat. -->
  <div class="provenance">
    Consensus basis: <strong>[IBES via Alpha Vantage | Yahoo Finance analyst estimates via yfinance]</strong>
    · Actuals: SEC EDGAR XBRL companyfacts (CIK [0000000000])
    · Prices: yfinance EOD close · Retrieved: [YYYY-MM-DD]
    · <strong>All prices and estimates are end-of-day or delayed — not real-time.</strong>
  </div>

  <h1 class="report-title">[Company Name] ([TICKER]) [Q# FY####] Earnings Preview: [Thematic Subtitle]</h1>

  <div class="executive-summary">
    <!-- Executive thesis: 2-3 short paragraphs + bullet points, in THIS order.
         1. Estimate revision  2. The bar  3. Consensus  4. Guidance
         5. Key metric  6. Catalyst  7. Key debate
         Weave in 3-4 management quotes as blockquotes where they support the thesis.
         Do NOT create a separate "Key Management Quotes" section.
         If no verbatim source exists (no IR transcript, no 8-K Ex-99.1), there are NO
         blockquotes — argue from the numbers instead. Never invent a quote. -->

    <p>[Opening 1-2 sentences: what we expect from this print, and why.]</p>

    <ul>
      <li><strong>Estimate revision:</strong> 90-day EPS drift <a href="#ref-N" class="data-ref">[+/-X.X%]</a>, net 30-day revision breadth <a href="#ref-N" class="data-ref">[+/-N]</a>, dispersion <a href="#ref-N" class="data-ref">[XX.X%]</a> and narrowing/widening — [read]</li>
      <li><strong>The bar:</strong> mean surprise <a href="#ref-N" class="data-ref">[+X.X%]</a> over the last <a href="#ref-N" class="data-ref">[N]</a> prints, σ <a href="#ref-N" class="data-ref">[X.X%]</a>, so the mean−1σ bar sits at <a href="#ref-N" class="data-ref">[+/-X.X%]</a> — [what that demands]</li>
      <li><strong>Consensus:</strong> We estimate <a href="#ref-1" class="data-ref">$X.XX</a> vs consensus mean <a href="#ref-2" class="data-ref">$X.XX</a> (range <a href="#ref-3" class="data-ref">$X.XX–$X.XX</a>), [rationale]</li>
      <li><strong>Revenue:</strong> We estimate <a href="#ref-4" class="data-ref">$XX.XB</a> vs consensus <a href="#ref-5" class="data-ref">$XX.XB</a>, [rationale]</li>
      <li><strong>Guidance:</strong> [What to expect on forward guidance — only if a verbatim source exists]</li>
      <li><strong>Key metric:</strong> [Most important sub-headline metric to watch]</li>
      <li><strong>Stock catalyst:</strong> [What would move the stock up/down post-print]</li>
      <li><strong>Key debate:</strong> [What bulls and bears disagree on]</li>
    </ul>

    <blockquote>"[Key management quote supporting a thesis point]" — [Speaker], [Q# FY####] Earnings Call</blockquote>

    <p>[1-2 sentences tying it together — your overall read on the setup.]</p>

    <blockquote>"[Another supporting quote]" — [Speaker], [Q# FY####] Earnings Call</blockquote>
  </div>

  <!-- ════════════════════════════════════════════ -->
  <!-- PAGE 2: ESTIMATES, THEMES & NEWS             -->
  <!-- ════════════════════════════════════════════ -->
  <div class="page-break">

    <!-- Figure A: Consensus & Revision Table -->
    <h2 class="section-title">Consensus, Revisions &amp; Surprise History — [Q# FY####]</h2>
    <h4 class="figure-title">Figure A: Consensus &amp; Estimate Revisions — [Q# FY####]</h4>
    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th class="num">Consensus Mean</th>
          <th class="num">Low–High Range</th>
          <th class="num">Our Estimate</th>
          <th class="num">30d Drift</th>
          <th class="num">90d Drift</th>
          <th class="num">y/y Change</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>EPS <span class="basis">IBES</span></td><td class="num"><a href="#ref-N" class="data-ref">$[X.XX]</a></td><td class="num"><a href="#ref-N" class="data-ref">$[X.XX]–$[X.XX]</a></td><td class="num"><a href="#ref-N" class="data-ref">$[X.XX]</a></td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-X.X%]</a></td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-X.X%]</a></td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-X.X%]</a></td></tr>
        <tr><td>Revenue <span class="basis">IBES</span></td><td class="num"><a href="#ref-N" class="data-ref">$[XX.X]B</a></td><td class="num"><a href="#ref-N" class="data-ref">$[XX.X]B–$[XX.X]B</a></td><td class="num"><a href="#ref-N" class="data-ref">$[XX.X]B</a></td><td class="num neutral"><a href="#ref-N" class="data-ref">n/a</a></td><td class="num neutral"><a href="#ref-N" class="data-ref">n/a</a></td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-X.X%]</a></td></tr>
        <tr><td>Gross Margin</td><td class="num"><a href="#ref-N" class="data-ref">[XX.X%]</a></td><td class="num neutral">—</td><td class="num"><a href="#ref-N" class="data-ref">[XX.X%]</a></td><td class="num neutral">—</td><td class="num neutral">—</td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-XXbps]</a></td></tr>
        <tr><td>Operating Income</td><td class="num"><a href="#ref-N" class="data-ref">$[X.X]B</a></td><td class="num neutral">—</td><td class="num"><a href="#ref-N" class="data-ref">$[X.X]B</a></td><td class="num neutral">—</td><td class="num neutral">—</td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-X.X%]</a></td></tr>
        <!-- Add 2-3 company-specific KPIs below (e.g., comp sales, eComm growth, membership revenue) -->
        <tr><td>[Company KPI 1]</td><td class="num">[Value]</td><td class="num neutral">—</td><td class="num">[Value]</td><td class="num neutral">—</td><td class="num neutral">—</td><td class="num [pos|neg]">[Change]</td></tr>
        <tr><td>[Company KPI 2]</td><td class="num">[Value]</td><td class="num neutral">—</td><td class="num">[Value]</td><td class="num neutral">—</td><td class="num neutral">—</td><td class="num [pos|neg]">[Change]</td></tr>
      </tbody>
    </table>
    <div class="source">Source: Alpha Vantage <code>EARNINGS_ESTIMATES</code> (IBES-sourced), retrieved [YYYY-MM-DD].
      Revenue drift is <code>n/a</code> — that endpoint carries no revenue revision history. Do not construct one.
      Blank drift cells are genuine absences in the response, not zeros.</div>

    <!-- Figure B: Surprise History Table -->
    <h4 class="figure-title">Figure B: Surprise History — Last 8 Prints</h4>
    <table>
      <thead>
        <tr>
          <th>Fiscal Period</th>
          <th class="num">Reported EPS</th>
          <th class="num">Consensus EPS</th>
          <th class="num">Surprise %</th>
          <th class="num">1-Day Post-Print</th>
          <th>Result</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>[Q# FY####]</td><td class="num"><a href="#ref-N" class="data-ref">$[X.XX]</a></td><td class="num"><a href="#ref-N" class="data-ref">$[X.XX]</a></td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-X.X%]</a></td><td class="num [pos|neg]"><a href="#ref-N" class="data-ref">[+/-X.X%]</a></td><td>[Beat | Miss | In line]</td></tr>
        <!-- 8 rows, most recent first. Colour the surprise column mechanically. -->
      </tbody>
      <tfoot>
        <tr class="highlight-row">
          <td colspan="3">Beat rate / mean surprise % / trimmed mean / σ / the bar (mean − 1σ)</td>
          <td class="num"><a href="#ref-N" class="data-ref">[x of 8]</a></td>
          <td class="num"><a href="#ref-N" class="data-ref">[+X.X%]</a></td>
          <td><a href="#ref-N" class="data-ref">bar = [+/-X.X%]</a></td>
        </tr>
      </tfoot>
    </table>
    <div class="source">Source: Alpha Vantage <code>EARNINGS</code> (reportedEPS / estimatedEPS / surprisePercentage), retrieved [YYYY-MM-DD];
      1-day post-print moves computed from yfinance EOD closes. A quarter with a missing estimate is
      <strong>excluded</strong> from every statistic and named in Manual Review — never silently dropped.</div>

    <!-- Key Metrics Beyond Headline EPS -->
    <h3 class="subsection-title">Key Metrics Beyond Headline EPS</h3>
    <div class="key-metrics">
      <ul>
        <li><strong>[Metric 1]:</strong> [What consensus/management expects, why it matters. Be specific with numbers.]</li>
        <li><strong>[Metric 2]:</strong> [Details]</li>
        <li><strong>[Metric 3]:</strong> [Details]</li>
        <!-- 3-5 items -->
      </ul>
    </div>

    <!-- Themes to Watch -->
    <h3 class="subsection-title">Themes to Watch</h3>
    <div class="themes">
      <ul>
        <li><strong>[Theme 1]:</strong> [1-2 sentences max. Forward-looking, specific.]</li>
        <li><strong>[Theme 2]:</strong> [Details]</li>
        <li><strong>[Theme 3]:</strong> [Details]</li>
        <!-- 3-5 themes -->
      </ul>
    </div>

    <!-- Recent News & Developments -->
    <h3 class="subsection-title">Recent News &amp; Developments</h3>
    <div class="news-list">
      <ul>
        <li><strong>[Filing date]:</strong> [Headline] — [Brief impact assessment, one line] — <a href="[EDGAR filing-index URL]" target="_blank" class="src-url">[Form 8-K, [Filer Name]]</a></li>
        <li><strong>[Date]:</strong> [Headline] — [Impact] — <a href="[URL]" target="_blank" class="src-url">[Source]</a></li>
        <li><strong>[Date]:</strong> [Headline] — [Impact] — <a href="[URL]" target="_blank" class="src-url">[Source]</a></li>
        <!-- 3-5 material items, last 60-90 days. Every item carries a clickable source URL.
             If a category returns nothing, write it as a finding rather than padding:
             "no material 8-K events identified in the last 60 days from EDGAR full-text search". -->
      </ul>
    </div>
    <div class="source">Source: SEC EDGAR full-text search
      (<code>efts.sec.gov/LATEST/search-index?q=…&amp;forms=8-K&amp;ciks=…</code>), company IR pages,
      yfinance news. Analyst actions from Yahoo Finance are <strong>not</strong> IBES and carry no
      source document — unverifiable actions go to Manual Review, not the narrative.</div>

  </div>

  <!-- ════════════════════════════════════════════ -->
  <!-- PAGES 3-5: FIGURES                           -->
  <!-- All charts and tables, numbered sequentially -->
  <!-- ════════════════════════════════════════════ -->
  <div class="page-break">
    <h2 class="section-title">Financial & Competitive Analysis</h2>

    <!-- Figure 1: Quarterly Revenue & Diluted EPS -->
    <div class="chart-row">
      <div class="chart-container">
        <h4 class="figure-title">Figure 1: Quarterly Revenue & Diluted EPS</h4>
        <canvas id="chart-rev-eps"></canvas>
        <div class="source">Source: SEC EDGAR XBRL companyfacts, CIK [0000000000] —
          us-gaap:Revenues and us-gaap:EarningsPerShareDiluted. Derived quarters are marked (FY − 9M).</div>
      </div>

      <!-- Figure 2: Margin Trends -->
      <div class="chart-container">
        <h4 class="figure-title">Figure 2: Margin Trends (Gross & Operating %)</h4>
        <canvas id="chart-margins"></canvas>
        <div class="source">Source: SEC EDGAR XBRL companyfacts — us-gaap:GrossProfit / us-gaap:OperatingIncomeLoss
          over us-gaap:Revenues. Calculated; no quarter is interpolated.</div>
      </div>
    </div>

    <!-- Figure 3: Revenue Growth y/y % -->
    <div class="chart-row">
      <div class="chart-container chart-full">
        <h4 class="figure-title">Figure 3: Revenue Growth y/y (%)</h4>
        <canvas id="chart-rev-growth" style="max-height: 200px;"></canvas>
        <div class="source">Source: SEC EDGAR XBRL companyfacts (calculated). Quarters with no derivable
          year-ago figure are omitted, not zero-filled.</div>
      </div>
    </div>

    <!-- Figure 4: Business Segment Revenue -->
    <!-- Figure 4: Business Segment Revenue — DELETE THIS FIGURE ENTIRELY if segment detail is not
         retrievable from free sources. Never infer segments from the total. -->
    <h4 class="figure-title">Figure 4: Business Segment Revenue</h4>
    <table>
      <thead>
        <tr>
          <th>Segment</th>
          <th class="num">Latest Q Rev ($M)</th>
          <th class="num">% of Total</th>
          <th class="num">y/y Change</th>
        </tr>
      </thead>
      <tbody>
        <!-- Populate from XBRL segment members (srt:StatementBusinessSegmentsAxis) or the
             10-Q/10-K segment footnote — record which in the source line. Colour y/y change with
             pos/neg classes. If a prior-year quarter is missing, write "y/y not available". -->
      </tbody>
    </table>
    <div class="source">Source: SEC EDGAR XBRL companyfacts, CIK [0000000000] (segment members) or the
      segment footnote in the [Form 10-Q/10-K, filed YYYY-MM-DD].</div>
  </div>

  <!-- Page break for stock & competitor charts -->
  <div class="page-break">

    <!-- Figure 5: 1-Year Stock Price with Earnings Dates -->
    <div class="chart-row">
      <div class="chart-container chart-full">
        <h4 class="figure-title">Figure 5: 1-Year Stock Price with Earnings Dates</h4>
        <canvas id="chart-price-annotated" style="max-height: 300px;"></canvas>
        <div class="source">Source: yfinance <code>Ticker("[TICKER]").history(period="1y").Close</code> — EOD,
          retrieved [YYYY-MM-DD]. Earnings markers from Alpha Vantage <code>EARNINGS</code>
          <code>reportedDate</code>. Not real-time.</div>
      </div>
    </div>

    <!-- Figure 6: Stock Performance vs. Competitors (Indexed to 100) -->
    <div class="chart-row">
      <div class="chart-container chart-full">
        <h4 class="figure-title">Figure 6: Stock Performance vs. Competitors — 1 Year (Indexed to 100)</h4>
        <canvas id="chart-comp-perf" style="max-height: 300px;"></canvas>
        <div class="source">Source: yfinance EOD closes, all tickers rebased to the <strong>same common
          base date</strong> ([YYYY-MM-DD]) — see appendix. Mixed base dates are not permitted.</div>
      </div>
    </div>
  </div>

  <div class="page-break">

    <!-- Figure 7: LTM P/E vs. Competitors -->
    <div class="chart-row">
      <div class="chart-container chart-full">
        <h4 class="figure-title">Figure 7: LTM P/E vs. Competitors</h4>
        <canvas id="chart-pe-comp" style="max-height: 280px;"></canvas>
        <div class="source">Source: yfinance EOD close ÷ sum of each company's own most recent 4
          reported quarters (SEC EDGAR XBRL for the subject; yfinance / company filings for peers).</div>
      </div>
    </div>

    <!-- Figure 8: Competitor Comparison Table — the NTM P/E column CARRIES THE CONSENSUS BASIS.
         Subject NTM EPS = IBES (Alpha Vantage). Peer NTM EPS = Yahoo Finance analyst estimates.
         Never present these in one unlabelled column. -->
    <h4 class="figure-title">Figure 8: Competitor Comparison</h4>
    <table>
      <thead>
        <tr>
          <th>Ticker</th>
          <th>Company</th>
          <th class="num">Mkt Cap ($B)</th>
          <th class="num">LTM P/E</th>
          <th class="num">NTM P/E</th>
          <th class="num">YTD %</th>
          <th class="num">1-Yr %</th>
        </tr>
      </thead>
      <tbody>
        <!-- Highlight the subject company row with class="highlight-row".
             Add a <span class="basis">IBES</span> / <span class="basis">YAHOO</span> tag to the
             NTM P/E cell of every row. -->
      </tbody>
    </table>
    <div class="source">Source: yfinance (market cap, EOD closes, Yahoo consensus for peers);
      Alpha Vantage <code>EARNINGS_ESTIMATES</code> (IBES) for the subject's NTM EPS only;
      SEC EDGAR XBRL for reported EPS. <strong>NTM P/E is IBES for the subject and Yahoo-derived for
      peers — these are different contributor pools and the comparison is not strictly like-for-like.</strong></div>
  </div>

  <div class="page-break">

    <!-- Figure 9: Estimate Revisions — DELETE THIS FIGURE if fewer than two near-term quarters have
         usable revision data. Never chart a null as zero, and never chart far-dated quarters: on
         those the 7/30-day-ago averages simply equal the current average because the panel has not
         formed, so the "drift" is structurally zero and meaningless. -->
    <div class="chart-row">
      <div class="chart-container chart-full">
        <h4 class="figure-title">Figure 9: Estimate Revisions — 90-Day Drift vs. Net 30-Day Revision Breadth</h4>
        <canvas id="chart-revisions" style="max-height: 300px;"></canvas>
        <div class="source">Source: Alpha Vantage <code>EARNINGS_ESTIMATES</code> (IBES-sourced), near-term
          fiscal quarters only, retrieved [YYYY-MM-DD]. Drift = (avg − avg_90_days_ago) ÷ |avg_90_days_ago|.
          Net breadth = up_trailing_30_days − down_trailing_30_days, with <code>null</code> excluded, never
          read as zero.</div>
      </div>
    </div>
  </div>

  <!-- ════════════════════════════════════════════ -->
  <!-- APPENDIX: DATA SOURCES & CALCULATIONS        -->
  <!-- ════════════════════════════════════════════ -->
  <div class="page-break appendix" id="appendix">
    <div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>
    <h2 class="section-title">Appendix: Data Sources, Calculations &amp; Manual Review</h2>
    <p style="font-size: 11px; color: #666; margin-bottom: 6px;">
      Every claim in this report is hyperlinked to its entry below. Click any highlighted text to jump here.
    </p>
    <p style="font-size: 11px; color: #444; background: #f4f5f9; border-left: 3px solid #1a1a4e; padding: 5px 10px; margin-bottom: 12px;">
      Consensus basis: <strong>[IBES via Alpha Vantage | Yahoo Finance analyst estimates via yfinance]</strong>
      · Actuals: SEC EDGAR XBRL companyfacts, CIK [0000000000] · Prices: yfinance EOD close
      · Retrieved: <strong>[YYYY-MM-DD]</strong> · <strong>All data is end-of-day or delayed — not real-time.</strong>
      · Alpha Vantage free tier: 25 requests/day, single-name only.
    </p>
    <table>
      <thead>
        <tr>
          <th style="width: 40px;">Ref</th>
          <th style="width: 170px;">Fact</th>
          <th style="width: 75px;">Value</th>
          <th>Source &amp; Derivation</th>
        </tr>
      </thead>
      <tbody>
        <!-- Group: Quarterly Financials — every row is an EDGAR XBRL fact with tag, frame, form,
             accession and filing date. A quarter derived as FY − 9M says so and names the accession. -->
        <tr><td colspan="4" class="appendix-group">Quarterly Financials</td></tr>
        <tr id="ref-1">
          <td class="ref-id">1</td>
          <td>[Q# FY#### Revenue]</td>
          <td class="num">$[XX.X]B</td>
          <td class="source-detail">
            <span class="src-label">SEC EDGAR XBRL</span> — companyfacts CIK[0000000000], us-gaap:Revenues,
            frame=CY20XXQ[X], form=10-Q, accn=[0000000000-XX-000000], filed [YYYY-MM-DD], retrieved [YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-2">
          <td class="ref-id">2</td>
          <td>[Q# FY#### Revenue — derived quarter]</td>
          <td class="num">$[XX.X]B</td>
          <td class="source-detail">
            <span class="src-label">SEC EDGAR XBRL</span> — companyfacts CIK[0000000000], us-gaap:Revenues,
            derived Q4 = FY $[XXX.X]M − 9M $[XXX.X]M, both from accn=[0000000000-XX-000000] (same 10-K)
          </td>
        </tr>
        <tr id="ref-3">
          <td class="ref-id">3</td>
          <td>[Q# FY#### Diluted EPS]</td>
          <td class="num">$[X.XX]</td>
          <td class="source-detail">
            <span class="src-label">SEC EDGAR XBRL</span> — companyfacts CIK[0000000000],
            us-gaap:EarningsPerShareDiluted, frame=CY20XXQ[X], form=10-Q, accn=[…], filed [YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-4">
          <td class="ref-id">4</td>
          <td>[Q# FY#### Gross Profit]</td>
          <td class="num">$[XX.X]B</td>
          <td class="source-detail">
            <span class="src-label">SEC EDGAR XBRL</span> — companyfacts CIK[0000000000], us-gaap:GrossProfit,
            frame=CY20XXQ[X], form=10-Q, accn=[…], filed [YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-5">
          <td class="ref-id">5</td>
          <td>[Q# FY#### Gross Margin]</td>
          <td class="num">[XX.X%]</td>
          <td class="source-detail">
            <span class="formula"><a href="#ref-4" class="data-ref">Gross Profit $XX.XB</a> / <a href="#ref-1" class="data-ref">Revenue $XX.XB</a> = XX.X%</span><br>
            <span class="src-label">SEC EDGAR XBRL</span> (calculated)
          </td>
        </tr>
        <tr id="ref-6">
          <td class="ref-id">6</td>
          <td>[Q# FY#### Revenue y/y Growth]</td>
          <td class="num">[+/-X.X%]</td>
          <td class="source-detail">
            <span class="formula">(<a href="#ref-1" class="data-ref">[Q# FY## Rev $XX.XB]</a> - <a href="#ref-2" class="data-ref">[Q# FY## Rev $XX.XB]</a>) / <a href="#ref-2" class="data-ref">[Q# FY## Rev $XX.XB]</a> = X.X%</span><br>
            <span class="src-label">SEC EDGAR XBRL</span> (calculated)
          </td>
        </tr>
        <tr id="ref-7">
          <td class="ref-id">7</td>
          <td>Segment revenue — [segment name]</td>
          <td class="num">$[X,XXX]M</td>
          <td class="source-detail">
            <span class="src-label">SEC EDGAR XBRL</span> — companyfacts CIK[0000000000], us-gaap:[Tag],
            member=[segment axis member], frame=CY20XXQ[X]. <span class="excerpt">Or: segment footnote,
            Form 10-Q filed [YYYY-MM-DD], accn=[…]. Record which.</span>
          </td>
        </tr>
        <!-- Continue for all financial data points... -->

        <!-- Group: Estimates, Consensus & Revisions — the IBES-sourced core of the report.
             Every consensus figure carries an IBES tag; every peer figure carries a Yahoo tag. -->
        <tr><td colspan="4" class="appendix-group">Estimates, Consensus &amp; Revisions <span class="basis">IBES</span></td></tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Consensus EPS — [Q# FY####] <span class="basis">IBES</span></td>
          <td class="num">$[X.XX]</td>
          <td class="source-detail">
            <span class="src-label">Alpha Vantage EARNINGS_ESTIMATES</span> (IBES-sourced) —
            symbol=[TICKER], horizon="fiscal quarter", date=[YYYY-MM-DD],
            field=<code>eps_estimate_average</code>, analyst_count [N], retrieved [YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Consensus EPS range — [Q# FY####]</td>
          <td class="num">$[X.XX]–$[X.XX]</td>
          <td class="source-detail">
            <span class="src-label">Alpha Vantage EARNINGS_ESTIMATES</span> —
            fields <code>eps_estimate_low</code> / <code>eps_estimate_high</code>, date=[YYYY-MM-DD],
            retrieved [YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Estimate dispersion — [Q# FY####]</td>
          <td class="num">[XX.X%]</td>
          <td class="source-detail">
            <span class="formula">(<a href="#ref-N" class="data-ref">High $X.XX</a> - <a href="#ref-N" class="data-ref">Low $X.XX</a>) / <a href="#ref-N" class="data-ref">Mean $X.XX</a> = XX.X%</span><br>
            <span class="src-label">Alpha Vantage EARNINGS_ESTIMATES</span> (calculated)
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>EPS revision drift, 90 days — [Q# FY####]</td>
          <td class="num">[+/-X.X%]</td>
          <td class="source-detail">
            <span class="formula">(<a href="#ref-N" class="data-ref">avg 1.5300</a> - <a href="#ref-N" class="data-ref">avg_90_days_ago 1.4900</a>) / 1.4900 = +2.7%</span><br>
            <span class="src-label">Alpha Vantage EARNINGS_ESTIMATES</span> — fields
            <code>eps_estimate_average</code> / <code>eps_estimate_average_90_days_ago</code>, date=[YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Net revision breadth, 30 days — [Q# FY####]</td>
          <td class="num">[+/-N]</td>
          <td class="source-detail">
            <span class="formula">up [N] - down [N] = [+/-N]</span><br>
            <span class="src-label">Alpha Vantage EARNINGS_ESTIMATES</span> — fields
            <code>eps_estimate_revision_up_trailing_30_days</code> /
            <code>…_down_trailing_30_days</code>.
            <span class="excerpt">A <code>null</code> on either side is excluded, not read as zero.</span>
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Peer consensus basis</td>
          <td class="num">N/A</td>
          <td class="source-detail">
            <span class="excerpt">Peer NTM EPS comes from Yahoo Finance analyst estimates, not IBES.
            Alpha Vantage's 25 req/day free tier permits the subject company only. These are different
            contributor pools; peer NTM P/E is not strictly like-for-like with the subject's.</span>
          </td>
        </tr>

        <!-- Group: Surprise History -->
        <tr><td colspan="4" class="appendix-group">Surprise History</td></tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Surprise % — [Q# FY####]</td>
          <td class="num">[+/-X.X%]</td>
          <td class="source-detail">
            <span class="src-label">Alpha Vantage EARNINGS</span> — symbol=[TICKER],
            quarterlyEarnings[fiscalDateEnding=[YYYY-MM-DD]].surprisePercentage; reportedEPS [X.XX] vs
            estimatedEPS [X.XX], reportTime [pre/post-market], retrieved [YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Beat rate / mean surprise / σ — last [N] prints</td>
          <td class="num">[x of N] / [X.X%]</td>
          <td class="source-detail">
            <span class="formula">mean [+X.X%], trimmed mean [+X.X%] (largest absolute surprise excluded), sample σ [X.X%] over n=[N]</span><br>
            <span class="src-label">Alpha Vantage EARNINGS</span> (calculated). Quarters with no estimate are excluded and named in Manual Review.
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>The bar — mean surprise − 1σ</td>
          <td class="num">[+/-X.X%]</td>
          <td class="source-detail">
            <span class="formula"><a href="#ref-N" class="data-ref">mean +X.X%</a> - <a href="#ref-N" class="data-ref">σ X.X%</a> = [+/-X.X%]</span><br>
            <span class="src-label">Alpha Vantage EARNINGS</span> (calculated)
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>1-day post-print move — [Q# FY####]</td>
          <td class="num">[+/-X.X%]</td>
          <td class="source-detail">
            <span class="formula">(<a href="#ref-N" class="data-ref">next-session close $XX.XX</a> - <a href="#ref-N" class="data-ref">print-day close $XX.XX</a>) / print-day close</span><br>
            <span class="src-label">yfinance</span> EOD close (calculated)
          </td>
        </tr>

        <!-- Group: Valuation -->
        <tr><td colspan="4" class="appendix-group">Valuation</td></tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Current Stock Price — [TICKER]</td>
          <td class="num">$[XXX.XX]</td>
          <td class="source-detail">
            <span class="src-label">yfinance</span> — <code>Ticker("[TICKER]").history(period="1y").Close</code>,
            EOD, retrieved [YYYY-MM-DD]. <span class="excerpt">Not real-time.</span>
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Market Cap — [TICKER]</td>
          <td class="num">$[XXX.X]B</td>
          <td class="source-detail">
            <span class="src-label">yfinance</span> — <code>Ticker("[TICKER]").info["marketCap"]</code>,
            EOD-derived (price × shares), retrieved [YYYY-MM-DD]
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>LTM P/E — [TICKER]</td>
          <td class="num">[XX.X]x</td>
          <td class="source-detail">
            <span class="formula"><a href="#ref-N" class="data-ref">Price $XXX.XX</a> / (<a href="#ref-3" class="data-ref">[Q# FY## EPS $X.XX]</a> + <a href="#ref-3" class="data-ref">[Q# FY## EPS $X.XX]</a> + <a href="#ref-3" class="data-ref">[Q# FY## EPS $X.XX]</a> + <a href="#ref-3" class="data-ref">[Q# FY## EPS $X.XX]</a>) = XX.Xx</span><br>
            <span class="src-label">SEC EDGAR XBRL + yfinance</span> (calculated). Each company's own most
            recent 4 reported quarters — not a fixed calendar window.
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>NTM P/E — [TICKER] <span class="basis">IBES</span></td>
          <td class="num">[XX.X]x</td>
          <td class="source-detail">
            <span class="formula"><a href="#ref-N" class="data-ref">Price $XXX.XX</a> / (<a href="#ref-N" class="data-ref">[Q#]E $X.XX</a> + <a href="#ref-N" class="data-ref">[Q#]E $X.XX</a> + <a href="#ref-N" class="data-ref">[Q#]E $X.XX</a> + <a href="#ref-N" class="data-ref">[Q#]E $X.XX</a>) = XX.Xx</span><br>
            <span class="src-label">Alpha Vantage EARNINGS_ESTIMATES</span> (IBES-sourced) —
            symbol=[TICKER], horizon="fiscal quarter", nearest 4 forward periods, field
            <code>eps_estimate_average</code>, retrieved [YYYY-MM-DD].
            NTM EPS = sum of the next 4 quarterly consensus mean estimates, not a single annual figure.
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>NTM P/E — [PEER] <span class="basis">YAHOO</span></td>
          <td class="num">[XX.X]x</td>
          <td class="source-detail">
            <span class="formula"><a href="#ref-N" class="data-ref">Price $XXX.XX</a> / (<a href="#ref-N" class="data-ref">[4 forward quarterly estimates]</a>) = XX.Xx</span><br>
            <span class="src-label">yfinance</span> — <code>Ticker("[PEER]").earnings_estimate</code>.
            Yahoo Finance analyst estimates, <strong>not IBES</strong>, retrieved [YYYY-MM-DD].
          </td>
        </tr>

        <!-- Group: Transcript Claims — DELETE THIS WHOLE GROUP if no verbatim source exists.
             Never present a paraphrase as a quote. A press-release sentence is a quote from the
             press release, not from the call, and must be labelled as such. -->
        <tr><td colspan="4" class="appendix-group">Transcript &amp; Management Commentary</td></tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>[Fact, e.g., "Management guided comp sales +3-4%"]</td>
          <td class="num">N/A</td>
          <td class="source-detail">
            <span class="excerpt">"[exact verbatim sentence copied word for word from the source]"</span><br>
            <span class="src-label">Source:</span> <span class="transcript-ref">[Q# FY#### Earnings Call Transcript]</span>
            — <a href="[IR-hosted transcript URL]" target="_blank" class="src-url">[Company IR]</a>
            — [Speaker Name], [Title].
            <span class="excerpt">Or: Form 8-K Exhibit 99.1 press release,
            <a href="https://www.sec.gov/Archives/edgar/data/[cik]/[accession-no-dashes]/[doc]" target="_blank" class="src-url">[EDGAR filing]</a>
            (accn [number], filed [YYYY-MM-DD]) — a written document, not call commentary.</span>
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>Verbatim source availability</td>
          <td class="num">N/A</td>
          <td class="source-detail">
            <span class="excerpt">[IR transcript found | 8-K Ex-99.1 only | NONE].
            If NONE, this report contains no blockquotes — the argument is made from the numbers.</span>
          </td>
        </tr>

        <!-- Group: News & Events — every row carries a clickable filing-index or article URL. -->
        <tr><td colspan="4" class="appendix-group">News &amp; Events</td></tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>[e.g., "Form 8-K Item 2.02 — results of operations, filed 2026-08-20"]</td>
          <td class="num">N/A</td>
          <td class="source-detail">
            <span class="excerpt">"[key finding from the filing]"</span><br>
            <a href="https://www.sec.gov/Archives/edgar/data/[cik]/[accession-no-dashes]/" target="_blank" class="src-url">[Filer Name, Form 8-K, filed YYYY-MM-DD]</a><br>
            <span class="src-label">Query:</span> <code>efts.sec.gov/LATEST/search-index?q="[query]"&amp;forms=8-K&amp;ciks=[cik]</code>
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>[e.g., "Analyst action reported by Yahoo Finance"]</td>
          <td class="num">N/A</td>
          <td class="source-detail">
            <span class="excerpt">"[action as reported]"</span><br>
            <span class="src-label">yfinance</span> — <code>Ticker("[TICKER]").upgrades_downgrades</code>.
            Yahoo-derived panel, <strong>not IBES</strong>; no source document and not reliably
            timestamped. Unverifiable actions belong in Manual Review, not in the narrative.
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>[Sector / macro context]</td>
          <td class="num">N/A</td>
          <td class="source-detail">
            <span class="excerpt">"[finding]"</span><br>
            <span class="src-label">FRED</span> series <code>[ID]</code>,
            <code>fred.stlouisfed.org/graph/fredgraph.csv?id=[ID]</code>, retrieved [YYYY-MM-DD].
            <span class="excerpt">Or: peer 8-K guidance language from EDGAR full-text search.</span>
          </td>
        </tr>

        <!-- Group: Stock Performance -->
        <tr><td colspan="4" class="appendix-group">Stock Performance</td></tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>YTD Return — [TICKER]</td>
          <td class="num">[+/-X.X%]</td>
          <td class="source-detail">
            <span class="formula">(<a href="#ref-N" class="data-ref">Current $XXX.XX</a> - <a href="#ref-N" class="data-ref">Dec 31 Close $XXX.XX</a>) / <a href="#ref-N" class="data-ref">Dec 31 Close $XXX.XX</a> = X.X%</span><br>
            <span class="src-label">yfinance</span> EOD close (calculated). Common base date for
            <strong>all</strong> tickers: [YYYY-MM-DD].
          </td>
        </tr>
        <tr id="ref-N">
          <td class="ref-id">[N]</td>
          <td>1-Yr Return — [TICKER]</td>
          <td class="num">[+/-X.X%]</td>
          <td class="source-detail">
            <span class="formula">(<a href="#ref-N" class="data-ref">End $XXX.XX</a> - <a href="#ref-N" class="data-ref">Base $XXX.XX</a>) / <a href="#ref-N" class="data-ref">Base $XXX.XX</a> = X.X%</span><br>
            <span class="src-label">yfinance</span> EOD close (calculated), base date [YYYY-MM-DD]
          </td>
        </tr>
      </tbody>
    </table>

    <!-- ════════════════════════════════════════════ -->
    <!-- TABLE 2: MANUAL REVIEW — MANDATORY. Never omit.          -->
    <!-- One row per gap, exclusion, and unverifiable claim.      -->
    <!-- ════════════════════════════════════════════ -->
    <h3 class="subsection-title">Manual Review — items a human must resolve</h3>
    <table>
      <thead>
        <tr>
          <th style="width: 210px;">Item</th>
          <th style="width: 110px;">Status</th>
          <th>Blocker</th>
          <th style="width: 210px;">What a human must do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>[e.g., Q4 FY2024 segment revenue y/y]</td>
          <td><span class="neg">Not available</span></td>
          <td>Prior-year segment member absent from companyfacts; filer does not tag it</td>
          <td>Pull the segment footnote from the FY2024 10-K; do not estimate</td>
        </tr>
        <tr>
          <td>[e.g., Q2 FY2024 surprise %]</td>
          <td><span class="neg">Excluded</span></td>
          <td><code>estimatedEPS</code> absent for that quarter in Alpha Vantage EARNINGS</td>
          <td>Confirm against the original release; the quarter is out of every statistic</td>
        </tr>
        <tr>
          <td>[e.g., Q1 FY2027 net revision breadth 7d]</td>
          <td><span class="neg">Not available</span></td>
          <td>Field returned <code>null</code> — treated as not reported, never as zero</td>
          <td>None required; recorded so the reader knows breadth is absent, not neutral</td>
        </tr>
        <tr>
          <td>[e.g., Firm-level rating change, [Broker], [date]]</td>
          <td><span class="neg">Unverified</span></td>
          <td>Yahoo Finance analyst actions carry no source document</td>
          <td>Confirm with the broker note before this appears in any published research</td>
        </tr>
        <tr>
          <td>[e.g., Management Q&amp;A themes]</td>
          <td><span class="neg">Not available</span></td>
          <td>No IR transcript and no 8-K Ex-99.1 for [fiscal period]</td>
          <td>Obtain the call replay; report contains no blockquotes until then</td>
        </tr>
        <tr>
          <td>[e.g., Peer NTM consensus coverage]</td>
          <td><span class="neg">Depth limited</span></td>
          <td>Alpha Vantage free tier is 25 req/day — subject only; peers are Yahoo-sourced</td>
          <td>Label the basis (done); upgrade only with a paid IBES feed</td>
        </tr>
        <!-- Add one row per gap, exclusion, null and unverifiable claim found in any phase. -->
      </tbody>
    </table>
  </div>

  <!-- ════════════════════════════════════════════ -->
  <!-- FOOTER                                       -->
  <!-- ════════════════════════════════════════════ -->
  <div class="page-footer">
    <div class="footer-disclaimer">Analysis is AI-generated — please confirm all outputs</div>
    <div class="footer-meta">Data: Alpha Vantage EARNINGS_ESTIMATES / EARNINGS (IBES, subject only) · SEC EDGAR XBRL companyfacts · yfinance EOD close | [Month Day, Year] · <strong>EOD / delayed — not real-time</strong></div>
  </div>

</div>

<!-- ════════════════════════════════════════════════ -->
<!-- CHART.JS SCRIPTS                                 -->
<!-- ════════════════════════════════════════════════ -->
<script>
// ── Register Annotation Plugin ──
// The CDN-loaded annotation plugin must be explicitly registered.
// It is available as a global after the script tag loads.
if (window['chartjs-plugin-annotation']) {
  Chart.register(window['chartjs-plugin-annotation']);
}

// ── Chart Defaults ──
Chart.defaults.font.family = "'Arial Narrow', Arial, sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = '#555';
Chart.defaults.plugins.legend.position = 'bottom';
Chart.defaults.plugins.legend.labels.boxWidth = 12;

// ── Color Palette ──
const COLORS = {
  navy:     '#1a1a4e',
  blue:     '#3366cc',
  teal:     '#0d9488',
  orange:   '#e67e22',
  red:      '#c0392b',
  green:    '#27ae60',
  purple:   '#8e44ad',
  gray:     '#7f8c8d',
  lightBlue:'#85c1e9',
  gold:     '#f0b429',
};
const COMP_COLORS = [
  COLORS.navy, COLORS.blue, COLORS.teal,
  COLORS.orange, COLORS.red, COLORS.green,
  COLORS.purple, COLORS.gold
];

// ── Helper: Revenue & EPS Combo Chart ──
function createRevEpsChart(canvasId, labels, revenueData, epsData, revLabel) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: revLabel || 'Revenue ($B)',
          data: revenueData,
          backgroundColor: COLORS.navy + 'cc',
          borderColor: COLORS.navy,
          borderWidth: 1,
          yAxisID: 'y',
          order: 2
        },
        {
          label: 'Diluted EPS',
          data: epsData,
          type: 'line',
          borderColor: COLORS.orange,
          backgroundColor: COLORS.orange,
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: COLORS.orange,
          tension: 0.3,
          yAxisID: 'y1',
          order: 1
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      scales: {
        y: {
          position: 'left',
          title: { display: true, text: revLabel || 'Revenue ($B)', font: { size: 11 } },
          grid: { color: '#eee' }
        },
        y1: {
          position: 'right',
          title: { display: true, text: 'EPS ($)', font: { size: 11 } },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}

// ── Helper: Margin Trend Chart ──
function createMarginChart(canvasId, labels, grossMargins, opMargins) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Gross Margin %',
          data: grossMargins,
          borderColor: COLORS.blue,
          backgroundColor: COLORS.blue + '20',
          borderWidth: 2.5,
          pointRadius: 4,
          fill: false,
          tension: 0.3
        },
        {
          label: 'Operating Margin %',
          data: opMargins,
          borderColor: COLORS.teal,
          backgroundColor: COLORS.teal + '20',
          borderWidth: 2.5,
          pointRadius: 4,
          fill: false,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          title: { display: true, text: 'Margin (%)', font: { size: 11 } },
          grid: { color: '#eee' },
          ticks: { callback: v => v.toFixed(1) + '%' }
        }
      }
    }
  });
}

// ── Helper: Revenue Growth Bar Chart ──
function createRevGrowthChart(canvasId, labels, growthData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Revenue Growth y/y %',
        data: growthData,
        backgroundColor: growthData.map(v => v >= 0 ? COLORS.green + 'cc' : COLORS.red + 'cc'),
        borderColor: growthData.map(v => v >= 0 ? COLORS.green : COLORS.red),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          title: { display: true, text: 'Growth (%)', font: { size: 11 } },
          grid: { color: '#eee' },
          ticks: { callback: v => v.toFixed(1) + '%' }
        }
      },
      plugins: { legend: { display: false } }
    }
  });
}

// ── Helper: Earnings-Annotated Stock Price Chart ──
function createAnnotatedPriceChart(canvasId, labels, prices, earningsDates, ticker) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const annotations = {};
  earningsDates.forEach((ed, i) => {
    let xValue = ed.date;
    const isNeg = ed.move.startsWith('-');
    annotations['earnings' + i] = {
      type: 'line',
      xMin: xValue,
      xMax: xValue,
      borderColor: isNeg ? '#c0392b' : '#0d7a3e',
      borderWidth: 2,
      borderDash: [6, 4],
      label: {
        display: true,
        content: ed.label + ' (' + ed.move + ')',
        position: i % 2 === 0 ? 'start' : 'end',
        backgroundColor: isNeg ? '#c0392b' : '#0d7a3e',
        color: '#fff',
        font: { size: 10, weight: 'bold' },
        padding: { top: 3, bottom: 3, left: 6, right: 6 },
        borderRadius: 3
      }
    };
  });
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: ticker + ' Close',
        data: prices,
        borderColor: COLORS.navy,
        backgroundColor: COLORS.navy + '15',
        borderWidth: 1.5,
        pointRadius: 0,
        pointHitRadius: 4,
        fill: true,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { type: 'category', ticks: { maxTicksLimit: 12, font: { size: 10 } }, grid: { display: false } },
        y: { title: { display: true, text: 'Price ($)', font: { size: 11 } }, grid: { color: '#eee' } }
      },
      plugins: {
        annotation: { annotations: annotations },
        tooltip: { callbacks: { label: ctx => ticker + ': $' + ctx.raw.toFixed(2) } }
      }
    }
  });
}

// ── Helper: Competitor Indexed Performance Chart ──
// datasets: [{ label: 'TICKER', data: [price1, price2, ...], color: '#xxx', isSubject: true/false }, ...]
function createCompPerfChart(canvasId, labels, datasets) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const chartDatasets = datasets.map((ds, i) => {
    const base = ds.data[0] || 1;
    return {
      label: ds.label,
      data: ds.data.map(v => (v / base) * 100),
      borderColor: ds.color || COMP_COLORS[i % COMP_COLORS.length],
      backgroundColor: 'transparent',
      borderWidth: ds.isSubject ? 3 : 1.5,
      borderDash: ds.isSubject ? [] : [4, 2],
      pointRadius: 0,
      tension: 0.2
    };
  });
  new Chart(ctx, {
    type: 'line',
    data: { labels: labels, datasets: chartDatasets },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      scales: {
        y: { title: { display: true, text: 'Indexed (100 = Start)', font: { size: 11 } }, grid: { color: '#eee' } },
        x: { ticks: { maxTicksLimit: 12 } }
      },
      plugins: {
        tooltip: { callbacks: { label: ctx => ctx.dataset.label + ': ' + ctx.raw.toFixed(1) } }
      }
    }
  });
}

// ── Helper: LTM P/E Horizontal Bar Chart ──
// companies: [{ label: 'TICKER', pe: 25.3, isSubject: true/false }, ...]
function createPEChart(canvasId, companies) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  companies.sort((a, b) => b.pe - a.pe);
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: companies.map(c => c.label),
      datasets: [{
        label: 'LTM P/E',
        data: companies.map(c => c.pe),
        backgroundColor: companies.map(c => c.isSubject ? COLORS.navy : COLORS.lightBlue),
        borderColor: companies.map(c => c.isSubject ? COLORS.navy : COLORS.blue),
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      scales: {
        x: {
          title: { display: true, text: 'LTM P/E', font: { size: 11 } },
          grid: { color: '#eee' }
        },
        y: {
          ticks: { font: { size: 12, weight: 'bold' } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => 'P/E: ' + ctx.raw.toFixed(1) + 'x' }
        }
      }
    }
  });
}

// ── Helper: Estimate Revisions (Figure 9) ──
// driftPct: 90-day EPS estimate drift, in percent, per near-term quarter
// breadth:   net 30-day revision breadth (up - down), same quarters, same order
// Pass only quarters where BOTH series have usable (non-null) data. A null is
// excluded by the caller, never coerced to 0 — a zero breadth claim is a claim.
function createRevisionChart(canvasId, labels, driftPct, breadth) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    data: {
      labels: labels,
      datasets: [
        {
          type: 'bar',
          label: 'EPS Revision Drift, 90d %',
          data: driftPct,
          backgroundColor: driftPct.map(v => v >= 0 ? COLORS.green + 'cc' : COLORS.red + 'cc'),
          borderColor: driftPct.map(v => v >= 0 ? COLORS.green : COLORS.red),
          borderWidth: 1,
          yAxisID: 'y',
          order: 2
        },
        {
          type: 'line',
          label: 'Net Revision Breadth, 30d (up − down)',
          data: breadth,
          borderColor: COLORS.navy,
          backgroundColor: COLORS.navy,
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: COLORS.navy,
          tension: 0.3,
          yAxisID: 'y1',
          order: 1
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      scales: {
        y: {
          position: 'left',
          title: { display: true, text: 'Drift (%)', font: { size: 11 } },
          grid: { color: '#eee' },
          ticks: { callback: v => v.toFixed(1) + '%' }
        },
        y1: {
          position: 'right',
          title: { display: true, text: 'Net breadth (analysts)', font: { size: 11 } },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}

// ═══════════════════════════════════════════════
// HELPER FUNCTIONS DEFINED ABOVE — DO NOT REWRITE THEM.
// Use ONLY these functions to create charts.
// DO NOT write custom inline Chart.js code.
// ═══════════════════════════════════════════════

</script>

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- CHART DATA — EACH CHART IN ITS OWN SCRIPT + TRY-CATCH     -->
<!-- A syntax error in one chart must NOT break the others.     -->
<!-- MANDATORY: Use the helper functions above. No custom code. -->
<!-- ═══════════════════════════════════════════════════════════ -->

<!-- Figure 1: Revenue & EPS -->
<script>
try {
  createRevEpsChart('chart-rev-eps',
    ['Q1 FY24','Q2 FY24','Q3 FY24','Q4 FY24','Q1 FY25','Q2 FY25','Q3 FY25','Q4 FY25'],
    [152.3, 161.6, 160.8, 173.4, 161.5, 169.3, 165.8, 178.0],  // revenue in $B
    [1.47, 1.84, 1.53, 1.80, 1.56, 1.92, 1.60, 1.90],          // diluted EPS
    'Revenue ($B)'
  );
} catch(e) { console.error('Figure 1 error:', e); }
</script>

<!-- Figure 2: Margin Trends -->
<script>
try {
  createMarginChart('chart-margins',
    ['Q1 FY24','Q2 FY24','Q3 FY24','Q4 FY24','Q1 FY25','Q2 FY25','Q3 FY25','Q4 FY25'],
    [24.0, 24.4, 24.2, 23.8, 24.5, 24.8, 24.6, 24.1],  // gross margin %
    [4.2, 5.1, 4.5, 4.8, 4.6, 5.3, 4.7, 5.0]            // operating margin %
  );
} catch(e) { console.error('Figure 2 error:', e); }
</script>

<!-- Figure 3: Revenue Growth y/y — ONLY quarters where y/y can be computed (most recent 4) -->
<script>
try {
  createRevGrowthChart('chart-rev-growth',
    ['Q1 FY25','Q2 FY25','Q3 FY25','Q4 FY25'],  // Only 4 labels — quarters with y/y data
    [6.0, 4.8, 3.1, 2.7]                          // y/y revenue growth % for those 4 quarters
  );
} catch(e) { console.error('Figure 3 error:', e); }
</script>

<!-- Figure 5: Annotated Stock Price -->
<script>
try {
  createAnnotatedPriceChart('chart-price-annotated',
    ['2025-02-18','2025-02-19'],  // ... daily date labels for 1 year
    [170.5, 171.2],               // ... daily closing prices
    [
      { date: '2025-05-15', label: 'Q1 FY26', move: '+3.2%' },
      { date: '2025-08-15', label: 'Q2 FY26', move: '-1.8%' }
    ],
    'WMT'
  );
} catch(e) { console.error('Figure 5 error:', e); }
</script>

<!-- Figure 6: Competitor Indexed Performance -->
<script>
try {
  createCompPerfChart('chart-comp-perf',
    ['2025-02-18','2025-03-18'],  // ... date labels
    [
      { label: 'WMT', data: [170.5, 172.3], isSubject: true },
      { label: 'COST', data: [580.2, 595.1], isSubject: false },
      { label: 'TGT', data: [142.0, 138.5], isSubject: false }
    ]
  );
} catch(e) { console.error('Figure 6 error:', e); }
</script>

<!-- Figure 7: LTM P/E Comparison -->
<script>
try {
  createPEChart('chart-pe-comp', [
    { label: 'COST', pe: 52.3, isSubject: false },
    { label: 'WMT', pe: 28.1, isSubject: true },
    { label: 'TGT', pe: 15.6, isSubject: false },
    { label: 'BJ', pe: 22.4, isSubject: false }
  ]);
} catch(e) { console.error('Figure 7 error:', e); }
</script>

<!-- Figure 9: Estimate Revisions — near-term quarters only, both series non-null.
     DELETE this script and its <canvas> if fewer than two quarters qualify. -->
<script>
try {
  createRevisionChart('chart-revisions',
    ['Q4 FY26','Q1 FY27','Q2 FY27'],   // near-term fiscal quarters only
    [2.7, 1.9, 0.8],                    // 90-day EPS estimate drift, %
    [7, 4, 2]                           // net 30-day revision breadth (up - down)
  );
} catch(e) { console.error('Figure 9 error:', e); }
</script>

</body>
</html>
```

## Chart.js Implementation Notes

### Figure 2: Revenue & EPS Chart
- **Type**: Combo bar + line
- **Bars**: Quarterly revenue on left y-axis
- **Line**: Diluted EPS on right y-axis
- **Labels**: Quarter identifiers (e.g., "Q1 FY24")
- Use 8 quarters of data

### Figure 3: Margin Trend Chart
- **Type**: Dual line chart
- **Lines**: Gross margin % and operating margin %
- **Y-axis**: Percentage with 1 decimal place

### Figure 3: Revenue Growth Chart
- **Type**: Bar chart with conditional coloring
- **Green bars**: Positive growth quarters
- **Red bars**: Negative growth quarters
- **IMPORTANT**: Only include quarters where y/y growth can be computed (i.e., where both the current quarter AND the year-ago quarter exist in `financials.csv`). With 8 quarters of raw data, this typically yields 4 bars — NOT 8. Do not pass labels for quarters without y/y data.
- No legend needed (self-explanatory)

### Figure 4: Business Segment Revenue
- Use HTML table (not a chart)
- Columns: Segment | Latest Q Rev ($M) | % of Total | y/y Change
- Color-code y/y change cells with pos/neg classes

### Figure 5: Earnings-Annotated Stock Price Chart
- **Type**: Line chart with annotation plugin vertical lines
- **Data**: 1 year of daily closing prices
- **Annotations**: Vertical dashed lines at each earnings date
- **Labels**: Quarter name + 1-day post-earnings stock move
- **Colors**: Green for positive reactions, red for negative
- **Calculating the 1-day move**: Compare closing price on earnings date to next trading day close
- **CRITICAL**: The annotation plugin MUST be registered before creating charts: `Chart.register(window['chartjs-plugin-annotation'])` — this is already in the template script block

### Figure 7: Competitor Indexed Performance Chart
- **Type**: Multi-line chart, rebased to 100
- **Subject company**: Solid thick line (borderWidth: 3)
- **Competitors**: Thinner dashed lines (borderWidth: 1.5, borderDash)
- This visual hierarchy makes the subject company immediately identifiable

### Figure 8: LTM P/E Comparison Chart
- **Type**: Horizontal bar chart
- **Subject company**: Highlighted in navy (#1a1a4e)
- **Competitors**: Light blue (#85c1e9)
- **Sorted**: Descending by P/E
- Shows at a glance whether the company trades at a premium or discount to peers

### Figure 9: Estimate Revisions Chart
- **Type**: Dual-axis — 90-day EPS estimate drift as bars (left axis, %), net 30-day revision breadth as a line (right axis, count of analysts)
- **Bars**: Green for positive drift, red for negative — mechanical, never interpretive
- **Quarters**: near-term only. On far-dated quarters the 7/30-day-ago averages equal the current average because the panel has not formed, so drift is structurally zero and says nothing about the Street's view
- **Nulls are excluded, never zero-filled.** A `null` revision count means "not reported", and charting it as 0 fabricates neutral breadth
- **Delete the figure entirely** if fewer than two quarters have usable data in both series. A two-bar chart of real data beats a six-bar chart with four invented points
- **No revenue revision series exists** — `revenue_estimate_*` carries no 7/30/60/90-day history. Do not construct one

## Formatting Conventions

### Numbers
- Revenue: 1 decimal place for $B (e.g., "$152.3B"), no decimals for $M (e.g., "$4,521M")
- EPS: 2 decimal places (e.g., "$1.47")
- Margins: 1 decimal place with % sign (e.g., "24.5%")
- Growth rates, revision drift, surprise %: 1 decimal place with +/- sign (e.g., "+5.2%", "-3.1%")
- Estimate dispersion: 1 decimal place (e.g., "8.4%")
- Net revision breadth: signed integer (e.g., "+7")
- Market cap: 1 decimal place for $B (e.g., "$562.1B")
- Stock prices: 2 decimal places (e.g., "$172.35")
- P/E ratios: 1 decimal place with 'x' suffix (e.g., "25.3x")

### Color Coding
- Positive values: `class="pos"` -- green (#0d7a3e)
- Negative values: `class="neg"` -- red (#c0392b)
- Neutral/flat/unavailable: `class="neutral"` -- gray (#555)
- Subject company row: `class="highlight-row"` -- light blue background
- Consensus basis tag: `<span class="basis">IBES</span>` or `<span class="basis">YAHOO</span>`
- Color follows the **sign**, never the interpretation. A −1.1% is always red, however small

### Figure Labels
- Number all figures sequentially: "Figure 1:", "Figure 2:", etc.
- Figures A and B (Consensus & Revisions, Surprise History) sit on Page 2 and are lettered, not numbered; Figures 1–9 sit on Pages 3–5
- **Include source attribution under every chart and table**, naming the actual endpoint — not a generic vendor label

## Data-Sourcing Rules (free stack)

These are the source strings the report is allowed to print. Anything else is a defect.

| Figure / table | Required source attribution |
|---|---|
| Figures A, 9 | Alpha Vantage `EARNINGS_ESTIMATES` (IBES-sourced), retrieved [date] |
| Figure B | Alpha Vantage `EARNINGS`; 1-day moves from yfinance EOD closes |
| Figures 1, 2, 3 | SEC EDGAR XBRL `companyfacts`, CIK [CIK], retrieved [date] |
| Figure 4 | XBRL segment members or the 10-Q/10-K segment footnote — name which. **Delete the figure if unavailable** |
| Figures 5, 6, 7 | yfinance `history(period="1y").Close` — EOD, not real-time |
| Figure 7 | SEC EDGAR XBRL EPS (subject) / company filings or yfinance (peers) |
| Figure 8 | yfinance market cap and EOD closes; Alpha Vantage `EARNINGS_ESTIMATES` (subject NTM, IBES); yfinance `earnings_estimate` (peer NTM, **Yahoo, not IBES**) |
| News & Events | EDGAR full-text search `efts.sec.gov/LATEST/search-index?q=…&forms=8-K&ciks=…` + clickable `sec.gov/Archives/edgar/data/…` filing-index URL |
| Analyst actions | yfinance `upgrades_downgrades` / `analyst_price_targets` — labelled "Yahoo Finance analyst estimates", never "the Street" |
| Macro / sector | FRED keyless CSV with the series id (`fred.stlouisfed.org/graph/fredgraph.csv?id=[ID]`) or peer 8-K language |

### Honesty rules that apply to the rendered report

- **Never fabricate an estimate or an actual.** If a figure is unavailable, write
  `not available — [blocker]` and add a Manual Review row. Do not fill the hole.
- **Consensus basis travels with the number.** IBES (Alpha Vantage, subject) and Yahoo Finance
  (peers) are different products. Tag every consensus figure. Never put them in one unlabelled column.
- **Everything is EOD or delayed.** The header provenance line and the footer both say so. No figure,
  price, or estimate may be described as real-time or intraday.
- **Alpha Vantage's free tier is 25 requests/day — subject company only.** Peer consensus is
  Yahoo-sourced; say so wherever a peer multiple appears.
- **No verbatim source, no blockquote.** Without an IR transcript or an 8-K Exhibit 99.1, the report
  contains no `<blockquote>` elements at all. Never present a paraphrase as a quote.
- **`null` is not zero.** An absent revision count or an absent estimate is an absence, excluded from
  every statistic and named in Manual Review — not a neutral value.
- **A `not available` in the report is a feature.** The Manual Review table is the deliverable's
  honesty floor.

### Appendix

- **MUST begin with**: `<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`
  followed by the provenance line (consensus basis, CIK, retrieval date, EOD caveat, AV quota).
- **Table 1 — Sources & Calculations.** Columns: Ref # | Fact | Value | Source & Derivation. One row
  per unique claim, `id="ref-N"`, grouped under `appendix-group` subheadings: Quarterly Financials ·
  Estimates, Consensus & Revisions · Surprise History · Valuation · Transcript & Management
  Commentary · News & Events · Stock Performance.
- **Table 2 — Manual Review.** Columns: Item | Status | Blocker | What a human must do. **Mandatory and
  never omitted.** One row per gap, exclusion, null and unverifiable claim found in any phase.
- Every raw-data row cites the endpoint with its identifying detail — EDGAR tag + frame + form +
  accession + filing date; AV function + symbol + horizon + period + field + retrieval date; yfinance
  attribute. **A bare label like "SEC EDGAR" with no tag and no accession is a defect.**
- Every calculated row shows the full formula with **each component hyperlinked** to its own appendix
  row, so the reader can click from the result back to each input.
- Every news/event row carries a clickable `sec.gov/Archives/edgar/data/…` filing-index URL.
- Delete the Transcript group entirely when no verbatim source exists.
- Use 10–11px.

### Style Rules
- **NO EMOJIS** anywhere in the report. No emoji in headings, tables, chart labels, or body text. This is a professional research document.
- Font: Arial Narrow throughout (body, headings, tables, charts).
- Management quotes: integrate as `<blockquote>` elements within the executive thesis narrative. Never under a separate heading. Only if a verbatim source exists.
- Keep all text concise. Target 4-5 printed pages total (appendix is additional).
