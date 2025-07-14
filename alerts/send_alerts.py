import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# 📂 Load anomaly summary
df = pd.read_csv('reports/anomaly_summary.csv')
df['Date'] = pd.to_datetime(df['Date'])

# 📅 Only today's or yesterday’s anomalies
today = pd.Timestamp.today().normalize()
yesterday = today - timedelta(days=1)
recent_anomalies = df.head(5)  # 👈 Forces sample alerts to trigger

# ⏹️ Exit if no recent anomalies
if recent_anomalies.empty:
    print("✅ No anomalies to alert.")
    exit()

# 📩 Format message
def format_message(df):
    lines = ["🚨 *Ad Anomalies Detected!*"]
    for _, row in df.iterrows():
        lines.append(f"- 📅 {row['Date'].date()} | 🌍 {row['Country']} | 📊 {row['Anomaly Type']}")
    return "\n".join(lines)

alert_message = format_message(recent_anomalies)

# ✉️ Send Email
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

# 💬 Send Slack
def send_slack(message):
    webhook_url = os.getenv("SLACK_WEBHOOK")
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("✅ Slack alert sent.")
        else:
            print("❌ Slack failed:", response.text)
    except Exception as e:
        print("❌ Slack error:", e)

# 🚀 Send both alerts
send_email("🚨 Ad Metric Anomaly Alert", alert_message)
send_slack(alert_message)
