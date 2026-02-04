# Marketing ROI Dashboard

Executive-friendly Streamlit dashboard for marketing campaign analysis.

## Quick Start

```bash
# From project root
streamlit run dashboard/app.py
```

Opens at: http://localhost:8503

## Features

| Feature | Description |
|---------|-------------|
| **KPI Cards** | Campaigns, Impressions, Clicks, CTR, ROI, Conversion Rate |
| **Health Indicators** | Green/Yellow/Red based on data quartiles |
| **ROI Analysis** | By channel and campaign type (color-coded) |
| **Vanity Metrics** | Scatter plot showing high-CTR, low-ROI campaigns |
| **Actionable Insights** | Plain-English recommendations |
| **Filters** | Date, Channel, Type, Audience, Location, Segment |

## How to Read the Dashboard

1. **Health Check (🚦):** Start here. Red = needs attention.
2. **ROI Charts:** Green bars outperform, red bars underperform.
3. **Scatter Plot:** Red dots are "vanity" campaigns (high clicks, low profit).
4. **Insights:** Each one tells you what's happening and what to do.

## Metric Definitions

| Metric | Formula | Note |
|--------|---------|------|
| CTR | clicks ÷ impressions | Higher isn't always better |
| ROI | (revenue - cost) ÷ cost | Weighted by impressions |
| Conversion Rate | conversions ÷ clicks | Measures click quality |

## Requirements

```
pip install streamlit pandas numpy matplotlib
```
