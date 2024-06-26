import streamlit as st
import datetime
from pathlib import Path
from streamlit.runtime.uploaded_file_manager import UploadedFile
import pandas as pd

import db

def get_recent_logs(limit=10):
    session = db.create_database()  # Create or connect to the database
    logs = session.query(db.Log).order_by(db.Log.datetime.desc()).limit(limit).all()
    session.close()  # Close the database session
    return logs

DIR = Path(".")

st.title("SOD vs Proform Checks")

cd, rc = st.tabs(["Checks Status Dashboard", "Run Checks"])

date: datetime.date = rc.date_input(label="Select Date", value=datetime.date.today())
mr, urc = rc.tabs(["Manual Run",  "Upload and Run Checks"])



with cd:
    with st.expander(":alarm_clock: Scheduler Updates", expanded=True):
        st.write("Schduler updates")
    with st.expander(":memo: Logs", expanded=True):
        logs = pd.DataFrame(map(lambda x: x.__dict__, get_recent_logs()))
        selected_cols = filter(lambda x: not x.startswith("_"), logs.columns)
        st.dataframe(logs[selected_cols], hide_index=True, use_container_width=True)

with mr: 
    file_list = pd.DataFrame({"file": DIR.iterdir()})
    if not file_list.empty:
        st.write(f"Files for the selected date ({date}) is available")
        st.caption("")
        st.dataframe(file_list, hide_index=True, on_select="ignore")
    else:
        st.error("Files not available for the selected date. Please try manual uplaod!")


with urc:
    sod_file: UploadedFile = st.file_uploader(label="Upload SOD file")
    proforma_file: UploadedFile = st.file_uploader(label="Upload Proforma file")

    if sod_file:
        st.write(sod_file.name)

        st.write(sod_file)
    st.write(f"Selected date: {date}")
    st.write(st.session_state)
    
rc_btn, mail_btn = rc.columns(2)
rc_btn.button("Run Checks", use_container_width=True)
mail_btn.button("Send Results", use_container_width=True)