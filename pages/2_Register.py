import streamlit as st
from sqlalchemy import text
from streamlit_extras.switch_page_button import switch_page
from auth_utils import (
    engine,
    register_user,
    send_confirmation_email,
)

# -------------------------
st.set_page_config(page_title="ลงทะเบียน", page_icon="📝")

if st.session_state.get("role") == "admin":
        st.sidebar.page_link("pages/5_Admin.py", label="🛡️ Admin จัดการผู้ใช้")

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

st.markdown("## 📝 ลงทะเบียนผู้ใช้งานใหม่")

with st.form("register_form", clear_on_submit=True):
    username = st.text_input("ชื่อผู้ใช้", max_chars=50)
    email = st.text_input("อีเมล", max_chars=100)
    password = st.text_input("รหัสผ่าน", type="password")
    confirm_password = st.text_input("ยืนยันรหัสผ่าน", type="password")
    role = st.selectbox("ประเภทผู้ใช้", ["user", "admin"])
    submitted = st.form_submit_button("ลงทะเบียน")

    if submitted:
        if not username or not email or not password or not confirm_password:
            st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
        elif password != confirm_password:
            st.error("❌ รหัสผ่านไม่ตรงกัน")
        elif len(password) < 6:
            st.warning("⚠️ รหัสผ่านควรมีอย่างน้อย 6 ตัวอักษร")
        else:
            success, msg = register_user(username, email, password)
            if success:
                try:
                    send_confirmation_email(email, username)
                    st.success(msg)
                    st.info("📧 กรุณาตรวจสอบอีเมลของคุณเพื่อยืนยันการลงทะเบียน")
                except Exception as e:
                    st.warning(f"ลงทะเบียนสำเร็จ แต่ส่งอีเมลไม่สำเร็จ: {e}")
            else:
                st.error(msg)