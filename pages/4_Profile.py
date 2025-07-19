import streamlit as st
from sqlalchemy import text
import os, sys

# ✅ ดึง auth_utils จากโฟลเดอร์หลัก
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth_utils import engine, hash_password, insert_user_log

st.set_page_config(page_title="โปรไฟล์ของฉัน")

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

# ✅ ตรวจสอบ session ว่ามีผู้ใช้ล็อกอินหรือยัง
if "user" not in st.session_state:
    st.error("🚫 กรุณาเข้าสู่ระบบก่อนใช้งานหน้านี้")
    st.markdown("[กลับไปหน้า Login](Login)")
    st.stop()

# โหลดข้อมูลผู้ใช้จากฐานข้อมูล
def get_user_profile(username):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT username, email, role FROM users WHERE LOWER(username) = LOWER(:u)"),
            {"u": username}
        )
        return result.fetchone()

old_username = st.session_state["user"]
user = get_user_profile(old_username)

# 🔍 log ว่าผู้ใช้เข้ามาที่หน้าโปรไฟล์
insert_user_log(old_username, "view_profile")

st.markdown("## 👤 โปรไฟล์ของคุณ")

if user:
    st.write("🔑 บทบาท:", user.role)

    with st.form("update_form"):
        new_username = st.text_input("ชื่อผู้ใช้", value=user.username)
        new_email = st.text_input("อีเมล", value=user.email)
        new_password = st.text_input("รหัสผ่านใหม่ (ถ้าไม่เปลี่ยน ให้เว้นว่าง)", type="password")

        submitted = st.form_submit_button("บันทึกการเปลี่ยนแปลง")

        if submitted:
            if not new_username.strip():
                st.error("❌ กรุณากรอกชื่อผู้ใช้")
            else:
                try:
                    with engine.begin() as conn:
                        # ✅ ตรวจสอบ username ซ้ำ (ถ้าเปลี่ยน)
                        if new_username.lower() != old_username.lower():
                            dup = conn.execute(
                                text("SELECT 1 FROM users WHERE LOWER(username) = LOWER(:u)"),
                                {"u": new_username}
                            ).fetchone()
                            if dup:
                                st.error("❌ ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาเลือกชื่ออื่น")
                                st.stop()

                        # ✅ อัปเดตข้อมูล
                        if new_password:
                            hashed_pw = hash_password(new_password)
                            conn.execute(
                                text("""
                                    UPDATE users
                                    SET username=:new_u, email=:e, password=:p, updated_at=now()
                                    WHERE LOWER(username)=LOWER(:old_u)
                                """),
                                {"new_u": new_username, "e": new_email, "p": hashed_pw, "old_u": old_username}
                            )
                        else:
                            conn.execute(
                                text("""
                                    UPDATE users
                                    SET username=:new_u, email=:e, updated_at=now()
                                    WHERE LOWER(username)=LOWER(:old_u)
                                """),
                                {"new_u": new_username, "e": new_email, "old_u": old_username}
                            )

                    # ✅ อัปเดต session
                    st.session_state["user"] = new_username
                    st.success("✅ อัปเดตโปรไฟล์สำเร็จแล้ว")
                    insert_user_log(new_username, "update_profile")

                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
else:
    st.warning("ไม่พบข้อมูลผู้ใช้ในระบบ")

# ปุ่มทางลัด
st.markdown("---")
st.markdown("[📊 กลับหน้า Dashboard](3_Dashboard) | [🚪 ออกจากระบบ](9_Logout)")
