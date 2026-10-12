# Selection and Use of Tools and Technologies

## 1. Technological Stack and Library Inventory

The project environment is built on a modern Python scientific data stack. Package versions below reflect the exact environment installed on the development machine (verified via `importlib.metadata` under Python 3.12.9):

| Tool / Library | Installed Version | Architectural Role in Project |
| :--- | :--- | :--- |
| **Python** | `3.12.9` | Core runtime for data processing, statistical testing, and dashboard serving. |
| **pandas** | `3.0.2` | Tabular data manipulation, vectorised cleaning, multi-dimensional aggregations, and filtering. |
| **NumPy** | `2.4.4` | Numerical array operations and formatting custom hover arrays for visualizations. |
| **Streamlit** | `1.57.0` | Reactive web framework powering `app.py`, providing sidebar widgets, KPI cards, and layout control. |
| **Plotly** | `7.1.0` | Interactive charting suite (`graph_objects` and `express`) enabling zoom, hovercards, and dual-axis plots. |
| **JupyterLab / ipykernel** | `4.6.1` / `7.3.0` | Interactive notebook environment used for exploratory data analysis and code auditing (`mini-project.ipynb`). |
| **Matplotlib** | `3.11.1` | Static plotting library used during exploratory notebook analysis for initial distributions. |
| **Seaborn** | `0.13.2` | Statistical plotting library used in the notebook for univariate count plots and correlation heatmaps. |
| **scikit-learn** | `1.9.1` | Machine learning toolkit used in exploratory modeling (`LogisticRegression`, `train_test_split`). |
| **SciPy** | `1.18.0` | Statistical library used to compute Chi-Square independence tests ($\chi^2$) and Cramer's $V$ effect sizes. |

---

## 2. Why Streamlit and Plotly Suit This Project

For this university laboratory project, combining **Streamlit** and **Plotly** provides distinct technical advantages:

1. **Unified Pure-Python Workflow:** Keeping ingestion, statistical testing, and visualization entirely in Python avoids context-switching across different languages (e.g., JavaScript/HTML/CSS) or closed GUIs.
2. **Direct Code and Logic Reuse:** Data cleaning logic, aggregation routines, and derived temporal fields developed in the exploratory Jupyter notebook transferred directly into `app.py` with zero translation friction.
3. **Declarative Reactive Interactivity:** Streamlit generates multi-dimensional filter controls (`st.date_input`, `st.multiselect`, `st.slider`) that bind automatically to the filtering pipeline without manual event listeners or DOM manipulation.
4. **Rich Client-Side Interactivity:** Plotly provides built-in tooltips, zoom, pan, and trace toggling out of the box, allowing evaluators to inspect exact counts and percentages on hover.
5. **Rapid Prototyping and Free Reproducibility:** The stack is completely open-source and reproducible across student systems via `pip install -r requirements.txt`, avoiding proprietary software licenses.

---

## 3. Comparison with Alternative Dashboard Tools

The course deliverables mention **Power BI**, **Tableau Public**, and **Plotly Dash**. While each is powerful, they were not selected for deliberate reasons:

- **Microsoft Power BI:** Power BI offers enterprise governance, row-level security, and DAX modeling. However, it requires a proprietary Windows desktop application, relies on proprietary licenses for sharing, and conceals data transformations behind a visual interface rather than transparent, reproducible code.
- **Tableau Public:** Tableau excels at drag-and-drop aesthetics and geospatial rendering. However, Tableau Public requires publishing academic datasets to a public web server, lacks Git version control, and disconnects visual charts from Python's statistical testing libraries.
- **Plotly Dash:** While Dash provides granular client-side callback control and production multi-page scaling, its declarative HTML/React component trees and Flask callback architecture introduce excessive boilerplate for an exploratory 250,000-row dashboard.

---

## 4. Technical Constraints and Limitations of the Chosen Stack

While ideal for educational demonstration and exploratory analytics, the selected architecture has defined operational boundaries:

1. **Top-to-Bottom Script Re-execution:** Streamlit re-runs the script sequentially on each user interaction. Although `@st.cache_data` mitigates raw data reload overhead, multi-filter slicing still recalculates dynamically in memory.
2. **In-Memory Data Footprint:** pandas holds all 250,000 records in RAM (~30 MB). While fast locally, this architecture cannot handle production national UPI scale, which processes over 14 billion monthly transactions and requires distributed frameworks (e.g., Apache Spark, DuckDB, or streaming OLAP like ClickHouse).
3. **No Real-Time Event Streaming:** Streamlit is designed for batch exploratory analytics rather than live millisecond-level transaction streams or automated SLA incident alerting.

*Note: The dashboard is executed locally on the developer workstation via `streamlit run app.py` and does not rely on any hosted cloud service.*
