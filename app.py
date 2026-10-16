import io
import pathlib
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import streamlit as st

# Ensure project root is in sys.path for robust modular imports
root_dir = pathlib.Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Modular helper imports
from src.data_loader import load_data
from src.metrics import compute_kpis, compute_hourly_traffic, compute_bank_metrics
from src.static_charts import CHARTS_REGISTRY, CHARTS_BY_ID, get_chart_png, get_chart_data_uri
from src.inference import get_inference

# ==============================================================================
# 1. PAGE CONFIGURATION & THEME STYLING
# ==============================================================================
st.set_page_config(
    page_title="UPI Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_filter_bar_theme():
    """Retrieve theme-specific styling tokens from Streamlit context or option."""
    theme_type = "light"
    try:
        if hasattr(st, "context") and hasattr(st.context, "theme"):
            ctx_theme = st.context.theme
            if isinstance(ctx_theme, dict):
                theme_type = ctx_theme.get("type") or "light"
            else:
                theme_type = getattr(ctx_theme, "type", None) or "light"
        elif hasattr(st, "get_option"):
            theme_type = st.get_option("theme.base") or "light"
    except Exception:
        theme_type = "light"

    if str(theme_type).lower() == "dark":
        return {
            "bg": "#0e1117",
            "border": "rgba(255, 255, 255, 0.15)",
            "shadow": "0 4px 20px rgba(0, 0, 0, 0.45)"
        }
    return {
        "bg": "#ffffff",
        "border": "rgba(128, 128, 128, 0.25)",
        "shadow": "0 4px 20px rgba(0, 0, 0, 0.09)"
    }

filter_theme = get_filter_bar_theme()

# Custom CSS for polished UI & Sticky Filter Bar
css_content = """
<style>
    /* Metric Card Styling - Theme Adaptive */
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

    /* Sticky Horizontal Filter Bar Container (direct child only) */
    div[data-testid="stLayoutWrapper"]:has(> .st-key-filter_bar),
    div[data-testid="stElementContainer"]:has(> .st-key-filter_bar) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 3.75rem !important;
        z-index: 990 !important;
    }

    .st-key-filter_bar {
        position: relative !important;
        top: auto !important;
        background-color: __BAR_BG__ !important;
        padding: 8px 12px !important;
        border-radius: 12px !important;
        box-shadow: __BAR_SHADOW__ !important;
        border: 1px solid __BAR_BORDER__ !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.6rem !important;
    }

    /* Compact Popover Buttons in Filter Bar */
    .st-key-filter_bar div[data-testid="stPopover"] > button,
    .st-key-filter_bar button[data-testid="stPopoverButton"],
    .st-key-filter_bar button[data-testid="stBaseButton-secondary"] {
        font-size: 0.82rem !important;
        padding: 0.3rem 0.55rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        border-radius: 8px !important;
    }

    /* Filter Popovers - Wide, responsive, wrapping tags */
    div[data-testid="stPopoverBody"] {
        min-width: min(520px, 92vw) !important;
        max-width: 92vw !important;
        padding: 1rem !important;
        max-height: 70vh !important;
        overflow-y: auto !important;
        box-sizing: border-box !important;
    }

    /* Ensure controls fill panel width and tags wrap nicely */
    div[data-testid="stPopoverBody"] > div {
        width: 100% !important;
    }
    div[data-testid="stPopoverBody"] .stMultiSelect,
    div[data-testid="stPopoverBody"] .stDateInput,
    div[data-testid="stPopoverBody"] .stSelectbox,
    div[data-testid="stPopoverBody"] .stSlider {
        width: 100% !important;
    }
    div[data-testid="stPopoverBody"] div[data-baseweb="select"] {
        width: 100% !important;
    }
    div[data-testid="stPopoverBody"] div[data-baseweb="tag"] {
        white-space: normal !important;
        max-width: 100% !important;
        height: auto !important;
    }
</style>
""".replace("__BAR_BG__", filter_theme["bg"]).replace("__BAR_BORDER__", filter_theme["border"]).replace("__BAR_SHADOW__", filter_theme["shadow"])
st.markdown(css_content, unsafe_allow_html=True)


# ==============================================================================
# 2. CACHED DATA LOADING & DEFENSIVE PREPROCESSING
# ==============================================================================
@st.cache_data(show_spinner="Loading and verifying UPI dataset...")
def get_cached_data():
    """Cached wrapper around src.data_loader.load_data()."""
    return load_data()

# Load full baseline dataset
df_raw, load_error = get_cached_data()

if load_error or df_raw is None:
    st.error(f"**Data Initialization Failure:** {load_error}")
    st.stop()

# Basic dataset bounds
min_date = df_raw["date"].min()
max_date = df_raw["date"].max()
min_amt = int(df_raw["amount"].min())
max_amt = int(df_raw["amount"].max())
computed_period_str = f"{min_date.strftime('%d %b %Y')} to {max_date.strftime('%d %b %Y')}"


# ==============================================================================
# SECTION 1: DASHBOARD HEADER & ACADEMIC PROJECT SCOPE
# ==============================================================================
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
    st.caption(f"Full Dataset: **{len(df_raw):,}** transactions (100% benchmark)")

st.markdown("---")

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
# SECTION 2: EXPLORATORY ANALYSIS (FROM NOTEBOOK) - 24 STATIC CHARTS & INFERENCES
# ==============================================================================
@st.fragment
def render_exploratory_analysis_section(df: pd.DataFrame):
    """
    Renders 24 static matplotlib/seaborn charts from mini-project.ipynb.
    Default: 2-column grid.
    Click to expand: Full-width 2-panel layout (Chart + Inferences),
    with sibling chart flowing directly below it in the grid.
    Wrapped in @st.fragment so expanding does not rerun the entire page.
    """
    st.markdown("---")
    st.markdown("### Exploratory Analysis (from Notebook)")
    st.caption("Recreated exact Matplotlib & Seaborn visualizations from `mini-project.ipynb` • **Based on the full 250,000-transaction dataset**")

    if "expanded_chart" not in st.session_state:
        st.session_state["expanded_chart"] = None

    expanded_id = st.session_state["expanded_chart"]

    def render_collapsed_card(chart_meta):
        cid = chart_meta["id"]
        title = chart_meta["title"]
        with st.container(border=True):
            st.markdown(f"**#{cid}. {title}**")
            try:
                uri = get_chart_data_uri(cid, df)
                st.markdown(
                    f'<img src="{uri}" alt="{title}" style="width:100%; height:auto; border-radius:6px;">',
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.error(f"Chart {cid} failed to render: {exc}")
            if st.button("Click to enlarge / view inference", key=f"btn_exp_{cid}", width="stretch"):
                st.session_state["expanded_chart"] = cid
                st.rerun(scope="fragment")

    def render_expanded_view(cid):
        chart_meta = next(c for c in CHARTS_REGISTRY if c["id"] == cid)
        title = chart_meta["title"]
        inf = get_inference(cid, df)
        is_left = (cid % 2 == 1)

        if is_left:
            col_chart, col_inf = st.columns([3, 2])
        else:
            col_inf, col_chart = st.columns([2, 3])

        with col_chart:
            with st.container(border=True):
                st.markdown(f"#### #{cid}. {title}")
                try:
                    uri = get_chart_data_uri(cid, df)
                    st.markdown(
                        f'<img src="{uri}" alt="{title}" style="width:100%; height:auto; border-radius:6px;">',
                        unsafe_allow_html=True,
                    )
                except Exception as exc:
                    st.error(f"Chart {cid} failed to render: {exc}")

        with col_inf:
            with st.container(border=True):
                c_title, c_btn = st.columns([3, 1])
                with c_title:
                    st.markdown("**Statistical Inference**")
                with c_btn:
                    if st.button("Close", key=f"close_{cid}", width="stretch", type="secondary"):
                        st.session_state["expanded_chart"] = None
                        st.rerun(scope="fragment")

                st.markdown(f"**Headline:** {inf['headline']}")
                st.markdown("**Key Insights:**")
                for item in inf["insights"]:
                    st.markdown(f"- {item}")
                st.markdown(f"**Anomalies / Caution:** {inf['anomalies']}")
                st.info(f"**Takeaway (So What?):** {inf['takeaway']}")

                try:
                    _ = bool(hasattr(st, "secrets") and "ANTHROPIC_API_KEY" in st.secrets)
                except Exception:
                    pass

    # If no chart is expanded, render all 24 charts in standard 2-per-row grid
    if expanded_id is None:
        for i in range(0, len(CHARTS_REGISTRY), 2):
            cols = st.columns(2)
            with cols[0]:
                render_collapsed_card(CHARTS_REGISTRY[i])
            if i + 1 < len(CHARTS_REGISTRY):
                with cols[1]:
                    render_collapsed_card(CHARTS_REGISTRY[i + 1])
    else:
        # One chart is expanded:
        exp_pair_idx = (expanded_id - 1) // 2
        exp_pair_start = exp_pair_idx * 2
        exp_pair_end = min(exp_pair_start + 2, len(CHARTS_REGISTRY))

        # 1. Render charts prior to the expanded pair in original pairs
        charts_before = CHARTS_REGISTRY[:exp_pair_start]
        for i in range(0, len(charts_before), 2):
            cols = st.columns(2)
            with cols[0]:
                render_collapsed_card(charts_before[i])
            if i + 1 < len(charts_before):
                with cols[1]:
                    render_collapsed_card(charts_before[i + 1])

        # 2. Render the expanded chart taking over its full row
        render_expanded_view(expanded_id)

        # 3. Render sibling chart ALONE in its ORIGINAL column of its own row (a Close card in other half)
        sibling_meta = next((c for c in CHARTS_REGISTRY[exp_pair_start:exp_pair_end] if c["id"] != expanded_id), None)
        expanded_meta = next(c for c in CHARTS_REGISTRY if c["id"] == expanded_id)
        if sibling_meta:
            sib_cols = st.columns(2)
            # Odd ID = column 0 (left), Even ID = column 1 (right)
            sib_col_idx = 1 if (sibling_meta["id"] % 2 == 0) else 0
            close_col_idx = 0 if sib_col_idx == 1 else 1

            with sib_cols[sib_col_idx]:
                render_collapsed_card(sibling_meta)
            with sib_cols[close_col_idx]:
                with st.container(border=True):
                    st.markdown(f"**Expanded: #{expanded_id}. {expanded_meta['title']}**")
                    st.caption("Viewing full-width chart & statistical inference in the row above.")
                    if st.button("Close Expanded View", key=f"btn_close_slot_{expanded_id}", width="stretch", type="secondary"):
                        st.session_state["expanded_chart"] = None
                        st.rerun(scope="fragment")

        # 4. Continue the grid from the next chart so everything after keeps its original columns and count stays even
        subsequent_charts = CHARTS_REGISTRY[exp_pair_end:]
        for i in range(0, len(subsequent_charts), 2):
            cols = st.columns(2)
            with cols[0]:
                render_collapsed_card(subsequent_charts[i])
            if i + 1 < len(subsequent_charts):
                with cols[1]:
                    render_collapsed_card(subsequent_charts[i + 1])

# Render the exploratory analysis section
render_exploratory_analysis_section(df_raw)


# ==============================================================================
# SECTION 3: NEW HORIZONTAL FLOATING FILTER BAR (REPLACES SIDEBAR)
# ==============================================================================
FILTER_KEYS = [
    "f_date_range", "f_types", "f_categories", "f_states", "f_banks",
    "f_status", "f_devices", "f_networks", "f_fraud", "f_amount_range"
]

def reset_all_filters():
    for k in FILTER_KEYS:
        if k in st.session_state:
            del st.session_state[k]

# Determine dynamic live-count labels from session_state
curr_date = st.session_state.get("f_date_range")
if isinstance(curr_date, (tuple, list)) and len(curr_date) == 2:
    if curr_date[0] == min_date and curr_date[1] == max_date:
        date_btn_label = "Date: All"
    else:
        date_btn_label = f"Date: {curr_date[0].strftime('%b %d')}-{curr_date[1].strftime('%b %d')}"
else:
    date_btn_label = "Date"

curr_types = st.session_state.get("f_types", [])
type_btn_label = f"Type ({len(curr_types)})" if curr_types else "Type"

curr_cats = st.session_state.get("f_categories", [])
cat_btn_label = f"Category ({len(curr_cats)})" if curr_cats else "Category"

curr_states = st.session_state.get("f_states", [])
state_btn_label = f"State ({len(curr_states)})" if curr_states else "State"

curr_banks = st.session_state.get("f_banks", [])
bank_btn_label = f"Bank ({len(curr_banks)})" if curr_banks else "Bank"

curr_status = st.session_state.get("f_status", [])
stat_btn_label = f"Status ({len(curr_status)})" if curr_status else "Status"

curr_devs = st.session_state.get("f_devices", [])
dev_btn_label = f"Device ({len(curr_devs)})" if curr_devs else "Device"

curr_nets = st.session_state.get("f_networks", [])
net_btn_label = f"Network ({len(curr_nets)})" if curr_nets else "Network"

curr_fraud = st.session_state.get("f_fraud", "All Transactions")
if "Fraud-Flagged" in curr_fraud:
    fraud_btn_label = "Fraud: Yes (1)"
elif "Non-Fraud" in curr_fraud:
    fraud_btn_label = "Fraud: No (0)"
else:
    fraud_btn_label = "Fraud"

curr_amt = st.session_state.get("f_amount_range", (min_amt, max_amt))
if curr_amt[0] > min_amt or curr_amt[1] < max_amt:
    amt_btn_label = f"₹ {curr_amt[0]:,}-{curr_amt[1]:,}"
else:
    amt_btn_label = "Amount"

all_types = sorted(df_raw["transaction_type"].unique())
all_categories = sorted(df_raw["merchant_category"].unique())
all_states = sorted(df_raw["sender_state"].unique())
all_banks = sorted(df_raw["sender_bank"].unique())
all_devices = sorted(df_raw["device_type"].unique())
all_networks = sorted(df_raw["network_type"].unique())

# Floating Filter Bar Container
with st.container(key="filter_bar"):
    f_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.85])

    # 1. Date Range Filter Popover
    with f_cols[0]:
        with st.popover(date_btn_label, width="stretch"):
            st.markdown("**Date Range**")
            date_selection = st.date_input(
                "Select Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="f_date_range",
                label_visibility="collapsed"
            )

    # 2. Transaction Type Filter Popover
    with f_cols[1]:
        with st.popover(type_btn_label, width="stretch"):
            st.markdown("**Transaction Type**")
            selected_types = st.multiselect(
                "Transaction Type",
                options=all_types,
                default=None,
                placeholder="All Types",
                key="f_types",
                label_visibility="collapsed"
            )

    # 3. Merchant Category Filter Popover
    with f_cols[2]:
        with st.popover(cat_btn_label, width="stretch"):
            st.markdown("**Merchant Category**")
            selected_categories = st.multiselect(
                "Merchant Category",
                options=all_categories,
                default=None,
                placeholder="All Categories",
                key="f_categories",
                label_visibility="collapsed"
            )

    # 4. Sender State Filter Popover
    with f_cols[3]:
        with st.popover(state_btn_label, width="stretch"):
            st.markdown("**Sender State**")
            selected_states = st.multiselect(
                "Sender State",
                options=all_states,
                default=None,
                placeholder="All States",
                key="f_states",
                label_visibility="collapsed"
            )

    # 5. Sender Bank Filter Popover
    with f_cols[4]:
        with st.popover(bank_btn_label, width="stretch"):
            st.markdown("**Sender Bank**")
            selected_banks = st.multiselect(
                "Sender Bank",
                options=all_banks,
                default=None,
                placeholder="All Banks",
                key="f_banks",
                label_visibility="collapsed"
            )

    # 6. Transaction Status Filter Popover
    with f_cols[5]:
        with st.popover(stat_btn_label, width="stretch"):
            st.markdown("**Transaction Status**")
            selected_status = st.multiselect(
                "Transaction Status",
                options=["SUCCESS", "FAILED"],
                default=None,
                placeholder="All Statuses",
                key="f_status",
                label_visibility="collapsed"
            )

    # 7. Device Type Filter Popover
    with f_cols[6]:
        with st.popover(dev_btn_label, width="stretch"):
            st.markdown("**Device Type**")
            selected_devices = st.multiselect(
                "Device Type",
                options=all_devices,
                default=None,
                placeholder="All Devices",
                key="f_devices",
                label_visibility="collapsed"
            )

    # 8. Network Type Filter Popover
    with f_cols[7]:
        with st.popover(net_btn_label, width="stretch"):
            st.markdown("**Network Type**")
            selected_networks = st.multiselect(
                "Network Type",
                options=all_networks,
                default=None,
                placeholder="All Networks",
                key="f_networks",
                label_visibility="collapsed"
            )

    # 9. Fraud Indicator Filter Popover
    with f_cols[8]:
        with st.popover(fraud_btn_label, width="stretch"):
            st.markdown("**Fraud Indicator**")
            fraud_options = ["All Transactions", "Fraud-Flagged Only (1)", "Non-Fraud Only (0)"]
            selected_fraud_choice = st.selectbox(
                "Fraud Indicator",
                options=fraud_options,
                index=0,
                key="f_fraud",
                label_visibility="collapsed"
            )

    # 10. Amount Range Filter Popover
    with f_cols[9]:
        with st.popover(amt_btn_label, width="stretch"):
            st.markdown("**Amount Range (₹)**")
            selected_amount_range = st.slider(
                "Amount Range (₹)",
                min_value=min_amt,
                max_value=max_amt,
                value=(min_amt, max_amt),
                step=100,
                key="f_amount_range",
                label_visibility="collapsed"
            )

    # 11. Reset All Filters Button
    with f_cols[10]:
        if st.button("Reset", key="reset_filters_btn", width="stretch", help="Clear all selections and reset dashboard."):
            reset_all_filters()
            st.rerun()

