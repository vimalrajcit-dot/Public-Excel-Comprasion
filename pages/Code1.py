import streamlit as st
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# =========================
# CONFIG
# =========================
OTP_EXPIRY_SECONDS = 300  # 5 minutes

# =========================
# SECRETS
# =========================
GMAIL_USER = st.secrets["GMAIL_USER"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]
ALLOWED_EMAIL = st.secrets["ALLOWED_EMAIL"]

# =========================
# SEND OTP VIA GMAIL
# =========================
def send_otp_gmail(receiver_email, otp):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = receiver_email
    msg["Subject"] = "🔐 Your Streamlit Login OTP"

    body = f"""
    <h2>Your OTP is: {otp}</h2>
    <p>This OTP is valid for <b>5 minutes</b>.</p>
    <p>Do not share it with anyone.</p>
    """
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email send failed: {e}")
        return False

# =========================
# OTP AUTH FLOW
# =========================
def email_otp_auth():
    if "auth_ok" not in st.session_state:
        st.session_state.auth_ok = False
    if "otp_sent" not in st.session_state:
        st.session_state.otp_sent = False
    if "otp_time" not in st.session_state:
        st.session_state.otp_time = None

    if st.session_state.auth_ok:
        return True

    st.subheader("🔐 Gmail OTP Login")

    email = st.text_input("Enter your Gmail address")

    if st.button("📨 Send OTP"):
        if email.strip().lower() != ALLOWED_EMAIL.lower():
            st.error("❌ Unauthorized email")
            st.stop()

        otp = str(random.randint(100000, 999999))
        st.session_state.otp = otp
        st.session_state.otp_time = time.time()

        if send_otp_gmail(email, otp):
            st.session_state.otp_sent = True
            st.success("✅ OTP sent to your Gmail")

    if st.session_state.otp_sent:
        entered_otp = st.text_input("Enter OTP", max_chars=6)

        if st.button("✅ Verify OTP"):
            if time.time() - st.session_state.otp_time > OTP_EXPIRY_SECONDS:
                st.error("⏰ OTP expired. Send a new one.")
                st.session_state.otp_sent = False
                return False

            if entered_otp == st.session_state.otp:
                st.session_state.auth_ok = True
                st.success("🎉 Login successful")
                return True
            else:
                st.error("❌ Invalid OTP")

    return False

# =========================
# PROTECT APP
# =========================
if not email_otp_auth():
    st.stop()

# =========================
# APP STARTS HERE
# =========================
st.set_page_config(
    page_title="R0 vs R1 Tag Comparison",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Secure Streamlit App")
st.write("You are logged in via Gmail OTP 🚀")
