# SMB Growth Metrics Dashboard

Marketing campaign ROI analysis with consulting-style deliverables.

---

## 🚀 Run the Dashboard (One Command)

```bash
cd smb-growth-metrics-dashboard
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Then open **http://localhost:8505** in your browser.


---

## 📁 What's Inside

| Folder | What It Does |
|--------|--------------|
| `dashboard/` | Interactive web dashboard |
| `analysis/` | Jupyter notebooks + SQL queries |
| `deliverables/` | PDF reports (executive summary, recommendations, slides) |
| `data/raw/` | Put your Kaggle CSV here |
| `docs/` | How I built this (methodology) |

---

## 📊 Generate PDF Reports

```bash
cd analysis
python generate_deliverables.py
```

Creates 3 consulting-style PDFs in `/deliverables`:
- **Executive Summary** (1 page) - For busy executives
- **Recommendations** (2-4 pages) - Detailed strategy
- **Presentation** (8-12 slides) - Ready for meetings

---

## 🔑 Key Insights

Based on 200K+ marketing campaigns:

1. **Influencer campaigns** have the highest ROI
2. **25% of campaigns** are "vanity metrics" (high clicks, low profit)
3. **Facebook** is the top-performing channel
4. Reallocating 15% budget from worst → best performers could improve ROI by 10-15%

---

## 🛠 Tech Stack

Python, pandas, DuckDB (SQL), matplotlib, Streamlit, ReportLab (PDFs)