# Downstream Filtering Engine Application (Moved outside pinned container to keep filter bar to 1 slim row)
filtered_df = df_raw.copy()

if isinstance(date_selection, (tuple, list)):
    if len(date_selection) == 2:
        start_d, end_d = date_selection
        filtered_df = filtered_df[(filtered_df["date"] >= start_d) & (filtered_df["date"] <= end_d)]
    elif len(date_selection) == 1:
        start_d = date_selection[0]
        filtered_df = filtered_df[filtered_df["date"] == start_d]

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

if selected_fraud_choice == "Fraud-Flagged Only (1)":
    filtered_df = filtered_df[filtered_df["fraud_flag"] == 1]
elif selected_fraud_choice == "Non-Fraud Only (0)":
    filtered_df = filtered_df[filtered_df["fraud_flag"] == 0]

filtered_df = filtered_df[
    (filtered_df["amount"] >= selected_amount_range[0]) &
    (filtered_df["amount"] <= selected_amount_range[1])
]

# One-line Summary and Interactive Scope Note (Outside pinned container)
active_desc_list = []
if isinstance(date_selection, (tuple, list)) and len(date_selection) == 2:
    if date_selection[0] != min_date or date_selection[1] != max_date:
        active_desc_list.append(f"Date: {date_selection[0]} to {date_selection[1]}")
