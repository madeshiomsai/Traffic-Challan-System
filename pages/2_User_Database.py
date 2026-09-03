import sqlite3

import pandas as pd
import streamlit as st

from config import USER_DB

st.set_page_config(page_title="Registered Users", page_icon="👥", layout="wide")


def get_users():
    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, vehicle_reg, vehicle_type, vehnum, mobile
        FROM users
        ORDER BY id
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


st.markdown("## 👥 Registered Vehicle Owners")
st.caption("Owner and vehicle details retrieved from the users database.")

try:
    users = get_users()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if not users:
    st.warning("No registered users found.")
    st.stop()

df = pd.DataFrame(users, columns=[
    "ID", "Name", "Vehicle Registration", "Vehicle Type", "Vehicle ID", "Mobile",
])

search = st.text_input("🔎 Search by name, vehicle registration, or mobile")
if search:
    mask = df.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False))
    df = df[mask.any(axis=1)]

st.success(f"{len(df)} registered driver(s) found.")
st.dataframe(df, use_container_width=True, hide_index=True)
