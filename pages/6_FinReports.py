import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# ✅ เชื่อมต่อ PostgreSQL (แก้ไขตามรหัสผ่านคุณ)
engine = create_engine("postgresql+psycopg2://postgres:12345678@localhost:5432/postgres")

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

# ✅ โหลดข้อมูลจากตาราง VHAB1
@st.cache_data
def load_data():
    df = pd.read_sql('SELECT * FROM "VHAB1";', engine)

    # ✅ สร้างคอลัมน์ Period (ใช้วันที่ 1 ของเดือน)
    df["Period"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01", errors="coerce")

    # ✅ สร้าง MonthYear และ SortKey สำหรับจัดเรียง
    df["MonthYear"] = df["Period"].dt.strftime("%b%Y")
    df["SortKey"] = df["Period"].dt.year * 100 + df["Period"].dt.month

    # ✅ คำนวณ GP และ GP%
    if "Sales_Income" in df.columns and "CGS" in df.columns:
        df["GP"] = df["Sales_Income"] - df["CGS"]
        df["GP_percent"] = (df["GP"] / df["Sales_Income"]) * 100

    return df

df = load_data()

# ✅ ตั้งค่า session_state (ไว้ **เหนือกว่าฟอร์ม UI** เสมอ)
if "year_select" not in st.session_state:
    st.session_state.year_select = []
if "month_select" not in st.session_state:
    st.session_state.month_select = []
if "dept_select" not in st.session_state:
    st.session_state.dept_select = []
if "type_select" not in st.session_state:
    st.session_state.type_select = []
if "submit_clicked" not in st.session_state:
    st.session_state.submit_clicked = False


st.title("    📊 Business Performance")


# เช็คว่าเข้าสู่ระบบหรือยัง
if "user" not in st.session_state:
    st.error("🚫 คุณยังไม่ได้เข้าสู่ระบบ กรุณา Login ก่อน")
    
    st.markdown("[กลับไปหน้า Login](Login)")
    
    st.stop()

# แสดงข้อมูลเมื่อเข้าสู่ระบบแล้ว
st.success(f"👋 สวัสดีคุณ {st.session_state['user']}")

# ✅ แจ้งเตือนให้กด Submit ก่อนแสดงผล
if not st.session_state.get("submit_clicked", False):
    st.warning("Please select filters and click Submit to view the report.")

with st.sidebar:
    st.markdown("# 🔍 Filters")

    year_select = st.multiselect("YEAR", sorted(df["Year"].dropna().unique(), reverse=True))
    month_select = st.multiselect("MONTH", sorted(df["Month"].dropna().unique()))
    dept_select = st.multiselect("DEPARTMENT", sorted(df["Dept_Code"].dropna().unique()))
    type_select = st.multiselect("TYPE", sorted(df["Type"].dropna().unique()))

    # ✅ ปุ่ม Submit
    if st.button("Submit"):
        st.session_state.year_select = year_select
        st.session_state.month_select = month_select
        st.session_state.dept_select = dept_select
        st.session_state.type_select = type_select
        st.session_state.submit_clicked = True

# ✅ ตรวจสอบว่ามีการกด Submit แล้วหรือยัง
if st.session_state.get("submit_clicked", False):
    df_filtered = df.copy()

    if st.session_state.year_select:
        df_filtered = df_filtered[df_filtered["Year"].isin(st.session_state.year_select)]
    if st.session_state.month_select:
        df_filtered = df_filtered[df_filtered["Month"].isin(st.session_state.month_select)]
    if st.session_state.dept_select:
        df_filtered = df_filtered[df_filtered["Dept_Code"].isin(st.session_state.dept_select)]
    if st.session_state.type_select:
        df_filtered = df_filtered[df_filtered["Type"].isin(st.session_state.type_select)]

    # ใส่ CSS เพื่อปรับแต่ง padding ของกราฟ Plotly
    st.markdown(
    """
    <style>
    /* ซ่อน header ด้านบนของ Streamlit */
    header[data-testid="stHeader"] {
        height: 0;
        visibility: hidden;
    }

    /* ปรับขนาดพื้นที่หลักของเนื้อหา */
    .block-container {
        padding-top: 3rem !important; /* ปรับค่าเพิ่ม-ลดได้ตามต้องการ */
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }

    /* ปรับให้กราฟเต็มพื้นที่ ไม่เหลือขอบด้านข้าง */
    .stPlotlyChart {
        padding: 0;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    # ข้อความที่จะแสดง
    ticker_text = "💰 Total Sales: 122,514,235.94 Baht | 🔧 Service Income: 13,261,974.92 Baht | 📊 Gross Profit: 71,134,994.72 Baht | 💵 Net Profit: 28,395,755.62 Baht"

    # แสดงข้อความแบบไหลจากขวาไปซ้าย
    st.markdown(f"""
    <marquee behavior="scroll" direction="left" scrollamount="6" style="color:#2e86c1;font-size:20px;font-weight:bold;">
        {ticker_text}
    </marquee>
    """, unsafe_allow_html=True)

    
    # ✅ กำไรขั้นต้น และ กำไรสุทธิ (แบ่งซ้าย-ขวา)
    col1, col2 = st.columns(2)

    # ✅ กำไรขั้นต้น (GP)
    if "GP" in df_filtered.columns:
        gp_amount = df_filtered.groupby(["MonthYear", "SortKey"])["GP"].sum().reset_index()
        gp_amount = gp_amount.sort_values("SortKey", ascending=True)

    with col1:
        st.markdown("### 💰 GROSS PROFIT")
        fig_gp_amount = px.line(gp_amount, x="MonthYear", y="GP", markers=True)
        fig_gp_amount.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_gp_amount, use_container_width=True)

        total_gp = gp_amount["GP"].sum()
        


    # ✅ คำนวณกำไรสุทธิ (Net Profit)
        df_filtered["Net_Profit"] = (
        df_filtered["Sales_Income"].fillna(0) +
        df_filtered["Service_Income"].fillna(0) +
        df_filtered["Other_Income"].fillna(0) -
        (
        df_filtered["CGS"].fillna(0) +
        df_filtered["Sales_Exp"].fillna(0) +
        df_filtered["MA_Exp"].fillna(0) +
        df_filtered["GA_Exp"].fillna(0) +
        df_filtered["FA_Exp"].fillna(0) +
        df_filtered["Taxes_Exp"].fillna(0)
        )
    )
    
    # ✅ สร้างกราฟกำไรสุทธิรายเดือน
    net_month = df_filtered.groupby(["MonthYear", "SortKey"])["Net_Profit"].sum().reset_index()
    net_month = net_month.sort_values("SortKey")

    with col2:
        st.markdown("### 📉 NET PROFIT")
        fig_net = px.line(net_month, x="MonthYear", y="Net_Profit", markers=True, color_discrete_sequence=["#006400"])
        fig_net.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_net, use_container_width=True)

        total_net = net_month["Net_Profit"].sum()
        
    

    # ✅ สร้างตัวแปรรวมยอด
    sales_total = df_filtered["Sales_Income"].sum()
    service_total = df_filtered["Service_Income"].sum() if "Service_Income" in df_filtered.columns else 0
    gp_total = df_filtered["GP"].sum() if "GP" in df_filtered.columns else 0

    # ✅ แสดงสัดส่วนรายได้ทั้งหมด
    sales_total = df_filtered["Sales_Income"].sum()
    service_total = df_filtered["Service_Income"].sum()
    total_income = sales_total + service_total

    # ✅ เตรียม DataFrame รายได้
    total_income_data = pd.DataFrame({
        "Category": ["Total Sales Income", "Total Service Income"],
        "Amount": [sales_total, service_total]
    })
    fig_income_pie = px.pie(
    total_income_data,
    names="Category",
    values="Amount",
    title="🥧 Total Income Distribution",
    color_discrete_sequence=["#003366", "#0055AA"]  # ✅ น้ำเงินเข้ม
)

    # ✅ เตรียม DataFrame ค่าใช้จ่าย
    expenses_data = {
        "Category": ["CGS", "Sales Expenses", "Management Expenses", "General Expenses", "Fixed Asset Expenses", "Taxes Expenses"],
        "Amount": [
            df_filtered["CGS"].sum() if "CGS" in df_filtered.columns else 0,
            df_filtered["Sales_Exp"].sum() if "Sales_Exp" in df_filtered.columns else 0,
            df_filtered["MA_Exp"].sum() if "MA_Exp" in df_filtered.columns else 0,
            df_filtered["GA_Exp"].sum() if "GA_Exp" in df_filtered.columns else 0,
            df_filtered["FA_Exp"].sum() if "FA_Exp" in df_filtered.columns else 0,
            df_filtered["Taxes_Exp"].sum() if "Taxes_Exp" in df_filtered.columns else 0
        ]
    }
    expenses_df = pd.DataFrame(expenses_data)
    fig_expenses_pie = px.pie(
    expenses_df,
    names="Category",
    values="Amount",
    title="💸 Total Expenses Distribution",
    color_discrete_sequence=["#CC5500", "#FF6600", "#FF9933", "#D2691E", "#A0522D", "#8B4513"]
)

    # ✅ แบ่งสองคอลัมน์ ซ้าย-ขวา
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 TOTAL INCOME DISTRIBUTION")
        st.plotly_chart(fig_income_pie, use_container_width=True)

    with col2:
        st.markdown("### 💸 TOTAL EXPENSES DISTRIBUTION")
        st.plotly_chart(fig_expenses_pie, use_container_width=True)

    # ✅ แบ่งคอลัมน์ซ้าย-ขวา
    col1, col2 = st.columns(2)

    # ✅ คำนวณรายได้จากการขายรายเดือน
    sales_month = df_filtered.groupby(["MonthYear", "SortKey"])["Sales_Income"].sum().reset_index()
    sales_month = sales_month.sort_values("SortKey", ascending=True)

    with col1:
        st.markdown("### 📦 SALES INCOME")
        
        fig1_bar = px.bar(sales_month, x="MonthYear", y="Sales_Income", title="📊 Sales")
        fig1_pie = px.pie(sales_month, values="Sales_Income", names="MonthYear", title="🥧 Sales")

        
        st.plotly_chart(fig1_bar, use_container_width=True)
        st.plotly_chart(fig1_pie, use_container_width=True)


    # ✅ คำนวณรายได้จากบริการรายเดือน
    if "Service_Income" in df_filtered.columns:
        service_month = df_filtered.groupby(["MonthYear", "SortKey"])["Service_Income"].sum().reset_index()
        service_month = service_month.sort_values("SortKey", ascending=True)

    with col2:
        st.markdown("### 🧾 SERVICES INCOME")
        
        fig2_bar = px.bar(service_month, x="MonthYear", y="Service_Income", title="📊 Services",color_discrete_sequence=["#006400"])
        fig2_pie = px.pie(service_month, values="Service_Income", names="MonthYear", title="🥧 Services")

        
        st.plotly_chart(fig2_bar, use_container_width=True)
        st.plotly_chart(fig2_pie, use_container_width=True)

    # ✅ ดาวน์โหลด Excel
    st.markdown("### 📥 Download Excel")
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='Filtered Data')
        sales_month.to_excel(writer, index=False, sheet_name='Sales Monthly')
        service_month.to_excel(writer, index=False, sheet_name='Service Monthly')
        gp_amount.to_excel(writer, index=False, sheet_name='GP Monthly')
        net_month.to_excel(writer, index=False, sheet_name='Net Profit Monthly')
    excel_buffer.seek(0)
    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer,
        file_name="business_performance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ใส่สีพื้นหลังฟ้าอ่อนให้กับหน้าหลัก
st.markdown(
    """
    <style>
    .stApp {
        background-color: #E7F2FD;  /* สีฟ้าอ่อน */
    }
    </style>
    """,
    unsafe_allow_html=True
)
# ใส่ CSS เพื่อปรับแต่ง padding ของกราฟ Plotly
st.markdown(
    """
    <style>
    .plotly-container {
        padding: 10px;  /* ปรับแต่ง padding ของกราฟ Plotly */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# แสดงเมนู admin ถ้า role คือ 'admin'
if st.session_state.get("role") == "admin":
        st.sidebar.page_link("pages/5_Admin.py", label="🛡️ Admin จัดการผู้ใช้")