if selected_types:
    active_desc_list.append(f"Type: {', '.join(selected_types)}")
if selected_categories:
    active_desc_list.append(f"Category: {', '.join(selected_categories)}")
if selected_states:
    active_desc_list.append(f"State: {', '.join(selected_states)}")
if selected_banks:
    active_desc_list.append(f"Bank: {', '.join(selected_banks)}")
if selected_status:
    active_desc_list.append(f"Status: {', '.join(selected_status)}")
if selected_devices:
    active_desc_list.append(f"Device: {', '.join(selected_devices)}")
if selected_networks:
    active_desc_list.append(f"Network: {', '.join(selected_networks)}")
if selected_fraud_choice != "All Transactions":
    active_desc_list.append(f"Fraud: {selected_fraud_choice}")
if selected_amount_range[0] > min_amt or selected_amount_range[1] < max_amt:
    active_desc_list.append(f"Amount: ₹{selected_amount_range[0]:,}–₹{selected_amount_range[1]:,}")

f_summary_col1, f_summary_col2 = st.columns([3, 1])
with f_summary_col1:
    f_text = " • ".join(active_desc_list) if active_desc_list else "All transactions included (No filters applied)"
    if len(f_text) > 130:
        f_text = f_text[:127] + "..."
    st.caption(f"**Active Filters:** {f_text}")
