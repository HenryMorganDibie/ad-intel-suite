# 📊 Ad Intelligence Suite

A full-stack data analytics solution for monitoring, forecasting, and automating digital ad performance metrics — built with Python, Streamlit, and Prophet.

---

## 🚀 Project Overview

The **Ad Intelligence Suite** empowers marketers and analysts to:
- Track key ad metrics like eCPM, CTR, Clicks, Revenue, and Impressions
- Detect anomalies in campaign performance (e.g. drops/spikes)
- Forecast future ad performance using time series modeling
- Automatically send alerts via email and Slack
- Explore data via an interactive dashboard

This project combines automation, forecasting, anomaly detection, and visualization into a real-world, production-ready data product.

---

## 🧰 Tech Stack

| Layer           | Tools/Libraries                        |
|----------------|----------------------------------------|
| Data Handling   | `pandas`, `numpy`                     |
| Forecasting     | `prophet` (by Meta)                   |
| Visualization   | `matplotlib`, `seaborn`, `plotly`     |
| Dashboard UI    | `streamlit`                           |
| Automation      | `smtplib`, `requests`, `dotenv`       |
| Notifications   | Email (Yahoo SMTP), Slack Webhooks    |
| Scheduling      | Windows Task Scheduler                |
| Project Structure | Modular Python scripts + Jupyter Notebooks             |

---

## 📁 Project Structure
<pre lang="markdown">
ad-intelligence-suite/
├── alerts/                 # Email + Slack alert scripts
├── app/                    # Utilities (helpers, configs)
├── dashboard/              # Streamlit dashboard
├── forecast/               # Forecasting scripts
├── images/                 # 📸 All screenshots/images
├── data/                   # Raw datasets (CSV)
├── reports/                # Outputs (forecasts, anomalies, HTML)
├── notebooks/              # EDA, anomaly detection, modeling
├── .env                    # Email/Slack credentials (excluded in .gitignore)
└── README.md
</pre>


---

## 📈 Features

### 🧪 Exploratory Data Analysis (EDA)
- Data profiling
- Missing value checks
- Distribution & trend plots across eCPM, CTR, Revenue, and more

### 📉 Anomaly Detection
- Identify abnormal CTR, eCPM, Clicks, and Impressions
- Output a clean `anomaly_summary.csv` report
- Alert stakeholders automatically

### 📈 Forecasting (eCPM)
- Prophet-based time series modeling
- Auto-updated forecast file (`forecast_ecpm.csv`)
- Weekly summary messages (e.g. “eCPM down 8.4%”)

### 📬 Email & Slack Alerts
- Anomaly alerts sent instantly
- Weekly forecast alerts via Yahoo Mail + Slack
- Uses `.env` for secure credentials

### 📊 Interactive Dashboard (Streamlit)
- Metric switcher (CTR, Clicks, Revenue, etc.)
- Highlight anomalies directly on charts
- Compare date ranges (WoW, MoM)
- Forecast lines and historical trends displayed together

### ⏰ Automation (Scheduled Tasks)
- Fully autonomous with Windows Task Scheduler
- No need to run manually

---

## 📸 Screenshots

| Email & Slack Alerts      | Forecast Visuals           |
|---------------------------|----------------------------|
| ![](images/email_alert.png) | ![](images/ecpm_forecast.png) |
| ![](images/slack_alert.png) | ![](images/ctr_forecast.png)  |
|                           | ![](images/clicks_forecast.png) |
|                           | ![](images/impressions_forecast.png) |
|                           | ![](images/revenue_forecast.png) |

---

## 📦 Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/HenryMorganDibie/ad-intelligence-suite.git
   cd ad-intelligence-suite


2. **Create a virtual environment**
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

3. **Set up your .env**
   ```
   EMAIL_SENDER=your_yahoo_email
   EMAIL_PASSWORD=your_yahoo_app_password
   EMAIL_RECEIVER=recipient@example.com
   SLACK_WEBHOOK=https://hooks.slack.com/...

4. **Run components**
   ```
   - Run EDA: eda/eda.ipynb

   - Forecast: python forecast/generate_forecast_and_anomalies.py

   - Anomaly Alerts: python alerts/send_alerts.py

   - Forecast Alerts: python forecast/send_forecast_alerts.py

   - Dashboard: streamlit run dashboard/dashboard.py

💡 Inspiration
This project simulates the kind of real-time, data-driven alerting system used by performance marketing teams to optimize digital ad spend and delivery in real-time. It was built to demonstrate full-stack data capabilities in a real-world setting.

📫 Contact
Henry C. Dibie
henrymorgan273@yahoo.com

Give this repo a ⭐ if you find it useful or inspiring!

