# Nifty 50 Volatility Analyzer (Streamlit + Plotly version)

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import date

# ---------------------- UI CONFIGURATION ----------------------
st.set_page_config(page_title="Nifty 50 Volatility Analyzer", layout="wide")

# Apply Streamlit styling to fix chart overflow
st.markdown("""
    <style>
        .element-container iframe {
            max-width: 100% !important;
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Nifty & Bank Nifty Stock Volatility Analyzer")

# ---------------------- TICKER DATA ----------------------
nifty_50_symbols = {
    "Nifty 50":"^NSEI",
    "ADANI ENTERPRISES": "ADANIENT.NS", "ADANI PORTS": "ADANIPORTS.NS",
    "APOLLO HOSPITALS": "APOLLOHOSP.NS", "ASIAN PAINTS": "ASIANPAINT.NS",
    "AXIS BANK": "AXISBANK.NS", "BAJAJ AUTO": "BAJAJ-AUTO.NS",
    "BAJAJ FINANCE": "BAJFINANCE.NS", "BAJAJ FINSERV": "BAJAJFINSV.NS",
    "BHARTI AIRTEL": "BHARTIARTL.NS", "BPCL": "BPCL.NS",
    "BRITANNIA": "BRITANNIA.NS", "CIPLA": "CIPLA.NS",
    "COAL INDIA": "COALINDIA.NS", "DIVIS LABORATORIES": "DIVISLAB.NS",
    "DR REDDY'S LAB": "DRREDDY.NS", "EICHER MOTORS": "EICHERMOT.NS",
    "GRASIM": "GRASIM.NS", "HCL TECH": "HCLTECH.NS",
    "HDFC BANK": "HDFCBANK.NS", "HDFC LIFE": "HDFCLIFE.NS",
    "HEROMOTOCO": "HEROMOTOCO.NS", "HINDALCO": "HINDALCO.NS",
    "HINDUSTAN UNILEVER": "HINDUNILVR.NS", "ICICI BANK": "ICICIBANK.NS",
    "INDUSIND BANK": "INDUSINDBK.NS", "INFOSYS": "INFY.NS",
    "ITC": "ITC.NS", "JSW STEEL": "JSWSTEEL.NS",
    "KOTAK MAHINDRA BANK": "KOTAKBANK.NS", "LTIMINDTREE": "LTIM.NS",
    "L&T": "LT.NS", "M&M": "M&M.NS", "MARUTI SUZUKI": "MARUTI.NS",
    "NESTLE INDIA": "NESTLEIND.NS", "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS", "PIDILITE INDUSTRIES": "PIDILITIND.NS",
    "POWER GRID CORP": "POWERGRID.NS", "RELIANCE": "RELIANCE.NS",
    "SBIN": "SBIN.NS", "SBI LIFE": "SBILIFE.NS",
    "SUN PHARMA": "SUNPHARMA.NS", "TATA CONSUMER": "TATACONSUM.NS",
    "TATA MOTORS": "TATAMOTORS.NS", "TATA STEEL": "TATASTEEL.NS",
    "TCS": "TCS.NS", "TECH MAHINDRA": "TECHM.NS",
    "TITAN": "TITAN.NS", "ULTRATECH CEMENT": "ULTRACEMCO.NS",
    "UPL": "UPL.NS", "WIPRO": "WIPRO.NS"
}

bank_nifty_symbols = {
    "AU Small Finance Bank": "AUBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bandhan Bank": "BANDHANBNK.NS",
    "Bank of Baroda": "BANKBARODA.NS",
    "Federal Bank": "FEDERALBNK.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "IDFC First Bank": "IDFCFIRSTB.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Punjab National Bank": "PNB.NS",
    "State Bank of India": "SBIN.NS"
}

combined_symbols = {**nifty_50_symbols, **bank_nifty_symbols}

# ---------------------- SIDEBAR CONTROLS ----------------------
st.sidebar.header("Select Options")

stock = st.sidebar.selectbox("Choose a Stock (Nifty or Bank Nifty)", list(combined_symbols.keys()))
symbol = combined_symbols[stock]

start_date = st.sidebar.date_input("Start Date", date(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

# ---------------------- FETCH STOCK DATA ----------------------
data = yf.download(symbol, start=start_date, end=end_date, interval="1d", progress=False, threads=False)

if data.empty or 'Close' not in data.columns:
    st.error("No valid closing price data found for this stock and date range.")
    st.stop()

# Clean and prepare data
data = data[['Open', 'High', 'Low', 'Close']].dropna()
data.index = pd.to_datetime(data.index)
data = data[~data.index.duplicated()]
data = data.sort_index()



# ---------------------- CALCULATE VOLATILITY ----------------------
try:
    data['Rolling Mean'] = data['Close'].rolling(window=20).mean()
    data['Rolling Std'] = data['Close'].rolling(window=20).std()
    data['Volatility'] = data['Rolling Std'] / data['Rolling Mean']

    if 'Volatility' not in data.columns or data['Volatility'].dropna().empty:
        st.warning("Volatility could not be calculated. Try selecting a longer date range.")
        st.stop()

except Exception as e:
    st.error(f"Error during volatility calculation: {e}")
    st.stop()



# ---------------------- PLOTLY VOLATILITY CHART ----------------------
st.subheader(f"{stock} - Volatility Trend")

if 'Volatility' in data.columns and not data['Volatility'].isnull().all():
    vol_fig = go.Figure()
    vol_fig.add_trace(go.Scatter(x=data.index, y=data['Volatility'], mode='lines', name='Volatility'))
    vol_fig.add_shape(type='line', x0=data.index[0], x1=data.index[-1],
                      y0=data['Volatility'].quantile(0.75), y1=data['Volatility'].quantile(0.75),
                      line=dict(color='red', dash='dash'), name='High Vol Threshold')
    vol_fig.update_layout(title="Volatility Over Time", xaxis_title="Date", yaxis_title="Volatility",
                          autosize=True, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(vol_fig, use_container_width=True)
else:
    st.warning("Not enough data to plot volatility chart.")
