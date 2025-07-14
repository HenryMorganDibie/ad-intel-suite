import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
import os

# 🧭 Load datasets
actuals_path = 'data/Dataset - Sheet1.csv'
forecast_path = 'reports/forecast_ecpm.csv'
anomaly_path = 'reports/anomaly_summary.csv'

required_files = [actuals_path, forecast_path]
for f in required_files:
    if not os.path.exists(f):
        st.error(f"🚫 Missing file: {f}")
        st.stop()

# 🧼 Load & clean actuals
actuals = pd.read_csv(actuals_path)
actuals.columns = actuals.columns.str.strip()

# Add CTR manually if not present
if 'CTR' not in actuals.columns and 'Clicks' in actuals.columns and 'Impressions' in actuals.columns:
    actuals['CTR'] = actuals['Clicks'] / actuals['Impressions']

forecast = pd.read_csv(forecast_path)
actuals['Date'] = pd.to_datetime(actuals['Date'])
forecast['ds'] = pd.to_datetime(forecast['ds'])

# 🔴 Load anomalies (if file exists)
if os.path.exists(anomaly_path):
    anomalies = pd.read_csv(anomaly_path)
    anomalies['Date'] = pd.to_datetime(anomalies['Date'])
else:
    anomalies = pd.DataFrame()

# 🎛️ Metric selector
metrics = {
    "eCPM": "Observed eCPM (USD)",
    "CTR": "CTR",
    "Clicks": "Clicks",
    "Impressions": "Impressions",
    "Revenue": "Est. earnings (USD)"
}
selected_metric = st.selectbox("📊 Select Metric", list(metrics.keys()))
metric_col = metrics[selected_metric]

# 🧽 Prepare data
actuals = actuals.rename(columns={"Date": "ds"})
forecast = forecast.rename(columns={"yhat": "Forecasted eCPM"})

# 🎯 Date range
min_date = actuals['ds'].min().date()
max_date = forecast['ds'].max().date()
date_range = st.slider("📅 Select date range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# 🔍 Filter actuals
filtered_actuals = actuals[(actuals['ds'].dt.date >= date_range[0]) & (actuals['ds'].dt.date <= date_range[1])]

# 📆 Previous period
period_days = (date_range[1] - date_range[0]).days + 1
prev_start = date_range[0] - timedelta(days=period_days)
prev_end = date_range[0] - timedelta(days=1)
previous_actuals = actuals[(actuals['ds'].dt.date >= prev_start) & (actuals['ds'].dt.date <= prev_end)]

# 📊 KPI Cards
def calc_pct_change(curr, prev):
    if prev == 0: return "N/A"
    return f"{((curr - prev) / prev) * 100:.1f}%"

col1, col2, col3 = st.columns(3)

# Special handling for CTR
if selected_metric == "CTR":
    ctr_curr = filtered_actuals['Clicks'].sum() / filtered_actuals['Impressions'].sum()
    ctr_prev = previous_actuals['Clicks'].sum() / previous_actuals['Impressions'].sum()
    col1.metric("Avg CTR", f"{ctr_curr:.2%}", calc_pct_change(ctr_curr, ctr_prev))
    col2.metric("Total Clicks", f"{filtered_actuals['Clicks'].sum():,.0f}")
    col3.metric("Total Impressions", f"{filtered_actuals['Impressions'].sum():,.0f}")
else:
    curr_avg = filtered_actuals[metric_col].mean()
    prev_avg = previous_actuals[metric_col].mean()
    col1.metric(f"Avg {selected_metric}", f"{curr_avg:.2f}", calc_pct_change(curr_avg, prev_avg))

    curr_total = filtered_actuals[metric_col].sum()
    prev_total = previous_actuals[metric_col].sum()
    col2.metric(f"Total {selected_metric}", f"{curr_total:,.0f}", calc_pct_change(curr_total, prev_total))

    col3.metric("Period", f"{period_days} days", f"vs. prev {period_days} days")

# 📈 Timeseries Chart
fig = px.line(filtered_actuals, x='ds', y=metric_col, title=f"📈 {selected_metric} Over Time", labels={'ds': 'Date', metric_col: selected_metric})

# 🔴 Overlay Anomalies
if not anomalies.empty and selected_metric in anomalies['Anomaly Type'].unique():
    anomaly_dates = anomalies[anomalies['Anomaly Type'] == selected_metric]['Date'].dt.date
    anomalies_filtered = filtered_actuals[filtered_actuals['ds'].dt.date.isin(anomaly_dates)]
    if not anomalies_filtered.empty:
        fig.add_scatter(
            x=anomalies_filtered['ds'],
            y=anomalies_filtered[metric_col],
            mode='markers',
            name='Anomalies',
            marker=dict(color='red', size=8, symbol='x')
        )

st.plotly_chart(fig, use_container_width=True)

# 📥 Forecast download
if selected_metric == "eCPM":
    st.download_button(
        label="📥 Download Forecast CSV",
        data=forecast.to_csv(index=False),
        file_name='forecast_ecpm.csv',
        mime='text/csv'
    )
