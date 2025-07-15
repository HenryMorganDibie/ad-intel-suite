import pandas as pd
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import requests
from dotenv import load_dotenv

load_dotenv()

# 🔍 Define metrics to monitor
metrics = {
    "eCPM": "forecast_ecpm.csv",
    "CTR": "forecast_ctr.csv",
    "Clicks": "forecast_clicks.csv",
    "Impressions": "forecast_impressions.csv",
    "Revenue": "forecast_revenue.csv"
}

today = datetime.today().date()
alert_sections = []

# 📊 Loop through each metric and generate section
for metric, filename in metrics.items():
    path = os.path.join("reports", filename)
    if not os.path.exists(path):
        print(f"⚠️ Skipping {metric} – file not found.")
        continue

    df = pd.read_csv(path)
    df["ds"] = pd.to_datetime(df["ds"])

    next_7 = df[df["ds"].dt.date.between(today, today + timedelta(days=6))]
    prev_7 = df[df["ds"].dt.date.between(today - timedelta(days=7), today - timedelta(days=1))]

    if next_7.empty:
        print(f"✅ No forecast for {metric}.")
        continue

    next_avg = next_7["Forecast"].mean()
    prev_avg = prev_7["Forecast"].mean() if not prev_7.empty else None
    pct_change = ((next_avg - prev_avg) / prev_avg * 100) if prev_avg else None
    peak_day = next_7.loc[next_7["Forecast"].idxmax()]["ds"].date()
    low_day = next_7.loc[next_7["Forecast"].idxmin()]["ds"].date()

    section = [
        f"📊 *{metric} Forecast*",
        f"📅 {today} → {today + timedelta(days=6)}",
        f"🔹 Avg {metric}: {next_avg:.2f}" if metric != "CTR" else f"🔹 Avg {metric}: {next_avg:.2%}"
    ]

    if pct_change is not None:
        trend = "🔼 Increase" if pct_change > 0 else "🔻 Decrease"
        section.append(f"{trend} vs last week: {pct_change:.1f}%")

    section.append(f"📈 Peak on {peak_day}")
    section.append(f"📉 Lowest on {low_day}")
    alert_sections.append("\n".join(section))

# 🚫 If no sections, exit
if not alert_sections:
    print("✅ No forecasts available to send.")
    exit()

# 🧾 Final message
alert_text = "\n\n".join(alert_sections)

# ✉️ Email Alert
def send_email(subject, body):
    sender = os.getenv("EMAIL_SENDER")
    receiver = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Email failed:", e)

# 💬 Slack Alert
def send_slack(message):
    webhook_url = os.getenv("SLACK_WEBHOOK")
    try:
        res = requests.post(webhook_url, json={"text": message})
        if res.status_code == 200:
            print("✅ Slack alert sent.")
        else:
            print("❌ Slack failed:", res.text)
    except Exception as e:
        print("❌ Slack error:", e)

# 🚀 Send Alerts
send_email("📈 Weekly Forecast Update", alert_text)
send_slack(alert_text)
