import streamlit as st
from sqlalchemy import create_engine, text
import bcrypt, yagmail, uuid
from datetime import datetime

# ------------------------------
# 1. สร้าง engine เชื่อม PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:12345678@localhost:5432/postgres")

# ------------------------------
# 2. ตั้งค่า Email (อย่าลืมใช้ App Password สำหรับ Gmail)
SENDER_EMAIL = "sww103492@gmail.com"
SENDER_PASSWORD = "sxbf vmed orsx enye"
yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)

# ------------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ------------------------------
def register_user(username, email, password):
    """
    ลงทะเบียนผู้ใช้ใหม่และบันทึกข้อมูลลงตาราง users
    """
    try:
        with engine.begin() as conn:  # ใช้ begin() เพื่อ auto-commit
            # ตรวจสอบ username/email ซ้ำ
            user = conn.execute(
                text("SELECT 1 FROM users WHERE username = :u"), {"u": username.strip()}
            ).fetchone()
            if user:
                return False, "❌ Username นี้ถูกใช้งานแล้ว"
            email_exist = conn.execute(
                text("SELECT 1 FROM users WHERE email = :e"), {"e": email.strip()}
            ).fetchone()
            if email_exist:
                return False, "❌ อีเมลนี้ถูกใช้งานแล้ว"

            hashed = hash_password(password)

            # INSERT ข้อมูลใหม่
            conn.execute(text("""
                INSERT INTO users (username, email, password, is_confirmed, role, created_at)
                VALUES (:u, :e, :p, false, 'user', :t)
            """), {
                "u": username.strip(),
                "e": email.strip(),
                "p": hashed,
                "t": datetime.now()
            })
        return True, "✅ ลงทะเบียนสำเร็จ กรุณายืนยันอีเมลของคุณทางลิงก์ที่ส่งไป"
    except Exception as e:
        print("Register Exception:", e)
        return False, f"❌ เกิดข้อผิดพลาด: {str(e)}"

# ------------------------------
def send_confirmation_email(to_email, username):
    """
    ส่งอีเมลยืนยันไปหาผู้ใช้งาน
    """
    link = f"http://localhost:8501/Login?confirm={username}"
    subject = "กรุณายืนยันอีเมลเพื่อเข้าใช้งานระบบ FinAIgent"
    body = f"""สวัสดีคุณ {username},\n\nกรุณาคลิกที่ลิงก์ด้านล่างเพื่อยืนยันอีเมลของคุณ:\n{link}"""
    yag.send(to_email, subject, body)

# ------------------------------
def create_reset_token(username):
    """
    สร้างโทเคนสำหรับ reset password
    """
    token = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET reset_token=:t WHERE username=:u"),
            {"t": token, "u": username}
        )
    return token

def send_reset_email(to_email, username, token):
    """
    ส่งอีเมลสำหรับ reset password
    """
    link = f"http://localhost:8501/Login?reset={token}"
    subject = "รีเซตรหัสผ่าน FinAIgent"
    body = f"""สวัสดีคุณ {username},\n\nคลิกที่ลิงก์เพื่อสร้างรหัสผ่านใหม่:\n{link}"""
    yag.send(to_email, subject, body)

def reset_password(token, new_password):
    """
    รีเซ็ตรหัสผ่านผู้ใช้ด้วย token
    """
    hashed = hash_password(new_password)
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password=:p, reset_token=NULL WHERE reset_token=:t"),
            {"p": hashed, "t": token}
        )

def insert_user_log(username, action):
    """
    บันทึก Log การกระทำของผู้ใช้ เช่น Login, Register, Reset Password
    """
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO user_logs (username, action, timestamp)
                VALUES (:u, :a, :t)
            """),
            {"u": username, "a": action, "t": datetime.now()}
        )

params = st.query_params

if params.get("page") == "dashboard":
    st.switch_page("2_Dashboard.py")  # ถ้ายังใช้ได้ หรือ redirect ด้วยลิงก์