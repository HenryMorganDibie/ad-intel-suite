import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import os

# 📂 Load data
df = pd.read_csv('data/Dataset - Sheet1.csv')
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values('Date', inplace=True)

# 🧽 Clean data
df = df[['Date', 'Observed eCPM (USD)']].rename(columns={
    'Date': 'ds',
    'Observed eCPM (USD)': 'y'
})
df = df.dropna()

# 🧠 Initialize Prophet
model = Prophet(daily_seasonality=True)
model.fit(df)

# 📅 Forecast next 30 days
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# 📊 Plot forecast
fig = model.plot(forecast)
plt.title('📈 Forecasted Observed eCPM (Next 30 Days)')
plt.xlabel('Date')
plt.ylabel('eCPM (USD)')
plt.tight_layout()
plt.show()

# 🔍 Optional: trend + seasonality components
model.plot_components(forecast)
plt.tight_layout()
plt.show()

# 💾 Save forecast to CSV
forecast_out = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
forecast_out.to_csv('reports/forecast_ecpm.csv', index=False)
print("✅ Forecast saved to reports/forecast_ecpm.csv")