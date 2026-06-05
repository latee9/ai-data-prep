# connectors/bigquery_connector.py
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd

def run_bigquery_query(query: str):
    try:
        creds_dict = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        client = bigquery.Client(credentials=credentials, project=creds_dict["project_id"])
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"BigQuery error: {e}")
        return None