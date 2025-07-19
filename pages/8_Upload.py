import streamlit as st
import pandas as pd
from sqlalchemy import text
import sys, os



# ✅ เพิ่ม path ของ utils/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))
from auth_utils import engine  # เรียกใช้ engine โดยตรง

st.set_page_config(page_title="📤 Upload CSV to PostgreSQL", layout="wide")
st.title("📤 Upload CSV to PostgreSQL")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("🔍 Preview Data")
    st.dataframe(df)

    table_name = st.text_input("Enter table name to insert data", value="VHAB1")

    if st.button("📥 Upload to Database"):
        try:
            with engine.connect() as conn:
                # ✅ ดึง Primary Keys ที่มีอยู่
                query = f'''
                    SELECT "Dept_Code", "Year", "Month", "Type"
                    FROM "{table_name}"
                '''
                existing = pd.read_sql(query, conn)

            # ✅ สร้างคีย์เพื่อเทียบความซ้ำ
            existing_keys = set(tuple(x) for x in existing[["Dept_Code", "Year", "Month", "Type"]].values)
            df["__key__"] = df.apply(lambda x: (x["Dept_Code"], int(x["Year"]), x["Month"], x["Type"]), axis=1)

            # ✅ แยกข้อมูลซ้ำ และใหม่
            df_duplicate = df[df["__key__"].isin(existing_keys)]
            df_new = df[~df["__key__"].isin(existing_keys)].drop(columns="__key__")

            if not df_duplicate.empty:
                st.warning(f"⚠️ พบข้อมูลซ้ำจำนวน {len(df_duplicate)} แถว ซึ่งจะไม่ถูกเพิ่มซ้ำเข้าไป")
                st.dataframe(df_duplicate)

            if df_new.empty:
                st.info("ℹ️ ไม่มีข้อมูลใหม่ให้อัปโหลด (ข้อมูลทั้งหมดซ้ำ)")
            else:
                df_new.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
                st.success(f"✅ อัปโหลดสำเร็จ {len(df_new)} แถวไปยัง `{table_name}`")

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

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