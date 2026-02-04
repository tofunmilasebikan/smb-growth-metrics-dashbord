# Methodology

## My Approach, Decisions & Assumptions

---

## 1. Problem Statement

Small and medium-sized businesses (SMBs) often lack visibility into which marketing campaigns deliver the best return on investment. This project analyzes marketing campaign performance data to:

1. Identify high-performing campaign types, channels, and audience segments
2. Uncover "vanity metric" traps (high engagement, low returns)
3. Provide actionable budget reallocation recommendations
4. Deliver insights in a consulting-style format suitable for executive decision-making

---

## 2. KPI Definitions

| Metric | Definition | Formula |
|--------|------------|---------|
| **Impressions** | Number of times the ad was displayed | Raw count from data |
| **Clicks** | Number of times users clicked the ad | Raw count from data |
| **CTR** | Click-Through Rate - engagement measure | `clicks / impressions` |
| **Conversion Rate** | Percentage of clicks that convert | `conversions / clicks` OR direct from data |
| **Conversions (Est.)** | Estimated number of conversions | `conversion_rate × clicks` |
| **ROI** | Return on Investment | Direct from data (assumed: `(revenue - cost) / cost × 100`) |
| **Acquisition Cost** | Cost per campaign | Direct from data |
| **Engagement Score** | Qualitative engagement metric (1-10) | Direct from data |

### Traffic Light Indicators

- **Green**: Performance > 10% above average
- **Yellow**: Performance within ±10% of average
- **Red**: Performance > 10% below average

---

## 3. Data Cleaning Rules

### 3.1 Column Standardization
- All column names converted to `snake_case` for consistency
- Example: `Campaign_Type` → `campaign_type`

### 3.2 Data Type Handling
- **Dates**: Parsed to datetime format
- **Currency fields**: Stripped of `$` and `,` symbols, converted to float
- **Numeric fields**: Validated as numeric types

### 3.3 Missing Value Treatment

| Column Type | Rule |
|-------------|------|
| Impressions, Clicks | Drop row if missing (critical metrics) |
| Categorical fields | Fill with "Unknown" |
| ROI, Conversion Rate | Keep as-is (analysis adapts) |

### 3.4 Derived Metrics
- **CTR**: Calculated as `clicks / impressions` with zero-division guard
- **Conversions (Est.)**: If `conversions` column missing but `conversion_rate` exists: `round(conversion_rate × clicks)`

### 3.5 Data Quality Validations
- ✅ Clicks ≤ Impressions (sanity check)
- ✅ CTR range: 0-1 (or 0-100 if percentage)
- ✅ No negative values in count fields

---

## 4. Assumptions & Limitations

### Assumptions

1. **ROI Calculation**: Assumed the dataset's ROI is pre-calculated as `(revenue - cost) / cost × 100`. We use it directly.

2. **Acquisition Cost as Spend Proxy**: Used `acquisition_cost` as a proxy for campaign spend when simulating budget reallocation.

3. **Conversion Attribution**: Assumed conversions are directly attributed to campaigns (no multi-touch attribution complexity).

4. **Time Independence**: Each campaign is treated as independent; no carry-over effects modeled.

5. **Data Completeness**: Assumed the dataset represents a complete picture of campaign performance for the time period covered.

### Limitations

1. **No Revenue Data**: Without explicit revenue, we rely on ROI as provided. Cannot decompose ROI into its components.

2. **No Customer Lifetime Value (LTV)**: ROI shown is immediate; long-term customer value not captured.

3. **No A/B Test Structure**: Cannot determine if performance differences are statistically significant.

4. **Synthetic/Kaggle Data**: Patterns may not reflect real-world marketing dynamics.

5. **No Seasonality Adjustment**: Monthly trends shown but not seasonally adjusted.

---

## 5. Technical Implementation

### 5.1 Why DuckDB over SQLite

| Criteria | DuckDB | SQLite |
|----------|--------|--------|
| CSV reading | Native `read_csv_auto()` | Requires import |
| Window functions | Full SQL:2016 support | Limited support |
| Analytics workloads | Optimized (columnar) | Row-based |
| Aggregation speed | Faster on large data | Slower |
| Python integration | Seamless | Good |

