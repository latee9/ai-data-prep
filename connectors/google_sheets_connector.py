# connectors/google_sheets_connector.py
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def load_google_sheet(sheet_url_or_id, worksheet_name=0):
    """
    Load data from Google Sheets.
    Requires service account credentials in st.secrets["gcp_service_account"].
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url_or_id) if "http" in sheet_url_or_id else client.open(sheet_url_or_id)
        worksheet = sheet.get_worksheet(worksheet_name) if isinstance(worksheet_name, int) else sheet.worksheet(worksheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Google Sheets error: {e}")
        return None