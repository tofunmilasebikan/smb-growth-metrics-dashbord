"""
SMB Growth Metrics Dashboard
============================
Executive-friendly marketing ROI analysis dashboard.

Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Marketing ROI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - Fixed for dark theme visibility
# =============================================================================
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* KPI Card */
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.4rem;
    }
    .kpi-note {
        font-size: 0.7rem;
        color: #64748b;
        margin-top: 0.2rem;
    }
    
    /* Health indicator cards */
    .health-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .health-metric {
        font-weight: 600;
        color: #e2e8f0;
        font-size: 0.95rem;
    }
    .health-badge {
        font-size: 0.85rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 500;
    }
    .badge-green { background: #166534; color: #bbf7d0; }
    .badge-yellow { background: #854d0e; color: #fef08a; }
    .badge-red { background: #991b1b; color: #fecaca; }
    
    /* Insight boxes - FIXED for visibility */
    .insight-box {
        background: #0f172a;
        border: 1px solid #1e40af;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        border-radius: 0 8px 8px 0;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .insight-box b {
        color: #60a5fa;
    }
    .insight-action {
        color: #fbbf24;
        font-weight: 600;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #f1f5f9;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data(ttl=3600)
def load_data():
    """Load and prepare campaign data."""
    paths = [
        Path('../analysis/cleaned_campaigns.csv'),
        Path('analysis/cleaned_campaigns.csv'),
        Path('./cleaned_campaigns.csv'),
    ]
    
    for path in paths:
        if path.exists():
            df = pd.read_csv(path)
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            # Ensure CTR is calculated correctly
            if 'ctr' not in df.columns or df['ctr'].isna().all():
                df['ctr'] = np.where(df['impressions'] > 0, 
                                     df['clicks'] / df['impressions'], 0)
            
            # Estimate conversions if not present
            if 'conversions' not in df.columns and 'conversion_rate' in df.columns:
                df['conversions'] = (df['conversion_rate'] * df['clicks']).round().astype(int)
            
            return df
    
    st.error("Data file not found. Run the exploratory notebook first.")
    st.stop()


@st.cache_data
def calculate_quantiles(df):
    """Calculate quantile thresholds for health indicators."""
    return {
        'roi': {'p25': df['roi'].quantile(0.25), 'p75': df['roi'].quantile(0.75)},
        'ctr': {'p25': df['ctr'].quantile(0.25), 'p75': df['ctr'].quantile(0.75)},
        'conversion_rate': {'p25': df['conversion_rate'].quantile(0.25), 'p75': df['conversion_rate'].quantile(0.75)}
    }


def get_health_status(value, thresholds):
    """Determine health status based on quantile thresholds."""
    if value >= thresholds['p75']:
        return '🟢', 'Strong', 'badge-green', 'Top 25%'
    elif value <= thresholds['p25']:
        return '🔴', 'Weak', 'badge-red', 'Bottom 25%'
    else:
        return '🟡', 'Average', 'badge-yellow', 'Middle 50%'


def format_number(num, style='default'):
    """Format numbers for display."""
    if style == 'billions':
        if num >= 1e9:
            return f"{num/1e9:.2f}B"
        elif num >= 1e6:
            return f"{num/1e6:.1f}M"
        elif num >= 1e3:
            return f"{num/1e3:.0f}K"
        return f"{num:,.0f}"
    elif style == 'thousands':
        return f"{num:,.0f}"
    elif style == 'percent':
        return f"{num:.2f}%"
    elif style == 'decimal':
        return f"{num:.2f}"
    return f"{num:,.0f}"


def generate_insights(df, filtered_df, quantiles):
    """Generate plain-English actionable insights."""
    insights = []
    
    if len(filtered_df) == 0:
        return ["No data available for the selected filters."]
    
    avg_roi = filtered_df['roi'].mean()
    
    # 1. Best vs Worst Campaign Type
    if 'campaign_type' in filtered_df.columns:
        type_roi = filtered_df.groupby('campaign_type')['roi'].mean().sort_values(ascending=False)
        if len(type_roi) >= 2:
            best_type = type_roi.index[0]
            worst_type = type_roi.index[-1]
            roi_diff = ((type_roi.iloc[0] - type_roi.iloc[-1]) / type_roi.iloc[-1] * 100)
            if abs(roi_diff) > 1:
                insights.append(
                    f"<b>{best_type}</b> campaigns have <b>{abs(roi_diff):.0f}% higher ROI</b> than {worst_type}. "
                    f"<span class='insight-action'>Action: Shift 10-15% of {worst_type} budget to {best_type}.</span>"
                )
    
    # 2. Best Channel
    if 'channel_used' in filtered_df.columns:
        channel_roi = filtered_df.groupby('channel_used')['roi'].mean().sort_values(ascending=False)
        if len(channel_roi) >= 1:
            best_channel = channel_roi.index[0]
            best_channel_roi = channel_roi.iloc[0]
            pct_above = ((best_channel_roi - avg_roi) / avg_roi * 100)
            if pct_above > 0.5:
                insights.append(
                    f"<b>{best_channel}</b> delivers <b>{pct_above:.0f}% above-average ROI</b> ({best_channel_roi:.2f} vs {avg_roi:.2f}). "
                    f"<span class='insight-action'>Action: Prioritize this channel for new campaigns.</span>"
                )
    
    # 3. Vanity Metrics Warning
    high_ctr_low_roi = filtered_df[
        (filtered_df['ctr'] > filtered_df['ctr'].quantile(0.75)) & 
        (filtered_df['roi'] < filtered_df['roi'].quantile(0.25))
    ]
    vanity_pct = len(high_ctr_low_roi) / len(filtered_df) * 100
    if vanity_pct > 3:
        insights.append(
            f"<b>Vanity Metric Alert:</b> {vanity_pct:.0f}% of campaigns have high clicks but low ROI. "
            f"<span class='insight-action'>Action: Review targeting—clicks aren't converting to revenue.</span>"
        )
    
    # 4. Best Audience
    if 'target_audience' in filtered_df.columns:
        audience_roi = filtered_df.groupby('target_audience')['roi'].mean().sort_values(ascending=False)
        if len(audience_roi) >= 1:
            best_audience = audience_roi.index[0]
            best_audience_roi = audience_roi.iloc[0]
            if best_audience_roi > avg_roi * 1.02:
                insights.append(
                    f"<b>{best_audience}</b> is your top audience (ROI: {best_audience_roi:.2f}). "
                    f"<span class='insight-action'>Action: Create more content for this demographic.</span>"
                )
    
    # 5. Budget efficiency
    if 'acquisition_cost' in filtered_df.columns:
        high_cost_low_roi = filtered_df[
            (filtered_df['acquisition_cost'] > filtered_df['acquisition_cost'].quantile(0.75)) &
            (filtered_df['roi'] < filtered_df['roi'].quantile(0.5))
        ]
        waste_pct = len(high_cost_low_roi) / len(filtered_df) * 100
        if waste_pct > 10:
            insights.append(
                f"<b>{waste_pct:.0f}% of campaigns</b> have high cost but below-average ROI. "
                f"<span class='insight-action'>Action: Audit these for budget reallocation.</span>"
            )
    
    if not insights:
        insights.append("All metrics are performing within normal ranges. Continue monitoring weekly.")
    
    return insights


# =============================================================================
# MAIN APP
# =============================================================================
def main():
    df = load_data()
    quantiles = calculate_quantiles(df)
    
    # =========================================================================
    # HEADER (no emoji icon)
    # =========================================================================
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <h1 style="font-size: 2rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.3rem;">
            Marketing ROI Dashboard
        </h1>
        <p style="color: #94a3b8; font-size: 0.95rem;">
            Campaign performance insights for executive decision-making
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # FILTERS
    # =========================================================================
    with st.expander("🔍 Filters (click to expand)", expanded=False):
        filter_cols = st.columns(6)
        
        with filter_cols[0]:
            if 'date' in df.columns:
                min_date = df['date'].min().date()
                max_date = df['date'].max().date()
                date_range = st.date_input("Date Range", value=(min_date, max_date))
            else:
                date_range = None
        
        with filter_cols[1]:
            campaign_types = ['All'] + sorted(df['campaign_type'].unique().tolist()) if 'campaign_type' in df.columns else ['All']
            selected_type = st.selectbox("Campaign Type", campaign_types)
        
        with filter_cols[2]:
            channels = ['All'] + sorted(df['channel_used'].unique().tolist()) if 'channel_used' in df.columns else ['All']
            selected_channel = st.selectbox("Channel", channels)
        
        with filter_cols[3]:
            audiences = ['All'] + sorted(df['target_audience'].unique().tolist()) if 'target_audience' in df.columns else ['All']
            selected_audience = st.selectbox("Audience", audiences)
        
        with filter_cols[4]:
            locations = ['All'] + sorted(df['location'].unique().tolist()) if 'location' in df.columns else ['All']
            selected_location = st.selectbox("Location", locations)
        
        with filter_cols[5]:
            segments = ['All'] + sorted(df['customer_segment'].unique().tolist()) if 'customer_segment' in df.columns else ['All']
            selected_segment = st.selectbox("Customer Segment", segments)
        
        if st.button("🔄 Reset Filters"):
            st.rerun()
    
    # Apply filters
    filtered_df = df.copy()
    
    if date_range and len(date_range) == 2 and 'date' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) & 
            (filtered_df['date'].dt.date <= date_range[1])
        ]
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['campaign_type'] == selected_type]
    if selected_channel != 'All':
        filtered_df = filtered_df[filtered_df['channel_used'] == selected_channel]
    if selected_audience != 'All':
        filtered_df = filtered_df[filtered_df['target_audience'] == selected_audience]
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
    if selected_segment != 'All':
        filtered_df = filtered_df[filtered_df['customer_segment'] == selected_segment]
    
    # =========================================================================
    # KPI CARDS
    # =========================================================================
    st.markdown("<div class='section-header'>Key Performance Indicators</div>", unsafe_allow_html=True)
    
    total_campaigns = len(filtered_df)
    total_impressions = filtered_df['impressions'].sum()
    total_clicks = filtered_df['clicks'].sum()
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    # Weighted average ROI
    if total_impressions > 0:
        weighted_roi = (filtered_df['roi'] * filtered_df['impressions']).sum() / total_impressions
    else:
        weighted_roi = filtered_df['roi'].mean()
    
    avg_conversion = filtered_df['conversion_rate'].mean() * 100 if 'conversion_rate' in filtered_df.columns else 0
    
    kpi_cols = st.columns(6)
    
    kpis = [
        ("Total Campaigns", format_number(total_campaigns, 'thousands'), ""),
        ("Impressions", format_number(total_impressions, 'billions'), ""),
        ("Clicks", format_number(total_clicks, 'thousands'), ""),
        ("CTR", format_number(overall_ctr, 'percent'), "clicks ÷ impressions"),
        ("Avg ROI", format_number(weighted_roi, 'decimal'), "weighted average"),
        ("Conversion Rate", format_number(avg_conversion, 'percent'), ""),
    ]
    
    for col, (label, value, note) in zip(kpi_cols, kpis):
        with col:
            note_html = f"<p class='kpi-note'>{note}</p>" if note else ""
            st.markdown(f"""
            <div class="kpi-card">
                <p class="kpi-value">{value}</p>
                <p class="kpi-label">{label}</p>
                {note_html}
            </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # HEALTH INDICATORS
    # =========================================================================
    st.markdown("<div class='section-header'>Performance Health Check</div>", unsafe_allow_html=True)
    
    health_cols = st.columns(3)
    
    metrics_for_health = [
        ("ROI", weighted_roi, quantiles['roi'], False),
        ("CTR", overall_ctr / 100, quantiles['ctr'], True),
        ("Conversion Rate", avg_conversion / 100, quantiles['conversion_rate'], True),
    ]
    
    for col, (name, value, thresholds, is_pct) in zip(health_cols, metrics_for_health):
        emoji, status, badge_class, percentile = get_health_status(value, thresholds)
        display_val = f"{value*100:.2f}%" if is_pct else f"{value:.2f}"
        
        with col:
            st.markdown(f"""
            <div class="health-card">
                <span class="health-metric">{name}: {display_val}</span>
                <span class="health-badge {badge_class}">{emoji} {status} ({percentile})</span>
            </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # ROI CHARTS
    # =========================================================================
    st.markdown("<div class='section-header'>What's Driving ROI?</div>", unsafe_allow_html=True)
    
    chart_cols = st.columns(2)
    
    # Chart 1: ROI by Channel
    with chart_cols[0]:
        st.markdown("**ROI by Marketing Channel**")
        if 'channel_used' in filtered_df.columns:
            channel_roi = filtered_df.groupby('channel_used')['roi'].mean().sort_values(ascending=True)
            
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='#0e1117')
            ax.set_facecolor('#0e1117')
            
            colors = ['#ef4444' if v < quantiles['roi']['p25'] else '#22c55e' if v > quantiles['roi']['p75'] else '#f59e0b' 
                      for v in channel_roi]
            bars = ax.barh(channel_roi.index, channel_roi.values, color=colors, height=0.6)
            
            for bar, val in zip(bars, channel_roi.values):
                ax.text(val + 0.08, bar.get_y() + bar.get_height()/2, f'{val:.2f}', 
                        va='center', fontsize=10, fontweight='bold', color='white')
            
            ax.axvline(weighted_roi, color='#64748b', linestyle='--', linewidth=1.5)
            ax.text(weighted_roi, ax.get_ylim()[1], f' Avg: {weighted_roi:.2f}', va='bottom', fontsize=9, color='#94a3b8')
            
            ax.set_xlabel('Average ROI', fontsize=10, color='#94a3b8')
            ax.set_xlim(0, channel_roi.max() * 1.25)
            ax.tick_params(colors='#94a3b8')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#334155')
            ax.spines['left'].set_color('#334155')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    # Chart 2: ROI by Campaign Type
    with chart_cols[1]:
        st.markdown("**ROI by Campaign Type**")
        if 'campaign_type' in filtered_df.columns:
            type_roi = filtered_df.groupby('campaign_type')['roi'].mean().sort_values(ascending=True)
            
            fig, ax = plt.subplots(figsize=(8, 4), facecolor='#0e1117')
            ax.set_facecolor('#0e1117')
            
            colors = ['#ef4444' if v < quantiles['roi']['p25'] else '#22c55e' if v > quantiles['roi']['p75'] else '#f59e0b' 
                      for v in type_roi]
            bars = ax.barh(type_roi.index, type_roi.values, color=colors, height=0.6)
            
            for bar, val in zip(bars, type_roi.values):
                ax.text(val + 0.08, bar.get_y() + bar.get_height()/2, f'{val:.2f}', 
                        va='center', fontsize=10, fontweight='bold', color='white')
            
            ax.axvline(weighted_roi, color='#64748b', linestyle='--', linewidth=1.5)
            ax.text(weighted_roi, ax.get_ylim()[1], f' Avg: {weighted_roi:.2f}', va='bottom', fontsize=9, color='#94a3b8')
            
            ax.set_xlabel('Average ROI', fontsize=10, color='#94a3b8')
            ax.set_xlim(0, type_roi.max() * 1.25)
            ax.tick_params(colors='#94a3b8')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#334155')
            ax.spines['left'].set_color('#334155')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    # =========================================================================
    # CTR vs ROI SCATTER - FIXED
    # =========================================================================
    st.markdown("<div class='section-header'>CTR vs ROI Analysis</div>", unsafe_allow_html=True)
    
    # Explanation ABOVE the chart
    st.markdown("""
    **How to read this chart:**
    - **Green (top-right):** High CTR + High ROI = Best campaigns ✓
    - **Orange (bottom-right):** High CTR + Low ROI = "Vanity" campaigns (lots of clicks, poor profit) ⚠️
    - **Blue (top-left):** Low CTR + High ROI = Hidden gems (niche but profitable)
    - **Gray (bottom-left):** Low CTR + Low ROI = Underperformers
    """)
    
    # Sample for performance
    sample_df = filtered_df.sample(min(2000, len(filtered_df)), random_state=42)
    
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0e1117')
    ax.set_facecolor('#0e1117')
    
    ctr_med = filtered_df['ctr'].median()
    roi_med = filtered_df['roi'].median()
    
    # Assign colors by quadrant
    colors_list = []
    for _, row in sample_df.iterrows():
        if row['ctr'] >= ctr_med and row['roi'] >= roi_med:
            colors_list.append('#22c55e')  # Green - Stars
        elif row['ctr'] >= ctr_med and row['roi'] < roi_med:
            colors_list.append('#f97316')  # Orange - Vanity
        elif row['ctr'] < ctr_med and row['roi'] >= roi_med:
            colors_list.append('#3b82f6')  # Blue - Hidden gems
        else:
            colors_list.append('#6b7280')  # Gray - Dogs
    
    ax.scatter(sample_df['ctr'] * 100, sample_df['roi'], c=colors_list, alpha=0.6, s=25, edgecolors='none')
    
    # Quadrant lines
    ax.axhline(roi_med, color='#475569', linestyle='--', linewidth=1)
    ax.axvline(ctr_med * 100, color='#475569', linestyle='--', linewidth=1)
    
    ax.set_xlabel('CTR (%)', fontsize=11, color='#e2e8f0')
    ax.set_ylabel('ROI', fontsize=11, color='#e2e8f0')
    ax.tick_params(colors='#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#334155')
    ax.spines['left'].set_color('#334155')
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # =========================================================================
    # ACTIONABLE INSIGHTS - FIXED VISIBILITY
    # =========================================================================
    st.markdown("<div class='section-header'>Actionable Insights</div>", unsafe_allow_html=True)
    
    st.markdown("""
    **What is this?** These are data-driven recommendations based on your filtered campaigns. 
    Each insight shows: *What we found* → *What to do about it*.
    """)
    
    insights = generate_insights(df, filtered_df, quantiles)
    
    for insight in insights[:5]:
        st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)
    
    # =========================================================================
    # TOP & BOTTOM PERFORMERS
    # =========================================================================
    st.markdown("<div class='section-header'>Campaign Performance Table</div>", unsafe_allow_html=True)
    
    perf_cols = st.columns(2)
    
    with perf_cols[0]:
        st.markdown("**Top 10 Campaigns by ROI**")
        top_df = filtered_df.nlargest(10, 'roi')[['campaign_id', 'campaign_type', 'channel_used', 'roi', 'ctr', 'conversion_rate']].copy()
        top_df['ctr'] = (top_df['ctr'] * 100).round(2).astype(str) + '%'
        top_df['conversion_rate'] = (top_df['conversion_rate'] * 100).round(2).astype(str) + '%'
        top_df['roi'] = top_df['roi'].round(2)
        top_df.columns = ['ID', 'Type', 'Channel', 'ROI', 'CTR', 'Conv%']
        st.dataframe(top_df, use_container_width=True, hide_index=True)
    
    with perf_cols[1]:
        st.markdown("**Bottom 10 Campaigns by ROI** *(review these)*")
        bottom_df = filtered_df.nsmallest(10, 'roi')[['campaign_id', 'campaign_type', 'channel_used', 'roi', 'ctr', 'conversion_rate']].copy()
        bottom_df['ctr'] = (bottom_df['ctr'] * 100).round(2).astype(str) + '%'
        bottom_df['conversion_rate'] = (bottom_df['conversion_rate'] * 100).round(2).astype(str) + '%'
        bottom_df['roi'] = bottom_df['roi'].round(2)
        bottom_df.columns = ['ID', 'Type', 'Channel', 'ROI', 'CTR', 'Conv%']
        st.dataframe(bottom_df, use_container_width=True, hide_index=True)
    
    # =========================================================================
    # HOW TO INTERPRET
    # =========================================================================
    with st.expander("ℹ️ How to interpret this dashboard"):
        st.markdown("""
        **Key Metrics Explained:**
        
        - **ROI (Return on Investment):** How much profit per dollar spent. ROI of 5.0 = $5 return per $1 invested.
        
        - **CTR (Click-Through Rate):** % of people who clicked your ad. Higher isn't always better—what matters is whether those clicks convert.
        
        - **Health Indicators:** Compares your current metrics to your historical data:
          - 🟢 Green = Top 25% (doing great)
          - 🟡 Yellow = Middle 50% (normal)  
          - 🔴 Red = Bottom 25% (needs attention)
        
        - **Bar Chart Colors:** Green = above average, Yellow = average, Red = below average ROI.
        """)
    
    # =========================================================================
    # FOOTER
    # =========================================================================
    st.markdown("---")
    st.caption(f"Showing {len(filtered_df):,} of {len(df):,} campaigns | Data: {df['date'].min().strftime('%b %Y')} – {df['date'].max().strftime('%b %Y') if 'date' in df.columns else 'N/A'}")


if __name__ == "__main__":
    main()
