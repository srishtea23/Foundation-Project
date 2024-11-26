

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# App title
st.title("Stock Prediction App")

st.sidebar.header("Stock Prediction Settings")
stock_symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, MSFT)", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))





def fetch_stock_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

stock_data = fetch_stock_data(stock_symbol, start_date, end_date)

if stock_data is not None:
    st.subheader(f"Stock Data for {stock_symbol.upper()}")
    st.write(stock_data.tail())

    # Plot stock price
    st.subheader("Historical Stock Price")
    fig, ax = plt.subplots()
    ax.plot(stock_data['Date'], stock_data['Close'], label='Close Price')
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    st.pyplot(fig)

    # Moving average prediction
    st.subheader("Moving Average Prediction")
    ma_window = st.slider("Select Moving Average Window", 5, 50, 20)
    stock_data['MA'] = stock_data['Close'].rolling(window=ma_window).mean()

    # Plot moving average
    fig, ax = plt.subplots()
    ax.plot(stock_data['Date'], stock_data['Close'], label='Close Price')
    ax.plot(stock_data['Date'], stock_data['MA'], label=f"{ma_window}-Day MA", linestyle='--')
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    st.pyplot(fig)

    # Display forecast message
    st.write(
        f"The {ma_window}-day moving average can help identify trends. Use it with caution as it's a basic predictive measure."
    )
else:
    st.error("Unable to fetch stock data. Please check the symbol or date range.")