**Decision**: DuckDB for its analytics-first design and zero-config CSV handling.

### 5.2 Python + SQL Integration

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Raw CSV Data    │───▶│  Python (pandas) │───▶│  Cleaned CSV     │
│  data/raw/       │    │  EDA + Cleaning  │    │  analysis/       │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                                                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Insights        │◀───│  Python + DuckDB │◀───│  SQL Queries     │
│  Dashboard       │    │  Analysis        │    │  roi_analysis.sql│
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

**Workflow**:
1. **Python (pandas)**: Data loading, cleaning, validation, initial EDA
2. **SQL (DuckDB)**: Complex aggregations, window functions, segmentation analysis
3. **Python (matplotlib)**: Visualization and chart generation
4. **Streamlit**: Interactive dashboard
5. **Python (reportlab)**: PDF report generation

### 5.3 Analysis Framework

The analysis follows a consulting-style structure:

1. **What happened?** - Descriptive statistics and KPI summary
2. **Why?** - Segmentation analysis to identify drivers
3. **So what?** - Business implications of findings
4. **What to do next?** - Prioritized recommendations

---

## 6. Recommendation Derivation

### 6.1 Identification Process

1. **Segment Analysis**: Calculated average ROI across all segmentation dimensions (campaign type, audience, channel, location, customer segment)

2. **Performance Ranking**: Ranked segments by ROI within each dimension

3. **Anomaly Detection**: Identified "vanity metrics" (high CTR, low ROI) and "hidden gems" (low CTR, high ROI)

4. **Budget Simulation**: Modeled 15% budget shift from worst to best performers

### 6.2 Prioritization Framework

Recommendations prioritized using:

| Priority | Criteria |
|----------|----------|
| **Now** | High impact, low effort, clear evidence |
| **Next** | High impact, medium effort |
| **Later** | Requires more data or testing |

### 6.3 Confidence Levels

- **High Confidence**: Consistent patterns across multiple segments, large sample size
- **Medium Confidence**: Clear pattern but limited sample or single dimension
- **Explore Further**: Interesting signal but needs validation

---

## 7. Future Enhancements

With additional data, the analysis could be extended to include:

### 7.1 Additional Data Points Needed

| Data Point | Analysis Enabled |
|------------|------------------|
| **Actual spend per campaign** | True ROI calculation, budget optimization |
| **Customer Acquisition Cost (CAC)** | Unit economics analysis |
| **Customer Lifetime Value (LTV)** | Long-term ROI, LTV:CAC ratio |
| **Channel attribution** | Multi-touch attribution modeling |
| **Creative/copy variants** | A/B test analysis |
| **Competitive benchmarks** | Market positioning |

### 7.2 Advanced Analytics

1. **Statistical Significance Testing**: Determine if segment differences are significant
2. **Predictive Modeling**: Forecast campaign performance
3. **Marketing Mix Modeling**: Optimize budget allocation across channels
4. **Cohort Analysis**: Track customer behavior over time
5. **Attribution Modeling**: Understand the customer journey

### 7.3 Dashboard Enhancements

1. Real-time data integration
2. Automated alerting for underperforming campaigns
3. Scenario planning tools
4. Export to common BI platforms

---

## 8. Reproducibility

This analysis is fully reproducible:

1. **Data**: Place Kaggle CSV in `data/raw/`
2. **Environment**: `pip install -r requirements.txt`
3. **Run EDA**: `jupyter notebook analysis/exploratory.ipynb`
4. **Run SQL**: `duckdb < analysis/roi_analysis.sql`
5. **View Insights**: `jupyter notebook analysis/insights.ipynb`
6. **Launch Dashboard**: `streamlit run dashboard/app.py`
7. **Generate PDFs**: `python analysis/generate_deliverables.py`

All notebooks run end-to-end without manual intervention.

---

*Document Version: 1.0*  
*Last Updated: January 2026*
