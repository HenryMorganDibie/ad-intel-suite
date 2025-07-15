import pandas as pd
from prophet import Prophet
from prophet.diagnostics import performance_metrics
from datetime import datetime
import os

# Paths
input_path = "data/Dataset - Sheet1.csv"
output_forecast_path = "reports/forecast_ecpm.csv"
output_anomalies_path = "reports/anomaly_summary.csv"

# Ensure output folder exists
os.makedirs("reports", exist_ok=True)

# Load actuals
df = pd.read_csv(input_path)
df.columns = df.columns.str.strip()

# Convert date
df["Date"] = pd.to_datetime(df["Date"])

# Add CTR if not already
if "CTR" not in df.columns and "Clicks" in df.columns and "Impressions" in df.columns:
    df["CTR"] = df["Clicks"] / df["Impressions"]

# Metrics to forecast
metrics = {
    "eCPM": "Observed eCPM (USD)",
    "CTR": "CTR",
    "Clicks": "Clicks",
    "Impressions": "Impressions",
    "Revenue": "Est. earnings (USD)"
}

all_forecasts = []
all_anomalies = []

# Loop through each metric
for metric_name, col in metrics.items():
    print(f"🔮 Forecasting + detecting anomalies for: {metric_name}")

    # Prepare data
    clean_data = df[["Date", col]].dropna().copy()
    clean_data = clean_data.rename(columns={"Date": "ds", col: "y"})
    clean_data["y"] = clean_data["y"].ffill()

    # Train Prophet
    model = Prophet(daily_seasonality=True)
    model.fit(clean_data)

    # Create future dataframe
    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)

    # Merge with actuals
    forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].merge(clean_data, on="ds", how="left")

    # Detect anomalies
    forecast_df["Anomaly"] = "Normal"
    forecast_df.loc[forecast_df["y"] > forecast_df["yhat_upper"], "Anomaly"] = "Positive"
    forecast_df.loc[forecast_df["y"] < forecast_df["yhat_lower"], "Anomaly"] = "Negative"

    # Label metric
    forecast_df["Metric"] = metric_name

    # Append forecast for eCPM
    if metric_name == "eCPM":
        forecast_df.to_csv(output_forecast_path, index=False)

    # Extract anomalies
    anomalies = forecast_df[forecast_df["Anomaly"] != "Normal"].copy()
    anomalies["Anomaly Type"] = metric_name
    anomalies["Date"] = anomalies["ds"]

    # Add Country if available
    if "Country" in df.columns:
        anomalies = anomalies.merge(df[["Date", "Country"]].rename(columns={"Date": "ds"}), on="ds", how="left")

    all_anomalies.append(anomalies)

# Save all anomalies
if all_anomalies:
    result = pd.concat(all_anomalies, ignore_index=True)
    result.to_csv(output_anomalies_path, index=False)
    print("✅ All forecasts and anomalies generated!")
else:
    print("🚫 No anomalies detected.")
