import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Ken 10X Signal App", layout="wide")

WATCHLIST = [
    "NVDA", "PLTR", "TSLA", "SMCI",
    "AMD", "AVGO", "MRVL", "LITE",
    "TEM", "PATH", "IONQ",
    "SOXL", "TQQQ",
    "ETH-USD", "SOL-USD"
]

st.title("🚀 Ken 10X Portfolio Signal App")
st.write("AI / Semiconductor / Crypto aggressive growth signal system")

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_signal(price, ma20, ma50, rsi_value):
    if price > ma20 > ma50 and 40 <= rsi_value <= 65:
        return "🟢 STRONG BUY"
    elif price >= ma50 and 30 <= rsi_value < 40:
        return "🟡 ACCUMULATE"
    elif rsi_value >= 70:
        return "🔴 TAKE PROFIT"
    elif price < ma50:
        return "⚪ WAIT / DEFENSE"
    else:
        return "🟢 HOLD"

@st.cache_data(ttl=900)
def load_data(ticker):
    data = yf.download(ticker, period="6mo", interval="1d")
    return data

rows = []

for ticker in WATCHLIST:
    try:
        data = load_data(ticker)

        if data is None or data.empty:
    raise Exception("No data")

        data["MA20"] = data["Close"].rolling(20).mean()
        data["MA50"] = data["Close"].rolling(50).mean()
        data["RSI"] = rsi(data["Close"])

        latest = data.dropna().iloc[-1]

        price = float(latest["Close"])
        ma20 = float(latest["MA20"])
        ma50 = float(latest["MA50"])
        rsi_value = float(latest["RSI"])

        signal = get_signal(price, ma20, ma50, rsi_value)

        rows.append({
            "Ticker": ticker,
            "Price": round(price, 2),
            "MA20": round(ma20, 2),
            "MA50": round(ma50, 2),
            "RSI": round(rsi_value, 1),
            "Signal": signal
        })

    except Exception as e:
        rows.append({
            "Ticker": ticker,
            "Price": "Error",
            "MA20": "",
            "MA50": "",
            "RSI": "",
            "Signal": "Check ticker"
        })

df = pd.DataFrame(rows)

st.subheader("📊 Daily Signal Dashboard")
st.dataframe(df, use_container_width=True)

selected = st.selectbox("Choose ticker to view chart", WATCHLIST)

chart_data = load_data(selected)
chart_data["MA20"] = chart_data["Close"].rolling(20).mean()
chart_data["MA50"] = chart_data["Close"].rolling(50).mean()
chart_data["RSI"] = rsi(chart_data["Close"])

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=chart_data.index,
    y=chart_data["Close"],
    name="Price"
))

fig.add_trace(go.Scatter(
    x=chart_data.index,
    y=chart_data["MA20"],
    name="MA20"
))

fig.add_trace(go.Scatter(
    x=chart_data.index,
    y=chart_data["MA50"],
    name="MA50"
))

fig.update_layout(
    title=f"{selected} Price + MA20 + MA50",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("📌 Rules")
st.write("""
🟢 STRONG BUY = Price > MA20 > MA50 and RSI 40–65  
🟡 ACCUMULATE = Price near/above MA50 and RSI 30–40  
🔴 TAKE PROFIT = RSI above 70  
⚪ WAIT / DEFENSE = Price below MA50  
""")

st.warning("This is educational only, not financial advice. Aggressive portfolios can lose 40–60% during bad markets.")
