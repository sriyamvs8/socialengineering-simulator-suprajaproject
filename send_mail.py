import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load .env file
load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

receiver = input("Enter receiver email: ")

msg = EmailMessage()
msg["Subject"] = "SMTP Test"
msg["From"] = EMAIL
msg["To"] = receiver

msg.set_content("""
Hello,

This is my first SMTP email sent from my Flask project.

Regards,
TeddyLock
""")

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

    print("✅ Email Sent Successfully!")

except Exception as e:
    print("❌ Error:", e)