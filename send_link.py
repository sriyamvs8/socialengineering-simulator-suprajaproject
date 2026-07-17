import subprocess
import time
import requests
import smtplib
from email.mime.text import MIMEText

# ---- CONFIG ----
FLASK_PORT = 5000
SENDER_EMAIL = "netenterprise7@gmail.com"
SENDER_PASSWORD = "ggge itlr iclq wuba"
RECIPIENTS = ["pawarbhavani2005@gmail.com", "sriyamvs04@gmail.com"]
SUBJECT = "Your Training Page Link"

# ---- STEP 1: Start Flask app ----
flask_process = subprocess.Popen(["python", "app.py"])
time.sleep(3)

# ---- STEP 2: Start ngrok ----
ngrok_process = subprocess.Popen(["ngrok", "http", str(FLASK_PORT)])
time.sleep(5)

# ---- STEP 3: Get public URL from ngrok API ----
try:
    response = requests.get("http://localhost:4040/api/tunnels")
    data = response.json()
    public_url = data["tunnels"][0]["public_url"]
    print(f"Public URL generated: {public_url}")
except Exception as e:
    print("Failed to get ngrok URL:", e)
    public_url = None

# ---- STEP 4: Email the URL ----
if public_url:
    message_body = f"Hi,\n\nYour page is now live. Please open the link below:\n{public_url}\n\nRegards,\nTeam"
    msg = MIMEText(message_body)
    msg["Subject"] = SUBJECT
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())

    print("Email sent to all recipients!")

print("Press Ctrl+C to stop Flask + ngrok.")
try:
    flask_process.wait()
except KeyboardInterrupt:
    flask_process.terminate()
    ngrok_process.terminate()