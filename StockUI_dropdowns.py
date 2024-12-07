import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# App title
st.title("Stock Prediction App")

# Industry and Stock Data
industries = {
    "Energy": ["RELIANCE.NS", "NTPC.NS", "ONGC.NS", "IOCL.NS", "BPCL.NS", "GAIL.NS", "TATAPOWER.NS", "ADANIGREEN.NS", "MGL.NS", "HINDPETRO.NS",
               "APOLLOPIPE.NS", "BIRLACORPN.NS", "CIL.NS", "HINDALCO.NS", "SAIL.NS", "JSWSTEEL.NS", "TATAMOTORS.NS", "VEDANTA.NS", "OIL.NS", "NHPC.NS"],
    "Pharmacy": ["SUNPHARMA.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS", "DRREDDY.NS", "WOKHARDT.NS", "ABBOTINDIA.NS", "PIRAMAL.NS", "MOTHERSONSumi.NS", "ZYDUSLIFE.NS",
                 "ALKEM.NS", "BIOCON.NS", "NATCOPHARMA.NS", "FDC.NS", "SYNGENE.NS", "MANKIND.NS", "GLENMARK.NS", "CADILAHC.NS", "TORNTPHARM.NS", "KOTAKPHARMA.NS"],
    "Automobile": ["MARUTI.NS", "TATAMOTORS.NS", "MAHINDRA.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "MOTHERSUMI.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "AUBANK.NS", "BOSCHLTD.NS",
                   "EXIDEIND.NS", "INDIGO.NS", "OLECTRA.NS", "HERO.MOTOCO.NS", "RECLTD.NS", "GMDCLTD.NS", "SONALIKA.NS", "TATAPOWER.NS", "BHEL.NS", "HAVELLS.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "IDFCFIRSTB.NS", "INDUSINDBK.NS", "YESBANK.NS", "BANKBARODA.NS", "PNB.NS",
                "BOMDIA.NS", "RBLBANK.NS", "FEDERALBNK.NS", "SOUTHBANK.NS", "CANBK.NS", "IIB.NS", "MUTHOOTFIN.NS", "LICHSGFIN.NS", "NHB.NS", "BANDHANBNK.NS"],
    "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "MINDTREE.NS", "LTTS.NS", "COFORGE.NS", "CYIENT.NS", "NIIT.NS",
              "MATRIXLABS.NS", "BIRLASOFT.NS", "KPITTECH.NS", "ZENSARTECH.NS", "OCTALIT.NS", "TATAELXSI.NS", "SASKEN.NS", "3IINFOTECH.NS", "INTELLECT.NS"]
}

# First Dropdown: Select Industry
selected_industry = st.selectbox("Select Industry", ["Select an Industry"] + list(industries.keys()))

# Conditional: Display stock dropdown only when industry is selected
if selected_industry != "Select an Industry":
    # Second Dropdown: Select Stock based on selected industry
    selected_stock = st.selectbox("Select Stock", industries[selected_industry])

    # Fetch stock data function with a fixed date range
    def fetch_stock_data(symbol):
        try:
            # Automatically set the date range (last 5 years)
            end_date = pd.to_datetime("today")
            start_date = end_date - pd.DateOffset(years=5)
            
            # Fetch data from Yahoo Finance
            data = yf.download(symbol, start=start_date, end=end_date)
            data.reset_index(inplace=True)
            return data
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return None

    # Fetch the selected stock's data
    stock_data = fetch_stock_data(selected_stock)

    if stock_data is not None:
        # Display stock data
        st.subheader(f"Stock Data for {selected_stock}")
        st.write(stock_data.tail())

        # Plot stock price
        st.subheader("Historical Stock Price")
        fig, ax = plt.subplots()
        ax.plot(stock_data['Date'], stock_data['Close'], label='Close Price')
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)

        # Moving average calculation
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
        st.error("Unable to fetch stock data. Please check the symbol or connection.")
