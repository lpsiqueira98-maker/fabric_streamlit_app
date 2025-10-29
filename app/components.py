# app/components.py
# componentes reutilizáveis (ex: download csv)

import streamlit as st
import pandas as pd

def df_to_csv_download(df: pd.DataFrame, filename: str="export.csv"):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("baixar CSV", data=csv, file_name=filename, mime="text/csv")
