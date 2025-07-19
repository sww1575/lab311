import streamlit as st

st.set_page_config(page_title="Welcome to Fin Assistant", page_icon="🤖", layout="wide")

st.markdown("""
<style>
/* ---- BG Main App ---- */
.stApp {
    background: linear-gradient(135deg, #2f1f75 0%, #6b3fe7 70%, #12c2e9 100%) !important;
}
/* ---- Sidebar BG: ฟ้าเข้ม > ม่วงน้ำเงิน (โทนเดียวกัน แต่ตัดพื้นหลังหลัก) ---- */
section[data-testid="stSidebar"] {
    background: linear-gradient(120deg, #151c39 0%, #2b3289 80%, #3474b7 100%) !important;
    min-width: 250px !important;
    border-right: 3px solid #7a4cff22;
    box-shadow: 8px 0 24px -16px #20206044;
}
/* ---- Sidebar: ตัวอักษรขาวชัดทุกจุด ---- */
section[data-testid="stSidebar"] * {
    color: #fff !important;
    font-size: 18px !important;
}
section[data-testid="stSidebar"] a {
    color: #fff !important;
}
section[data-testid="stSidebar"] a:hover {
    color: #ffe268 !important;
}
/* Sidebar active */
section[data-testid="stSidebar"] .css-17lntkn,
section[data-testid="stSidebar"] .css-1v0mbdj,
section[data-testid="stSidebar"] .css-1c7y2kd,
section[data-testid="stSidebar"] .css-16idsys {
    background-color: #7a4cff !important;
    color: #ffe268 !important;
    font-weight: bold !important;
    border-radius: 8px !important;
}
/* ---- ปุ่มเข้าสู่ระบบ ---- */
.stButton button {
    color: #fff !important;
    background: linear-gradient(90deg, #7a4cff 0%, #27d3f7 100%) !important;
    border-radius: 12px !important;
    font-weight: bold;
    font-size: 22px !important;
    padding: 0.7em 3.5em;
    margin-top: 10px;
    box-shadow: 0 4px 24px 0 #22084f2a;
    border: 1.5px solid #fff5;
    transition: background 0.15s;
}
.stButton button:hover {
    background: linear-gradient(90deg, #27d3f7 0%, #7a4cff 100%) !important;
    color: #ffe268 !important;
}
</style>
""", unsafe_allow_html=True)

# --- ภาพใหญ่ขึ้น 20% (ใช้ column กลางกว้างขึ้นและเพิ่ม width)
col1, col2, col3 = st.columns([0.4, 2.2, 0.4])
with col2:
    st.image("fin_assistant_home.png", width=1150)  # ขยายจากเดิม 950 → 1150

st.write("")
col4, col5, col6 = st.columns([2, 1, 2])
with col5:
    login_button = st.button("เข้าสู่ระบบ", key="login_btn")

if login_button:
    st.switch_page("pages/1_Login.py")

st.markdown("""
<div style='text-align: center; font-size: 14px; color: #94A3B8;'>
    Fin Assistant ⓒ 2025 | พัฒนาเพื่อช่วยหน่วยงานวิเคราะห์ข้อมูลทางการเงินได้ง่ายขึ้น
</div>
""", unsafe_allow_html=True)

if st.session_state.get("role") == "admin":
    st.sidebar.page_link("pages/5_Admin.py", label="🛡️ Admin จัดการผู้ใช้")
