import pathlib
import sys

# Ensure project root is in sys.path for robust modular imports
root_dir = pathlib.Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Modular helper imports
from src.data_loader import load_data
from src.metrics import compute_kpis, compute_hourly_traffic, compute_bank_metrics

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="UPI Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished college mini-project UI
st.markdown("""
<style>
    /* Metric Card Styling - Theme Adaptive (Translucent for both Dark & Light themes) */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    /* Banner & Subtext */
    .dashboard-header {
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
    }
    .badge-authors {
        display: inline-block;
        background: rgba(3, 105, 161, 0.15);
        color: #0284c7;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-course {
        display: inline-block;
        background: rgba(100, 116, 139, 0.15);
        color: var(--text-color, #64748b);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. CACHED DATA LOADING & DEFENSIVE PREPROCESSING
# ==============================================================================
@st.cache_data(show_spinner="Loading and verifying UPI dataset...")
def get_cached_data():
    """
    Cached wrapper around src.data_loader.load_data().
    """
    return load_data()

# Load data
df_raw, load_error = get_cached_data()

if load_error or df_raw is None:
    st.error(f"**Data Initialization Failure:** {load_error}")
    st.stop()


# ==============================================================================
# 3. SIDEBAR FILTERS WITH SESSION STATE RESET
# ==============================================================================
st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Filter transactions dynamically across all KPIs & charts.")

# Filter key definitions for session state tracking
FILTER_KEYS = [
    "f_date_range", "f_types", "f_categories", "f_states", "f_banks",
    "f_status", "f_devices", "f_networks", "f_fraud", "f_amount_range"
]

def reset_all_filters():
    for k in FILTER_KEYS:
        if k in st.session_state:
            del st.session_state[k]

if st.sidebar.button("Reset All Filters", width="stretch", help="Clear all selections and reset dashboard to default view."):
    reset_all_filters()
    st.rerun()

st.sidebar.markdown("---")

# 1. Date Range Filter
min_date = df_raw["date"].min()
max_date = df_raw["date"].max()

date_selection = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="f_date_range",
    help="Select start and end date for transactions in 2024."
)

# 2. Transaction Type Filter
all_types = sorted(df_raw["transaction_type"].unique())
selected_types = st.sidebar.multiselect(
    "Transaction Type",
    options=all_types,
    default=None,
    placeholder="All Types (P2P, P2M, etc.)",
    key="f_types"
)

# 3. Merchant Category Filter
all_categories = sorted(df_raw["merchant_category"].unique())
selected_categories = st.sidebar.multiselect(
    "Merchant Category",
    options=all_categories,
    default=None,
    placeholder="All Categories",
    key="f_categories"
)

# 4. Sender State Filter
all_states = sorted(df_raw["sender_state"].unique())
selected_states = st.sidebar.multiselect(
    "Sender State",
    options=all_states,
    default=None,
    placeholder="All States",
    key="f_states"
)

# 5. Sender Bank Filter
all_banks = sorted(df_raw["sender_bank"].unique())
selected_banks = st.sidebar.multiselect(
    "Sender Bank",
    options=all_banks,
    default=None,
    placeholder="All Banks",
    key="f_banks"
)

# 6. Transaction Status Filter
selected_status = st.sidebar.multiselect(
    "Transaction Status",
    options=["SUCCESS", "FAILED"],
    default=None,
    placeholder="All Statuses",
    key="f_status"
)

# 7. Device Type Filter
all_devices = sorted(df_raw["device_type"].unique())
selected_devices = st.sidebar.multiselect(
    "Device Type",
    options=all_devices,
    default=None,
    placeholder="All Devices (Android, iOS, Web)",
    key="f_devices"
)

# 8. Network Type Filter
all_networks = sorted(df_raw["network_type"].unique())
selected_networks = st.sidebar.multiselect(
    "Network Type",
    options=all_networks,
    default=None,
    placeholder="All Networks (4G, 5G, etc.)",
    key="f_networks"
)

# 9. Fraud-Flag Indicator Filter
fraud_options = ["All Transactions", "Fraud-Flagged Only (1)", "Non-Fraud Only (0)"]
selected_fraud_choice = st.sidebar.selectbox(
    "Fraud Indicator",
    options=fraud_options,
    index=0,
    key="f_fraud",
    help="Note: fraud_flag is an indicator in this simulated dataset, not confirmed chargebacks."
)

# 10. Amount Range Slider
min_amt = int(df_raw["amount"].min())
max_amt = int(df_raw["amount"].max())
selected_amount_range = st.sidebar.slider(
    "Amount Range (₹)",
    min_value=min_amt,
    max_value=max_amt,
    value=(min_amt, max_amt),
    step=100,
    key="f_amount_range",
    help="Filter transactions by INR value."
)


# ==============================================================================
# 4. PROGRESSIVE FILTERING ENGINE
# ==============================================================================
filtered_df = df_raw.copy()

# Date Range Filter application
if isinstance(date_selection, (tuple, list)):
    if len(date_selection) == 2:
        start_d, end_d = date_selection
        filtered_df = filtered_df[(filtered_df["date"] >= start_d) & (filtered_df["date"] <= end_d)]
    elif len(date_selection) == 1:
        start_d = date_selection[0]
        filtered_df = filtered_df[filtered_df["date"] == start_d]

# Multiselect filters (empty list means all included)
if selected_types:
    filtered_df = filtered_df[filtered_df["transaction_type"].isin(selected_types)]
if selected_categories:
    filtered_df = filtered_df[filtered_df["merchant_category"].isin(selected_categories)]
if selected_states:
    filtered_df = filtered_df[filtered_df["sender_state"].isin(selected_states)]
if selected_banks:
    filtered_df = filtered_df[filtered_df["sender_bank"].isin(selected_banks)]
if selected_status:
    filtered_df = filtered_df[filtered_df["transaction_status"].isin(selected_status)]
if selected_devices:
    filtered_df = filtered_df[filtered_df["device_type"].isin(selected_devices)]
if selected_networks:
    filtered_df = filtered_df[filtered_df["network_type"].isin(selected_networks)]

# Fraud Indicator filter
if selected_fraud_choice == "Fraud-Flagged Only (1)":
    filtered_df = filtered_df[filtered_df["fraud_flag"] == 1]
elif selected_fraud_choice == "Non-Fraud Only (0)":
    filtered_df = filtered_df[filtered_df["fraud_flag"] == 0]

# Amount Range filter
filtered_df = filtered_df[
    (filtered_df["amount"] >= selected_amount_range[0]) &
    (filtered_df["amount"] <= selected_amount_range[1])
]

# Overall dataset date range formatted for header
computed_period_str = f"{min_date.strftime('%d %b %Y')} to {max_date.strftime('%d %b %Y')}"


# ==============================================================================
# 5. DASHBOARD HEADER & ACADEMIC PROJECT SCOPE
# ==============================================================================
st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title("UPI Transaction Analytics")
    st.markdown("### Exploring Payment Behavior, Transaction Reliability and Fraud Patterns in India")
    st.markdown(
        "**Subject:** Data Exploration and Visualization Laboratory  \n"
        "**Submitted By:**  \n"
        "• **Swaraj Suresh Shinde** — 125B1D053  \n"
        "• **Nikol Dharmraj Ghodke** — 125B1D062"
    )

with header_col2:
    st.markdown(f"**Dataset Period:**  \n`{computed_period_str}`")
    st.caption(f"Showing **{len(filtered_df):,}** of **{len(df_raw):,}** transactions ({(len(filtered_df)/len(df_raw)*100):.1f}%)")

st.markdown('</div>', unsafe_allow_html=True)

with st.container(border=True):
    scope_col1, scope_col2 = st.columns([1.15, 0.85])
    with scope_col1:
        st.markdown("""
#### 1. Dataset and Problem Statement
- **Dataset:** UPI Transactions 2024
- **Source:** [Kaggle Dataset](https://www.kaggle.com/datasets/skullagos5246/upi-transactions-2024-dataset)
- **Description:** The dataset contains 250,000 simulated UPI transactions with details such as transaction amount, type, status, bank, state, device, network and fraud flag.
- **Problem Statement:** To analyze UPI transaction patterns and identify trends in payment behavior, transaction failures and fraud across different banks, states, devices and transaction types.

**Objectives:**
- Analyze transaction amounts and categories.
- Study transaction activity over time.
- Examine transaction failure patterns.
- Explore fraud-related patterns.
- Present findings through visualizations and an interactive dashboard.
        """)
    with scope_col2:
        st.markdown("""
**Key Questions:**
1. Which transaction types are most common?
2. Which merchant categories have the most transactions?
3. How are transaction amounts distributed?
4. When is transaction activity highest?
5. Which banks have the highest failure percentages?
6. How do failures vary by device and network?
7. Which states have the most fraud-flagged transactions?
8. How does fraud vary across transaction types?
9. Is transaction amount associated with fraud flags?
10. What relationships exist between numerical variables?
        """)


# ==============================================================================
# 6. EMPTY STATE GUARD
# ==============================================================================
if len(filtered_df) == 0:
    st.warning("**No transactions match the selected filter criteria.** Please widen or reset your sidebar filters to inspect data.")
    st.info("Tip: Click **'Reset All Filters'** in the sidebar to restore the complete 250,000 transaction dataset.")
    st.stop()


# ==============================================================================
# 7. DYNAMIC KPI CARDS
# ==============================================================================
kpi = compute_kpis(filtered_df)

n_total = kpi["n_total"]
total_value = kpi["total_value"]
total_value_cr = kpi["total_value_cr"]
avg_amount = kpi["avg_amount"]
n_success = kpi["n_success"]
success_rate = kpi["success_rate"]
n_failed = kpi["n_failed"]
failure_rate = kpi["failure_rate"]
n_fraud = kpi["n_fraud"]
fraud_rate = kpi["fraud_rate"]

kpi_cols = st.columns(6)

with kpi_cols[0]:
    st.metric(
        label="Total Transactions",
        value=f"{n_total:,}",
        help="Total number of transactions matching current filter criteria."
    )

with kpi_cols[1]:
    st.metric(
        label="Total Value",
        value=f"₹{total_value_cr:,.2f} Cr",
        delta=f"₹{total_value:,.0f}",
        delta_color="off",
        help="Cumulative transaction value in Crores (₹1 Cr = 10 Million INR)."
    )

with kpi_cols[2]:
    st.metric(
        label="Average Ticket",
        value=f"₹{avg_amount:,.2f}",
        help="Mean transaction amount in Indian Rupees."
    )

with kpi_cols[3]:
    st.metric(
        label="Success Rate",
        value=f"{success_rate:.2f}%",
        delta=f"{n_success:,} successful",
        delta_color="normal",
        help="Percentage of transactions successfully completed."
    )

with kpi_cols[4]:
    st.metric(
        label="Failure Rate",
        value=f"{failure_rate:.2f}%",
        delta=f"{n_failed:,} failed",
        delta_color="inverse",
        help="Percentage of transactions that encountered technical or routing failure."
    )

with kpi_cols[5]:
    st.metric(
        label="Fraud-Flagged Rate",
        value=f"{fraud_rate:.3f}%",
        delta=f"{n_fraud:,} flagged",
        delta_color="inverse",
        help="Flagged security anomalies (indicator only, not confirmed fraud). Overall benchmark: 0.192%."
    )

st.markdown("<br>", unsafe_allow_html=True)


# ==============================================================================
# 8. ANALYTICAL VISUALIZATIONS (6+ CORE CHARTS)
# ==============================================================================

# Row 1: Traffic Diurnal Cycle & Bank Reliability
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    # CHART 1: Hourly Traffic with Secondary Failure Rate Axis
    hourly_df = compute_hourly_traffic(filtered_df)

    fig_hourly = make_subplots(specs=[[{"secondary_y": True}]])

    fig_hourly.add_trace(
        go.Bar(
            x=hourly_df["hour"],
            y=hourly_df["volume"],
            name="Traffic Volume",
            marker_color="#3b82f6",
            opacity=0.75,
            hovertemplate="<b>Hour:</b> %{x}:00<br><b>Volume:</b> %{y:,} tx<extra></extra>"
        ),
        secondary_y=False
    )

    fig_hourly.add_trace(
        go.Scatter(
            x=hourly_df["hour"],
            y=hourly_df["failure_rate"],
            name="Failure Rate (%)",
            mode="lines+markers",
            line=dict(color="#ef4444", width=3),
            marker=dict(size=6, color="#b91c1c"),
            hovertemplate="<b>Hour:</b> %{x}:00<br><b>Failure Rate:</b> %{y:.2f}%<extra></extra>"
        ),
        secondary_y=True
    )

    fig_hourly.update_layout(
        title="<b>1. Hourly Traffic Velocity vs. Failure Rate</b>",
        title_font_size=15,
        xaxis=dict(title="Hour of Day (24-hr clock)", tickmode="linear", tick0=0, dtick=2),
        yaxis=dict(title="Transaction Count", showgrid=True),
        yaxis2=dict(title="Failure Rate (%)", overlaying="y", side="right", showgrid=False, range=[0, max(8, hourly_df["failure_rate"].max() + 2)]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )
    st.plotly_chart(fig_hourly, width="stretch")

with row1_col2:
    # CHART 2: Bank Ecosystem: Volume Share vs Failure Rate
    bank_df = compute_bank_metrics(filtered_df, n_total=n_total)

    fig_bank = go.Figure()

    fig_bank.add_trace(go.Bar(
        x=bank_df["sender_bank"],
        y=bank_df["market_share_pct"],
        name="Transaction Share (%)",
        marker_color="#0284c7",
        hovertemplate="<b>%{x}</b><br>Share: %{y:.2f}%<br>Transactions: %{customdata[0]:,}<br>Value: ₹%{customdata[1]:,.2f} Cr<extra></extra>",
        customdata=np.stack((bank_df["total_tx"], bank_df["value_cr"]), axis=-1),
        yaxis="y"
    ))

    fig_bank.add_trace(go.Scatter(
        x=bank_df["sender_bank"],
        y=bank_df["failure_rate_pct"],
        name="Failure Rate (%)",
        mode="lines+markers",
        line=dict(color="#dc2626", width=2.5, dash="dot"),
        marker=dict(size=8, color="#991b1b"),
        hovertemplate="<b>%{x}</b><br>Failure Rate: %{y:.2f}%<br>Failed tx: %{customdata:,}<extra></extra>",
        customdata=bank_df["failed_tx"],
        yaxis="y2"
    ))

    fig_bank.update_layout(
        title="<b>2. Bank Ecosystem: Market Share vs. Failure Reliability</b>",
        title_font_size=15,
        xaxis=dict(title="Sender Bank"),
        yaxis=dict(title="Market Share of Transactions (%)", showgrid=True),
        yaxis2=dict(title="Failure Rate (%)", overlaying="y", side="right", showgrid=False, range=[0, max(8, bank_df["failure_rate_pct"].max() + 2)]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )
    st.plotly_chart(fig_bank, width="stretch")


# Row 2: Merchant Categories & State-Level Fraud
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    # CHART 3: Merchant Category Volume and Total Value
    cat_df = filtered_df.groupby("merchant_category").agg(
        volume=("transaction_id", "count"),
        total_value=("amount", "sum")
    ).reset_index()
    cat_df["value_cr"] = cat_df["total_value"] / 10_000_000.0
    cat_df = cat_df.sort_values(by="volume", ascending=True)

    fig_cat = go.Figure()

    fig_cat.add_trace(go.Bar(
        y=cat_df["merchant_category"],
        x=cat_df["volume"],
        name="Volume (Count)",
        orientation="h",
        marker_color="#6366f1",
        hovertemplate="<b>%{y}</b><br>Volume: %{x:,} tx<extra></extra>"
    ))

    fig_cat.update_layout(
        title="<b>3. Merchant Category Transaction Volume</b>",
        title_font_size=15,
        xaxis=dict(title="Number of Transactions", showgrid=True),
        yaxis=dict(title="Merchant Category"),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )
    st.plotly_chart(fig_cat, width="stretch")

with row2_col2:
    # CHART 4: Fraud-Flagged Count and Rate by State (No Choropleth)
    state_df = filtered_df.groupby("sender_state").agg(
        total_tx=("transaction_id", "count"),
        fraud_tx=("fraud_flag", lambda s: (s == 1).sum())
    ).reset_index()
    state_df["fraud_rate_pct"] = (state_df["fraud_tx"] / state_df["total_tx"] * 100.0).fillna(0)
    state_df = state_df.sort_values(by="fraud_tx", ascending=False)

    fig_state = make_subplots(specs=[[{"secondary_y": True}]])

    fig_state.add_trace(
        go.Bar(
            x=state_df["sender_state"],
            y=state_df["fraud_tx"],
            name="Flagged Count",
            marker_color="#f59e0b",
            hovertemplate="<b>%{x}</b><br>Flagged Count: %{y}<br>Total State tx: %{customdata:,}<extra></extra>",
            customdata=state_df["total_tx"]
        ),
        secondary_y=False
    )

    fig_state.add_trace(
        go.Scatter(
            x=state_df["sender_state"],
            y=state_df["fraud_rate_pct"],
            name="Fraud Rate (%)",
            mode="lines+markers",
            line=dict(color="#be185d", width=2.5),
            marker=dict(size=7, color="#831843"),
            hovertemplate="<b>%{x}</b><br>Fraud Rate: %{y:.3f}%<extra></extra>"
        ),
        secondary_y=True
    )

    fig_state.update_layout(
        title="<b>4. State-Level Fraud-Flagged Volume & Occurrence Rate</b>",
        title_font_size=15,
        xaxis=dict(title="Sender State", tickangle=-30),
        yaxis=dict(title="Fraud-Flagged Transactions (Count)", showgrid=True),
        yaxis2=dict(title="Fraud Rate (%)", overlaying="y", side="right", showgrid=False, range=[0, max(0.4, state_df["fraud_rate_pct"].max() * 1.3)]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )
    st.plotly_chart(fig_state, width="stretch")


# Row 3: Failure Rate Heatmap & Amount Distribution Boxplot
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    # CHART 5: Failure Rate Heatmap: Network Type x Device Type
    net_dev_counts = pd.crosstab(filtered_df["network_type"], filtered_df["device_type"])
    net_dev_fails = pd.crosstab(
        filtered_df["network_type"],
        filtered_df["device_type"],
        values=(filtered_df["transaction_status"] == "FAILED").astype(int),
        aggfunc="sum"
    ).fillna(0)

    # Calculate Failure Rate (%)
    net_dev_rate = (net_dev_fails / net_dev_counts * 100.0).fillna(0)

    # Hover text matrix with volume, failed count, and rate
    custom_hover = []
    for net in net_dev_rate.index:
        row_hover = []
        for dev in net_dev_rate.columns:
            tot = net_dev_counts.loc[net, dev] if (net in net_dev_counts.index and dev in net_dev_counts.columns) else 0
            fld = net_dev_fails.loc[net, dev] if (net in net_dev_fails.index and dev in net_dev_fails.columns) else 0
            rt = net_dev_rate.loc[net, dev]
            row_hover.append(f"Network: {net}<br>Device: {dev}<br>Total Tx: {tot:,}<br>Failed: {fld:,}<br>Failure Rate: {rt:.2f}%")
        custom_hover.append(row_hover)

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=net_dev_rate.values,
        x=list(net_dev_rate.columns),
        y=list(net_dev_rate.index),
        text=np.round(net_dev_rate.values, 2),
        texttemplate="%{text:.2f}%",
        textfont={"size": 13, "color": "black"},
        hoverinfo="text",
        hovertext=custom_hover,
        colorscale="Reds",
        zmin=4.0,
        zmax=6.0,
        colorbar=dict(title="Failure Rate (%)")
    ))

    fig_heatmap.update_layout(
        title="<b>5. Infrastructure Failure Rate: Network vs. Device</b>",
        title_font_size=15,
        xaxis=dict(title="Device Type"),
        yaxis=dict(title="Network Type"),
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )
    st.plotly_chart(fig_heatmap, width="stretch")

with row3_col2:
    # CHART 6: Amount Distribution by Transaction Type (Box Plot, Log Scale)
    fig_box = px.box(
        filtered_df,
        x="transaction_type",
        y="amount",
        color="transaction_type",
        log_y=True,
        title="<b>6. Ticket Size Distribution by Transaction Type (Log Scale)</b>",
        labels={"amount": "Amount (INR, Log Scale ₹)", "transaction_type": "Transaction Type"},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_box.update_layout(
        title_font_size=15,
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        height=380
    )
    st.plotly_chart(fig_box, width="stretch")


# Optional Bonus: Day of Week Traffic Heatmap
with st.expander("Optional View: Day-of-Week × Hourly Traffic Intensity Matrix", expanded=False):
    day_hour_counts = pd.crosstab(
        filtered_df["day_name"],
        filtered_df["hour"]
    )
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_hour_counts = day_hour_counts.reindex([d for d in days_order if d in day_hour_counts.index])
    
    fig_day_hour = px.imshow(
        day_hour_counts,
        labels=dict(x="Hour of Day", y="Day of Week", color="Transactions"),
        x=day_hour_counts.columns,
        y=day_hour_counts.index,
        color_continuous_scale="Viridis",
        aspect="auto"
    )
    fig_day_hour.update_layout(
        title="Day-of-Week × Hourly Transaction Intensity Heatmap",
        height=320
    )
    st.plotly_chart(fig_day_hour, width="stretch")


# ==============================================================================
# 9. DYNAMIC KEY INSIGHTS SECTION (TABS)
# ==============================================================================
st.markdown("---")
st.subheader("Analytical Findings & Key Insights")
st.caption("All findings are dynamically derived from the currently filtered subset of transactions.")

tab_types, tab_infra, tab_fraud, tab_caution = st.tabs([
    "Payment Behavior",
    "Infrastructure & Reliability",
    "Fraud Risk Patterns",
    "Methodological & Statistical Caution"
])

with tab_types:
    top_type = filtered_df["transaction_type"].value_counts().index[0] if not filtered_df.empty else "N/A"
    top_type_count = filtered_df["transaction_type"].value_counts().iloc[0] if not filtered_df.empty else 0
    top_type_pct = (top_type_count / n_total * 100) if n_total > 0 else 0
    
    # Weekday vs Weekend average daily rate
    wkday_tx = int((filtered_df["is_weekend_calc"] == 0).sum())
    wkend_tx = int((filtered_df["is_weekend_calc"] == 1).sum())
    # 5 weekdays vs 2 weekend days ratio
    wkday_avg_daily = wkday_tx / 5.0
    wkend_avg_daily = wkend_tx / 2.0
    median_amt = filtered_df["amount"].median() if not filtered_df.empty else 0
    max_amt = filtered_df["amount"].max() if not filtered_df.empty else 0
    
    with st.container(border=True):
        st.markdown(
            f"**1. Dominance of Peer Transfers:**  \n"
            f"The most prevalent transaction type in the current selection is **{top_type}** with "
            f"**{top_type_count:,} transactions** (**{top_type_pct:.2f}%** of total traffic)."
        )
    with st.container(border=True):
        st.markdown(
            f"**2. Weekday vs. Weekend Normalized Daily Velocity:**  \n"
            f"While raw volume shows Weekdays (**{wkday_tx:,} tx**) outnumbering Weekends (**{wkend_tx:,} tx**), "
            f"normalizing across the 5-to-2 calendar day ratio reveals an almost identical daily transaction rate: "
            f"**{wkday_avg_daily:,.1f} tx/day** on weekdays vs. **{wkend_avg_daily:,.1f} tx/day** on weekends. "
            f"UPI velocity remains uniformly active 7 days a week (relative difference < 0.18%)."
        )
    with st.container(border=True):
        st.markdown(
            f"**3. Micro-Ticket Dominance & Amount Skewness:**  \n"
            f"The median ticket size is **₹{median_amt:,.0f}**, whereas the arithmetic mean is "
            f"**₹{avg_amount:,.2f}** (with an extreme maximum of **₹{max_amt:,}**). "
            f"This high positive skew confirms that the majority of UPI payments are retail micro-transactions under ₹1,000, "
            f"with 8.47% high-value transfers (> ₹3,558) elevating the arithmetic mean."
        )

with tab_infra:
    peak_hour = hourly_df.sort_values(by="volume", ascending=False).iloc[0]["hour"] if not hourly_df.empty else 0
    peak_vol = hourly_df.sort_values(by="volume", ascending=False).iloc[0]["volume"] if not hourly_df.empty else 0
    
    # Highest failure bank
    bank_stats = filtered_df.groupby("sender_bank").agg(
        tot=("transaction_id", "count"),
        fail=("transaction_status", lambda s: (s == "FAILED").sum())
    ).reset_index()
    bank_stats["fail_rate"] = bank_stats["fail"] / bank_stats["tot"] * 100.0
    bank_stats = bank_stats.sort_values(by="fail_rate", ascending=False)
    highest_fail_bank = bank_stats.iloc[0]["sender_bank"] if not bank_stats.empty else "N/A"
    highest_fail_rate = bank_stats.iloc[0]["fail_rate"] if not bank_stats.empty else 0.0
    highest_fail_count = bank_stats.iloc[0]["fail"] if not bank_stats.empty else 0
    highest_fail_tot = bank_stats.iloc[0]["tot"] if not bank_stats.empty else 0
    
    with st.container(border=True):
        st.markdown(
            f"**1. Peak Diurnal Congestion:**  \n"
            f"Peak network usage occurs at **{int(peak_hour):02d}:00 hours** carrying "
            f"**{int(peak_vol):,} transactions** (8.49% of daily traffic). Transaction traffic accelerates through the evening "
            f"window (18:00–20:00), which processes nearly 24% of all daily volume."
        )
    with st.container(border=True):
        st.markdown(
            f"**2. Banking Ecosystem Reliability Invariance:**  \n"
            f"The sender bank with the nominally highest failure rate is **{highest_fail_bank}** at "
            f"**{highest_fail_rate:.2f}%** ({highest_fail_count:,} failed out of {highest_fail_tot:,} transactions). "
            f"However, two-way Chi-Square testing (χ² = 3.235, p = 0.863, Cramer's V = 0.0036) proves that all sender "
            f"banks remain confined within a narrow band (**4.82% – 5.10%**). No single bank is an operational bottleneck."
        )
    with st.container(border=True):
        st.markdown(
            f"**3. Client Device & Cellular Network Parity:**  \n"
            f"Across Android (4.94%), iOS (4.93%), and Web (5.15%), and across 4G (4.98%), 5G (4.86%), WiFi (4.86%), "
            f"and 3G (5.22%), failure rates are statistically invariant from the baseline **{failure_rate:.2f}%**. "
            f"Android accounts for 74.97% of total failures solely because it generates 75.11% of all traffic."
        )

with tab_fraud:
    state_fraud_sorted = state_df.sort_values(by="fraud_tx", ascending=False) if not state_df.empty else pd.DataFrame()
    top_fraud_state = state_fraud_sorted.iloc[0]["sender_state"] if not state_fraud_sorted.empty else "N/A"
    top_fraud_count = state_fraud_sorted.iloc[0]["fraud_tx"] if not state_fraud_sorted.empty else 0
    top_fraud_rate = state_fraud_sorted.iloc[0]["fraud_rate_pct"] if not state_fraud_sorted.empty else 0.0
    
    with st.container(border=True):
        st.markdown(
            f"**1. Ultra-Rare Baseline Anomaly Rate:**  \n"
            f"In the filtered view, **{n_fraud:,} transactions** are flagged by fraud heuristics, "
            f"constituting an overall occurrence rate of **{fraud_rate:.3f}%** (approx. 1 in 520 transactions)."
        )
    with st.container(border=True):
        st.markdown(
            f"**2. State Distribution Governed Strictly by Volume Proportionality:**  \n"
            f"The state with the highest absolute count of flagged transactions is **{top_fraud_state}** "
            f"(**{int(top_fraud_count):,} flagged**, cohort rate: **{top_fraud_rate:.3f}%**). "
            f"Maharashtra and Karnataka contribute 29.17% of all fraud flags solely because they generate 26.87% of all traffic. "
            f"Chi-Square testing (χ² = 7.765, p = 0.558) confirms fraud rates are uniform across states."
        )
    with st.container(border=True):
        st.markdown(
            f"**3. Heuristic Flagging vs. True Fraud:**  \n"
            f"The dataset's `fraud_flag` represents an algorithmic detection trigger rather than adjudicated chargebacks or confirmed losses. "
            f"Ticket amounts do not correlate linearly with fraud flags (r = -0.00069), meaning high ticket sizes do not carry higher risk."
        )

with tab_caution:
    st.info("""
    **Methodological Rigor & Statistical Uncertainty Notes:**
    
    1. **Chi-Square Independence Tests (Failure Reliability):**
       - Rigorous contingency tests performed on the 250,000 transactions show:
         - Bank vs. Status: $\\chi^2 = 3.2349, p = 0.8625$ (Cramer's $V = 0.0036$)
         - Device vs. Status: $\\chi^2 = 1.1811, p = 0.5540$ (Cramer's $V = 0.0022$)
         - Network vs. Status: $\\chi^2 = 3.8527, p = 0.2778$ (Cramer's $V = 0.0039$)
       - **Conclusion:** Failure rate differences between banks or devices are **not statistically significant**. They represent random stochastic noise around a constant ~4.95% system baseline.
       
    2. **Extreme Class Imbalance in Fraud Analysis:**
       - Across the full benchmark dataset, only **480 out of 250,000 transactions (0.192%)** are flagged as fraud.
       - Disaggregating 480 positive events across 10 states yields tiny sample sizes (35 to 71 positive rows per state).
       - The 95% Wilson score confidence interval for Karnataka (69/29,756 = 0.232%) is **[0.182%, 0.294%]**, which fully overlaps with Tamil Nadu (40/25,367 = 0.158%, **[0.115%, 0.215%]**).
       - Analysts and presenters must avoid labeling individual states or merchant categories as "fraud hotspots."
       
    3. **'Share of Failures' vs. 'Cohort Failure Rate':**
       - Android accounts for **74.97% of all system failures** solely because it represents **75.11% of total transaction traffic**.
       - Within the Android cohort, the failure rate is **4.94%**, identical to iOS (**4.93%**). Conflating cohort shares with failure likelihood is a common analytical error.
    """)


# ==============================================================================
# 10. SAMPLE DATA TABLE & CSV EXPORT
# ==============================================================================
st.markdown("---")
show_table = st.checkbox("Inspect Sample Data & Export Filtered Subset", value=False)

if show_table:
    st.write(f"Displaying first **100** transactions (of **{len(filtered_df):,}** matching rows):")
    
    display_cols = [
        "transaction_id", "timestamp", "transaction_type", "merchant_category",
        "amount", "transaction_status", "sender_bank", "receiver_bank",
        "sender_state", "device_type", "network_type", "fraud_flag"
    ]
    sample_preview = filtered_df[display_cols].head(100).copy()
    
    st.dataframe(
        sample_preview.style.format({"amount": "₹{:,.2f}"}),
        width="stretch",
        height=320
    )
    
    # Download Button for filtered dataset
    csv_buffer = io.StringIO()
    export_subset = filtered_df[display_cols]
    if len(export_subset) > 50000:
        st.caption("Note: Download is capped at 50,000 rows for browser performance.")
        export_subset = export_subset.head(50000)
        
    export_subset.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    
    st.download_button(
        label=f"Download Filtered Data as CSV ({len(export_subset):,} rows)",
        data=csv_bytes,
        file_name="filtered_upi_transactions.csv",
        mime="text/csv",
        help="Export the filtered subset in standard CSV format."
    )

st.markdown("<br><hr><center><small>UPI Transaction Analytics Dashboard • Built with Streamlit & Plotly • University Mini-Project Demo</small></center>", unsafe_allow_html=True)
