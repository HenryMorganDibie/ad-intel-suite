import pandas as pd
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import requests
from dotenv import load_dotenv

load_dotenv()

# 📥 Load forecast data
df = pd.read_csv("reports/forecast_ecpm.csv")
df["ds"] = pd.to_datetime(df["ds"])

# 📆 Define forecast window
today = datetime.today().date()
next_7 = df[df["ds"].dt.date.between(today, today + timedelta(days=6))]
prev_7 = df[df["ds"].dt.date.between(today - timedelta(days=7), today - timedelta(days=1))]

# 🚫 Abort if forecast missing
if next_7.empty:
    print("✅ No future forecast available.")
    exit()

# 📊 Stats
next_avg = next_7["yhat"].mean()
prev_avg = prev_7["yhat"].mean() if not prev_7.empty else None
pct_change = ((next_avg - prev_avg) / prev_avg * 100) if prev_avg else None
peak_day = next_7.loc[next_7["yhat"].idxmax()]["ds"].date()
low_day = next_7.loc[next_7["yhat"].idxmin()]["ds"].date()

# 📝 Format alert
lines = [
    "📊 *Weekly Forecast Alert*",
    f"📅 {today} → {today + timedelta(days=6)}",
    f"🔹 Avg eCPM: ${next_avg:.2f}",
]
if pct_change is not None:
    trend = "🔼 Increase" if pct_change > 0 else "🔻 Decrease"
    lines.append(f"{trend} vs last week: {pct_change:.1f}%")
lines.append(f"📈 Peak on {peak_day}")
lines.append(f"📉 Lowest on {low_day}")

alert_text = "\n".join(lines)

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

# 🚀 Send both alerts
send_email("📈 Weekly Forecast eCPM Update", alert_text)
send_slack(alert_text)
