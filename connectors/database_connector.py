import pandas as pd
from sqlalchemy import create_engine, text

def connect_db(db_type, host, port, database, user, password):
    if db_type == "PostgreSQL":
        conn_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    elif db_type == "MySQL":
        conn_str = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    else:
        raise ValueError("نوع قاعدة بيانات غير مدعوم")
    engine = create_engine(conn_str)
    return engine

def load_table(engine, table_name):
    return pd.read_sql_table(table_name, engine)

def load_query(engine, query):
    return pd.read_sql_query(query, engine)