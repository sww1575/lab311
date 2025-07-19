import yfinance as yf 
import pandas as pd 
import streamlit as st 
import matplotlib.pyplot as plt 
from enum import Enum

@st.cache_data
def load_data(tickers):
    df = yf.download(tickers, start='2020-01-01', end='2024-12-31', auto_adjust=False)['Close']
    df.columns = df.columns.str.replace('-', '_', regex=False)
    return df

tickers = ['BTC-USD', 'SOL-USD', 'ETH-USD', 'BNB-USD', 'LTC-USD', 'LINK-USD', 'AAVE-USD', 'MKR-USD']

data = load_data(tickers)

tickers = data.columns.tolist()

option = st.multiselect(
    "Select Asset",
    tickers,
    default=[tickers[0]]
)


st.title("Prices")

# Slider date 
first_date = data.index.min().to_pydatetime()
latest_date = data.index.max().to_pydatetime()

time_interval = st.slider(
    'Select time range',
    min_value=first_date,
    max_value=latest_date,
    value= (first_date, latest_date),
    format="MM/DD/YY"
)

@st.fragment
def plot_chart():
    if option:
        start_date, end_date = time_interval 
        _data = data.loc[start_date:end_date]
        chart_data =  _data[option]
        st.session_state.data = chart_data
        
        st.table(chart_data.head())

plot_chart()