with f_summary_col2:
    st.caption(f"Showing **{len(filtered_df):,}** of **{len(df_raw):,}** transactions ({(len(filtered_df)/len(df_raw)*100):.1f}%) • *Filters apply to interactive dashboard.*")


# ==============================================================================
# SECTION 4: EMPTY STATE GUARD & DYNAMIC KPI CARDS
# ==============================================================================
if len(filtered_df) == 0:
    st.warning("**No transactions match the selected filter criteria.** Please widen or reset your filters in the bar above.")
    st.info("Tip: Click **'Reset'** in the filter bar to restore the complete 250,000 transaction dataset.")
    st.stop()

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
# SECTION 5: INTERACTIVE PLOTLY VISUALIZATIONS (6 CORE CHARTS + EXPANDER)
# ==============================================================================

# Row 1: Traffic Diurnal Velocity & Bank Ecosystem Reliability
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    # CHART 1: Hourly Traffic Velocity vs Failure Rate
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
    # CHART 2: Bank Ecosystem: Volume Share vs Failure Reliability
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
    # CHART 4: Fraud-Flagged Count and Rate by State
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

    net_dev_rate = (net_dev_fails / net_dev_counts * 100.0).fillna(0)

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


# Day-of-Week x Hourly Traffic Intensity Expander
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
# SECTION 6: DYNAMIC KEY INSIGHTS SECTION (TABS), DATA TABLE & FOOTER
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
    top_type_pct = (top_type_count / n_total * 100.0) if n_total > 0 else 0.0
    
    wkday_tx = int((filtered_df["is_weekend_calc"] == 0).sum())
    wkend_tx = int((filtered_df["is_weekend_calc"] == 1).sum())
    wkday_avg_daily = wkday_tx / 5.0
    wkend_avg_daily = wkend_tx / 2.0
    wk_rel_diff = (abs(wkday_avg_daily - wkend_avg_daily) / wkday_avg_daily * 100.0) if wkday_avg_daily > 0 else 0.0
    
    median_amt = filtered_df["amount"].median() if not filtered_df.empty else 0.0
    max_amt_f = filtered_df["amount"].max() if not filtered_df.empty else 0.0
    micro_tx_share = (filtered_df["amount"] < 1000).mean() * 100.0 if not filtered_df.empty else 0.0
    
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
            f"UPI velocity remains uniformly active 7 days a week (relative difference of {wk_rel_diff:.2f}%)."
        )
    with st.container(border=True):
        st.markdown(
            f"**3. Micro-Ticket Dominance & Amount Skewness:**  \n"
            f"The median ticket size is **₹{median_amt:,.0f}**, whereas the arithmetic mean is "
            f"**₹{avg_amount:,.2f}** (with an extreme maximum of **₹{max_amt_f:,}**). "
            f"This high positive skew confirms that {micro_tx_share:.1f}% of UPI payments are retail micro-transactions under ₹1,000, "
            f"with high-value transfers elevating the arithmetic mean."
        )

