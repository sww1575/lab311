import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from utils.multi_agent import run_agent_streaming, leader_route
from utils.stock_api import get_stock_info

load_dotenv()
st.set_page_config(page_title="🤖 ผู้ช่วย AI ด้านการเงิน", layout="wide")
st.title("🤖 ผู้ช่วยอัจฉริยะด้านการเงิน & ธุรกิจ")



# ---- Styling ---
st.markdown("""<style>
.stApp {
    background: linear-gradient(135deg, #726bca 0%, #d1d8fd 50%, #5aa0f7 100%) !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(120deg, #43168d 0%, #273585 70%, #3e87f7 100%) !important;
    min-width: 250px !important;
    border-right: 3px solid #7a4cff22;
    box-shadow: 8px 0 24px -16px #20206044;
}
section[data-testid="stSidebar"] * {
    color: #fff !important;
    font-size: 18px !important;
}
section[data-testid="stSidebar"] .css-17lntkn,
section[data-testid="stSidebar"] .css-1v0mbdj,
section[data-testid="stSidebar"] .css-1c7y2kd,
section[data-testid="stSidebar"] .css-16idsys {
    background-color: #7a4cff !important;
    color: #ffe268 !important;
    font-weight: bold !important;
    border-radius: 8px !important;
}
</style>""", unsafe_allow_html=True)

# ===============================
# 🤖 Section 0: ถาม-ตอบ AI ทั่วไป (Streaming)
# ===============================
st.subheader("🤖 ถาม-ตอบ AI ด้านการเงิน/ธุรกิจ (Streaming)")

general_question = st.text_input("💬 ใส่คำถามของคุณ:", key="general_q")
agent_name = st.selectbox("🤖 เลือกผู้ช่วย:", ["🔎 Auto (AI แนะนำ)", "🧠 Finny", "🧾 Accy", "💼 Bizzy", "💬 Leader"])

agent_map = {
    "🧠 Finny": "finny",
    "🧾 Accy": "accy",
    "💼 Bizzy": "bizzy",
    "💬 Leader": "leader",
    "🔎 Auto (AI แนะนำ)": "auto"
}
agent_key = agent_map[agent_name]

if st.button("🚀 ถาม AI เลย!"):
    st.markdown(f"### 🗨️ คำตอบจาก {agent_name}:")

    if agent_key == "auto":
        agent_key = leader_route(general_question)

    response = run_agent_streaming(general_question, agent_key=agent_key)
    response_placeholder = st.empty()
    full_response = ""

    for answer_chunk in response:
        full_response += answer_chunk
        response_placeholder.markdown(full_response)

st.divider()

# ===============================
# 📁 Section 1: วิเคราะห์งบจากไฟล์ CSV
# ===============================
st.subheader("📁 วิเคราะห์งบการเงิน (อัปโหลดไฟล์ CSV)")
uploaded_file = st.file_uploader("📎 อัปโหลดไฟล์งบ (.csv)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
    csv_question = st.text_input("💬 ถามเกี่ยวกับงบ:")
    csv_agent = st.selectbox("🤖 เลือกผู้ช่วยสำหรับวิเคราะห์งบ:", ["🧠 Finny", "🧾 Accy", "💼 Bizzy", "💬 Leader"], key="csv_agent")

    if st.button("🔍 วิเคราะห์งบด้วย AI"):
        prompt = f"งบการเงิน:\n{df.to_string(index=False)}\nคำถาม: {csv_question}"
        selected = agent_map[csv_agent]
        response = run_agent_streaming(prompt, agent_key=selected)

        response_placeholder = st.empty()
        full_response = ""
        for chunk in response:
            full_response += chunk
            response_placeholder.markdown(full_response)

st.divider()

