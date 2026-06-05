# connectors/mongodb_connector.py
import streamlit as st
from pymongo import MongoClient
import pandas as pd

def load_mongodb_collection(uri, database_name, collection_name):
    try:
        client = MongoClient(uri)
        db = client[database_name]
        collection = db[collection_name]
        data = list(collection.find({}))
        if data:
            df = pd.DataFrame(data)
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            return df
        return None
    except Exception as e:
        st.error(f"MongoDB error: {e}")
        return None