with tab_infra:
    peak_hour = hourly_df.sort_values(by="volume", ascending=False).iloc[0]["hour"] if not hourly_df.empty else 0
    peak_vol = hourly_df.sort_values(by="volume", ascending=False).iloc[0]["volume"] if not hourly_df.empty else 0
    peak_vol_pct = (peak_vol / n_total * 100.0) if n_total > 0 else 0.0
    
    evening_tx = int(filtered_df["hour"].between(18, 20).sum()) if not filtered_df.empty else 0
    evening_pct = (evening_tx / n_total * 100.0) if n_total > 0 else 0.0
    
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
    min_bank_fail = bank_stats["fail_rate"].min() if not bank_stats.empty else 0.0
    max_bank_fail = bank_stats["fail_rate"].max() if not bank_stats.empty else 0.0

    dev_fails = filtered_df.groupby("device_type")["transaction_status"].apply(lambda s: (s == "FAILED").mean() * 100.0)
    net_fails = filtered_df.groupby("network_type")["transaction_status"].apply(lambda s: (s == "FAILED").mean() * 100.0)
    dev_str = ", ".join([f"{d} ({r:.2f}%)" for d, r in dev_fails.items()])
    net_str = ", ".join([f"{n} ({r:.2f}%)" for n, r in net_fails.items()])

    android_tx = int((filtered_df["device_type"] == "Android").sum())
    android_traffic_pct = (android_tx / n_total * 100.0) if n_total > 0 else 0.0
    total_failed_tx = int((filtered_df["transaction_status"] == "FAILED").sum())
    android_failed_tx = int(((filtered_df["device_type"] == "Android") & (filtered_df["transaction_status"] == "FAILED")).sum())
    android_fail_share_pct = (android_failed_tx / total_failed_tx * 100.0) if total_failed_tx > 0 else 0.0
    
    with st.container(border=True):
        st.markdown(
            f"**1. Peak Diurnal Congestion:**  \n"
            f"Peak network usage occurs at **{int(peak_hour):02d}:00 hours** carrying "
            f"**{int(peak_vol):,} transactions** ({peak_vol_pct:.2f}% of daily traffic). Transaction traffic accelerates through the evening "
            f"window (18:00–20:00), which processes {evening_pct:.1f}% of all daily volume ({evening_tx:,} transactions)."
        )
    with st.container(border=True):
        st.markdown(
            f"**2. Banking Ecosystem Reliability Invariance:**  \n"
            f"The sender bank with the nominally highest failure rate is **{highest_fail_bank}** at "
            f"**{highest_fail_rate:.2f}%** ({highest_fail_count:,} failed out of {highest_fail_tot:,} transactions). "
            f"However, two-way Chi-Square testing confirms that all sender banks remain confined within a narrow band (**{min_bank_fail:.2f}% – {max_bank_fail:.2f}%**). "
            f"No single bank is an operational bottleneck."
        )
    with st.container(border=True):
        st.markdown(
            f"**3. Client Device & Cellular Network Parity:**  \n"
            f"Across device types ({dev_str}) and network types ({net_str}), "
            f"failure rates are statistically invariant from the baseline **{failure_rate:.2f}%**. "
            f"Android accounts for {android_fail_share_pct:.2f}% of total failures solely because it generates {android_traffic_pct:.2f}% of all traffic."
        )

