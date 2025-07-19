import streamlit as st

# ตั้งค่าให้ชื่อแท็บดูดี
st.set_page_config(page_title="ออกจากระบบ", layout="centered")

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


# ลบ session ที่เกี่ยวกับผู้ใช้
for key in ["user", "role", "is_authenticated"]:
    if key in st.session_state:
        del st.session_state[key]

# แจ้งเตือนและ redirect
st.success("✅ ออกจากระบบเรียบร้อยแล้ว กำลังเปลี่ยนกลับไปยังหน้าเข้าสู่ระบบ...")



st.markdown("[กลับไปหน้า Login](Login)")
st.stop()

