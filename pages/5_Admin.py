import streamlit as st
from sqlalchemy import text
import os, sys

# ✅ ดึง auth_utils.py โดยตรง
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth_utils import engine, insert_user_log

st.set_page_config(page_title="🛡️ Admin จัดการผู้ใช้")

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

# ✅ ตรวจสอบสิทธิ์
if st.session_state.get("role") != "admin":
    st.error("🚫 คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (Admin เท่านั้น)")
    st.stop()

# Log การเข้าใช้งาน
insert_user_log(st.session_state["user"], "view_admin")

st.markdown("## 🛡️ จัดการบัญชีผู้ใช้ทั้งหมด")

# โหลดรายชื่อผู้ใช้
def load_users():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, username, email, role, is_confirmed, created_at
            FROM users ORDER BY created_at DESC
        """)).fetchall()
        return result

users = load_users()

# ตารางผู้ใช้
if users:
    for u in users:
        with st.expander(f"👤 {u.username} ({u.role})"):
            st.write("📧", u.email)
            st.write("✅ ยืนยันอีเมลแล้ว:", "ใช่" if u.is_confirmed else "ยัง")
            st.write("🕒 สร้างเมื่อ:", u.created_at)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"❌ ลบบัญชี {u.username}", key=f"del_{u.id}"):
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": u.id})
                    st.success(f"✅ ลบผู้ใช้ {u.username} แล้ว")
                    insert_user_log(st.session_state["user"], f"delete_user: {u.username}")
                    st.experimental_rerun()
            with col2:
                new_role = st.selectbox("👤 เปลี่ยนสิทธิ์", ["user", "admin"], index=["user", "admin"].index(u.role), key=f"role_{u.id}")
                if new_role != u.role:
                    if st.button(f"💼 เปลี่ยนเป็น {new_role}", key=f"rolebtn_{u.id}"):
                        with engine.begin() as conn:
                            conn.execute(
                                text("UPDATE users SET role = :r WHERE id = :id"),
                                {"r": new_role, "id": u.id}
                            )
                        st.success(f"🔄 เปลี่ยนสิทธิ์ของ {u.username} เป็น {new_role}")
                        insert_user_log(st.session_state["user"], f"change_role: {u.username} to {new_role}")
                        st.experimental_rerun()
else:
    st.warning("ไม่มีผู้ใช้ในระบบ")