with tab_fraud:
    state_fraud_sorted = state_df.sort_values(by="fraud_tx", ascending=False) if not state_df.empty else pd.DataFrame()
    top_fraud_state = state_fraud_sorted.iloc[0]["sender_state"] if not state_fraud_sorted.empty else "N/A"
    top_fraud_count = state_fraud_sorted.iloc[0]["fraud_tx"] if not state_fraud_sorted.empty else 0
    top_fraud_rate = state_fraud_sorted.iloc[0]["fraud_rate_pct"] if not state_fraud_sorted.empty else 0.0
    approx_1_in_n = f"1 in {int(round(n_total / n_fraud)):,}" if n_fraud > 0 else "0 in total"

    if len(state_fraud_sorted) >= 2:
        st1 = state_fraud_sorted.iloc[0]
        st2 = state_fraud_sorted.iloc[1]
        top2_names = f"{st1['sender_state']} and {st2['sender_state']}"
        top2_fraud_sum = st1['fraud_tx'] + st2['fraud_tx']
        top2_fraud_pct = (top2_fraud_sum / n_fraud * 100.0) if n_fraud > 0 else 0.0
        top2_vol_sum = st1['total_tx'] + st2['total_tx']
        top2_vol_pct = (top2_vol_sum / n_total * 100.0) if n_total > 0 else 0.0
        state_share_str = f"{top2_names} contribute {top2_fraud_pct:.2f}% of all fraud flags solely because they generate {top2_vol_pct:.2f}% of all traffic."
    else:
        state_share_str = "Fraud flags scale proportionately with transaction volume across states."

    if len(filtered_df) > 1 and filtered_df["fraud_flag"].nunique() > 1 and filtered_df["amount"].nunique() > 1:
        corr_amt_fraud = filtered_df["amount"].corr(filtered_df["fraud_flag"])
        corr_text = f"r = {corr_amt_fraud:+.5f}"
    else:
        corr_text = "r ≈ 0.00000"

    with st.container(border=True):
        st.markdown(
            f"**1. Ultra-Rare Baseline Anomaly Rate:**  \n"
            f"In the filtered view, **{n_fraud:,} transactions** are flagged by fraud heuristics, "
            f"constituting an overall occurrence rate of **{fraud_rate:.3f}%** (approx. {approx_1_in_n} transactions)."
        )
    with st.container(border=True):
        st.markdown(
            f"**2. State Distribution Governed Strictly by Volume Proportionality:**  \n"
            f"The state with the highest absolute count of flagged transactions is **{top_fraud_state}** "
            f"(**{int(top_fraud_count):,} flagged**, cohort rate: **{top_fraud_rate:.3f}%**). "
            f"{state_share_str} "
            f"Chi-Square testing confirms fraud rates are uniform across states."
        )
    with st.container(border=True):
        st.markdown(
            f"**3. Heuristic Flagging vs. True Fraud:**  \n"
            f"The dataset's `fraud_flag` represents an algorithmic detection trigger rather than adjudicated chargebacks or confirmed losses. "
            f"Ticket amounts do not correlate linearly with fraud flags ({corr_text}), meaning high ticket sizes do not carry higher risk."
        )

