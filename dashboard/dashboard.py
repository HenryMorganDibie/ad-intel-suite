import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
import os

# 📂 File paths
actuals_path = 'data/Dataset - Sheet1.csv'
forecast_dir = 'reports'
anomaly_path = 'reports/anomaly_summary.csv'

# 🎯 Metrics config
metrics = {
    "eCPM": "Observed eCPM (USD)",
    "CTR": "CTR",
    "Clicks": "Clicks",
    "Impressions": "Impressions",
    "Revenue": "Est. earnings (USD)"
}

# 🧭 Load actuals
if not os.path.exists(actuals_path):
    st.error(f"❌ Missing file: {actuals_path}")
    st.stop()

actuals = pd.read_csv(actuals_path)
actuals.columns = actuals.columns.str.strip()
actuals['Date'] = pd.to_datetime(actuals['Date'])
actuals = actuals.rename(columns={"Date": "ds"})

# ➕ Compute CTR if missing
if 'CTR' not in actuals.columns and 'Clicks' in actuals.columns and 'Impressions' in actuals.columns:
    actuals['CTR'] = actuals['Clicks'] / actuals['Impressions']

# 🔴 Load anomalies
if os.path.exists(anomaly_path):
    anomalies = pd.read_csv(anomaly_path)
    anomalies['Date'] = pd.to_datetime(anomalies['Date'])
else:
    anomalies = pd.DataFrame()

# 🎛️ Metric selection
selected_metric = st.selectbox("📊 Select Metric", list(metrics.keys()))
metric_col = metrics[selected_metric]

# 📉 Load forecast
forecast_file = os.path.join(forecast_dir, f"forecast_{selected_metric.lower()}.csv")
if os.path.exists(forecast_file):
    forecast = pd.read_csv(forecast_file)
    forecast['ds'] = pd.to_datetime(forecast['ds'])
    if 'yhat' in forecast.columns:
        forecast = forecast.rename(columns={'yhat': 'Forecast'})
    elif 'Forecasted eCPM' in forecast.columns:
        forecast = forecast.rename(columns={'Forecasted eCPM': 'Forecast'})
else:
    forecast = pd.DataFrame()

# 📅 Date range slider
min_date = actuals['ds'].min().date()
max_date = max(actuals['ds'].max(), forecast['ds'].max() if not forecast.empty else actuals['ds'].max()).date()
date_range = st.slider("📅 Select date range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# 🔍 Filter actuals + forecast
filtered_actuals = actuals[(actuals['ds'].dt.date >= date_range[0]) & (actuals['ds'].dt.date <= date_range[1])]
filtered_forecast = forecast[(forecast['ds'].dt.date >= date_range[0]) & (forecast['ds'].dt.date <= date_range[1])]

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

if selected_metric == "CTR":
    curr_ctr = filtered_actuals['Clicks'].sum() / filtered_actuals['Impressions'].sum()
    prev_ctr = previous_actuals['Clicks'].sum() / previous_actuals['Impressions'].sum()
    col1.metric("Avg CTR", f"{curr_ctr:.2%}", calc_pct_change(curr_ctr, prev_ctr))
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

# 📈 Time series chart
fig = px.line(filtered_actuals, x='ds', y=metric_col, title=f"{selected_metric} Over Time", labels={'ds': 'Date', metric_col: selected_metric})

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

# 🔮 Overlay Forecast
if not forecast.empty:
    fig.add_scatter(
        x=filtered_forecast['ds'],
        y=filtered_forecast['Forecast'],
        mode='lines',
        name='Forecast',
        line=dict(dash='dot', color='orange')
    )

st.plotly_chart(fig, use_container_width=True)

# 📥 Download forecast
if not forecast.empty:
    st.download_button(
        label=f"📥 Download {selected_metric} Forecast CSV",
        data=forecast.to_csv(index=False),
        file_name=f"forecast_{selected_metric.lower()}.csv",
        mime='text/csv'
    )
