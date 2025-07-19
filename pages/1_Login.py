import streamlit as st
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth_utils import engine, check_password, create_reset_token, send_reset_email, reset_password, insert_user_log
params = st.query_params

st.markdown("""
<style>
/* --- Main Background --- */
.stApp {
    background: linear-gradient(135deg, #726bca 0%, #d1d8fd 50%, #5aa0f7 100%) !important;
}
/* --- Sidebar Background --- */
section[data-testid="stSidebar"] {
    background: linear-gradient(120deg, #43168d 0%, #273585 70%, #3e87f7 100%) !important;
    min-width: 250px !important;
    border-right: 3px solid #7a4cff22;
    box-shadow: 8px 0 24px -16px #20206044;
}
/* --- Sidebar Text --- */
section[data-testid="stSidebar"] * {
    color: #fff !important;
    font-size: 18px !important;
}
section[data-testid="stSidebar"] a:hover {
    color: #ffe268 !important;
}
/* --- Sidebar Active --- */
section[data-testid="stSidebar"] .css-17lntkn,
section[data-testid="stSidebar"] .css-1v0mbdj,
section[data-testid="stSidebar"] .css-1c7y2kd,
section[data-testid="stSidebar"] .css-16idsys {
    background-color: #7a4cff !important;
    color: #ffe268 !important;
    font-weight: bold !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# 1. รีเซตรหัสผ่าน (ถ้ามี token reset มา)
if "reset" in params:
    token = params["reset"]
    st.markdown("## 🔁 รีเซตรหัสผ่านใหม่")
    new_pass = st.text_input("รหัสผ่านใหม่", type="password")
    confirm_pass = st.text_input("ยืนยันรหัสผ่าน", type="password")
    if st.button("รีเซตรหัสผ่าน"):
        if new_pass == confirm_pass:
            reset_password(token, new_pass)
            st.success("✅ รีเซตรหัสผ่านสำเร็จแล้ว กรุณาเข้าสู่ระบบใหม่")
        else:
            st.error("❌ รหัสผ่านไม่ตรงกัน")
    st.stop()

# 2. ยืนยันอีเมล (ถ้ามี query confirm)
if "confirm" in params:
    username = params["confirm"]
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET is_confirmed=TRUE WHERE LOWER(username)=LOWER(:u)"),
            {"u": username}
        )
    st.success(f"✅ ยืนยันอีเมลสำเร็จสำหรับผู้ใช้ {username} แล้ว กรุณาเข้าสู่ระบบ")

# 3. ฟอร์มเข้าสู่ระบบ
if "user" not in st.session_state:
    st.markdown("## เข้าสู่ระบบ")
    username = st.text_input("ชื่อผู้ใช้")
    password = st.text_input("รหัสผ่าน", type="password")
    login_btn = st.button("เข้าสู่ระบบ")

    if login_btn:
        with engine.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM users WHERE LOWER(username) = LOWER(:u)"),
                {"u": username}
            ).fetchone()
            if user:
                if check_password(password, user.password):
                    if user.is_confirmed:
                        insert_user_log(username, "success")
                        st.session_state["user"] = user.username
                        st.session_state["role"] = user.role
                        # --- REDIRECT อัตโนมัติไป Dashboard ด้วย JS ---
                        st.success(f"✅ ยินดีต้อนรับคุณ **{user.username}** เข้าสู่ระบบสำเร็จ!")
                        st.stop()  # หยุดโค้ดหลัง redirect (สำคัญ!)
                        
                        
                    else:
                        insert_user_log(username, "not_confirmed")
                        st.warning("⚠️ บัญชีนี้ยังไม่ได้ยืนยันอีเมล กรุณาตรวจสอบอีเมลของคุณและคลิกลิงก์ยืนยัน")
                else:
                    insert_user_log(username, "fail")
                    st.error("❌ รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
            else:
                insert_user_log(username, "fail")
                st.error("❌ ไม่พบผู้ใช้ในระบบ กรุณาตรวจสอบชื่อผู้ใช้ให้ถูกต้อง")

    st.markdown("### 📥 ยังไม่มีบัญชีผู้ใช้? [ลงทะเบียนที่นี่](Register)")

    st.markdown("---")
    with st.expander("🔁 ลืมรหัสผ่าน?"):
        user_forgot = st.text_input("ชื่อผู้ใช้สำหรับรีเซตรหัสผ่าน", key="forgot_user")
        if st.button("ส่งอีเมลรีเซต"):
            with engine.connect() as conn:
                user = conn.execute(
                    text("SELECT * FROM users WHERE LOWER(username) = LOWER(:u)"),
                    {"u": user_forgot}
                ).fetchone()
                if user:
                    token = create_reset_token(user.username)
                    send_reset_email(user.email, user.username, token)
                    st.success("✅ ส่งลิงก์รีเซตไปยังอีเมลเรียบร้อยแล้ว")
                else:
                    st.error("ไม่พบผู้ใช้งานนี้")
else:
    # ถ้า login แล้ว แสดงลิงก์เมนูต่าง ๆ
    st.markdown(f"👋 ยินดีต้อนรับ, **{st.session_state['user']}**")
    st.markdown("[➡️ ไปหน้า Dashboard](Dashboard)")
    st.markdown("[👤 ไปหน้าโปรไฟล์](Profile)")
    st.markdown("[🚪 ออกจากระบบ](Logout)")

    
    if st.session_state.get("role") == "admin":
        st.sidebar.page_link("pages/5_Admin.py", label="🛡️ Admin จัดการผู้ใช้")