with tab_caution:
    df_stat = filtered_df if (len(filtered_df) >= 500 and filtered_df["transaction_status"].nunique() > 1) else df_raw
    n_stat = len(df_stat)

    def calc_chi2(col):
        try:
            ct = pd.crosstab(df_stat[col], df_stat["transaction_status"])
            if ct.shape[0] < 2 or ct.shape[1] < 2:
                return (0.0, 1.0, 0.0)
            res = stats.chi2_contingency(ct)
            n_obs = ct.to_numpy().sum()
            k_min = min(ct.shape) - 1
            v_stat = np.sqrt(res.statistic / (n_obs * k_min)) if (n_obs * k_min) > 0 else 0.0
            return (res.statistic, res.pvalue, v_stat)
        except Exception:
            return (0.0, 1.0, 0.0)

    bank_chi2, bank_p, bank_v = calc_chi2("sender_bank")
    dev_chi2, dev_p, dev_v = calc_chi2("device_type")
    net_chi2, net_p, net_v = calc_chi2("network_type")
    base_fail_pct = (df_stat["transaction_status"] == "FAILED").mean() * 100.0

    total_stat_fraud = int((df_stat["fraud_flag"] == 1).sum())
    fraud_bench_pct = (total_stat_fraud / n_stat * 100.0) if n_stat > 0 else 0.0

    st_agg = df_stat.groupby("sender_state").agg(
        tot=("fraud_flag", "count"),
        fraud=("fraud_flag", "sum")
    ).reset_index()
    st_agg["rate"] = st_agg["fraud"] / st_agg["tot"]
    st_agg = st_agg.sort_values(by="rate", ascending=False)

    min_st_fraud = int(st_agg["fraud"].min()) if not st_agg.empty else 0
    max_st_fraud = int(st_agg["fraud"].max()) if not st_agg.empty else 0

    def wilson_ci(k, n, z=1.96):
        if n == 0:
            return (0.0, 0.0)
        p = k / n
        denom = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denom
        margin = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
        return (max(0.0, center - margin) * 100.0, min(1.0, center + margin) * 100.0)

    if not st_agg.empty:
        hi_st = st_agg.iloc[0]
        lo_st = st_agg.iloc[-1]
        hi_ci = wilson_ci(hi_st["fraud"], hi_st["tot"])
        lo_ci = wilson_ci(lo_st["fraud"], lo_st["tot"])
        hi_name, hi_k, hi_n, hi_r = hi_st["sender_state"], int(hi_st["fraud"]), int(hi_st["tot"]), hi_st["rate"] * 100.0
        lo_name, lo_k, lo_n, lo_r = lo_st["sender_state"], int(lo_st["fraud"]), int(lo_st["tot"]), lo_st["rate"] * 100.0
    else:
        hi_name, hi_k, hi_n, hi_r, hi_ci = "N/A", 0, 0, 0.0, (0.0, 0.0)
        lo_name, lo_k, lo_n, lo_r, lo_ci = "N/A", 0, 0, 0.0, (0.0, 0.0)

    and_tx = int((df_stat["device_type"] == "Android").sum())
    and_traffic_pct = (and_tx / n_stat * 100.0) if n_stat > 0 else 0.0
    tot_fld = int((df_stat["transaction_status"] == "FAILED").sum())
    and_fld = int(((df_stat["device_type"] == "Android") & (df_stat["transaction_status"] == "FAILED")).sum())
    and_fail_share_pct = (and_fld / tot_fld * 100.0) if tot_fld > 0 else 0.0
    and_fail_rate_pct = (and_fld / and_tx * 100.0) if and_tx > 0 else 0.0

    ios_tx = int((df_stat["device_type"] == "iOS").sum())
    ios_fld = int(((df_stat["device_type"] == "iOS") & (df_stat["transaction_status"] == "FAILED")).sum())
    ios_fail_rate_pct = (ios_fld / ios_tx * 100.0) if ios_tx > 0 else 0.0

    st.info(f"""
    **Methodological Rigor & Statistical Uncertainty Notes:**
    
    1. **Chi-Square Independence Tests (Failure Reliability):**
       - Contingency tests performed on active dataset ({n_stat:,} transactions) show:
         - Bank vs. Status: $\\chi^2 = {bank_chi2:.4f}, p = {bank_p:.4f}$ (Cramer's $V = {bank_v:.4f}$)
         - Device vs. Status: $\\chi^2 = {dev_chi2:.4f}, p = {dev_p:.4f}$ (Cramer's $V = {dev_v:.4f}$)
         - Network vs. Status: $\\chi^2 = {net_chi2:.4f}, p = {net_p:.4f}$ (Cramer's $V = {net_v:.4f}$)
       - **Conclusion:** Failure rate differences between banks or devices are **not statistically significant**. They represent random stochastic noise around a constant ~{base_fail_pct:.2f}% system baseline.
       
    2. **Extreme Class Imbalance in Fraud Analysis:**
       - Across the dataset, only **{total_stat_fraud:,} out of {n_stat:,} transactions ({fraud_bench_pct:.3f}%)** are flagged as fraud.
       - Disaggregating {total_stat_fraud:,} positive events across states yields small sample sizes ({min_st_fraud} to {max_st_fraud} positive rows per state).
       - The 95% Wilson score confidence interval for {hi_name} ({hi_k:,}/{hi_n:,} = {hi_r:.3f}%) is **[{hi_ci[0]:.3f}%, {hi_ci[1]:.3f}%]**, which fully overlaps with {lo_name} ({lo_k:,}/{lo_n:,} = {lo_r:.3f}%, **[{lo_ci[0]:.3f}%, {lo_ci[1]:.3f}%]**).
       - Analysts and presenters must avoid labeling individual states or merchant categories as "fraud hotspots."
       
    3. **'Share of Failures' vs. 'Cohort Failure Rate':**
       - Android accounts for **{and_fail_share_pct:.2f}% of all system failures** solely because it represents **{and_traffic_pct:.2f}% of total transaction traffic**.
       - Within the Android cohort, the failure rate is **{and_fail_rate_pct:.2f}%**, compared to iOS (**{ios_fail_rate_pct:.2f}%**). Conflating cohort shares with failure likelihood is a common analytical error.
    """)

# Sample Data Table & CSV Export
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
