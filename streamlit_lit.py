import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import boto3
from dotenv import load_dotenv
import os
from io import StringIO
import numpy as np
import joblib
from PIL import Image
import io
from datetime import datetime

load_dotenv()

# Access the environment variables for AWS credentials
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
BUCKET_NAME = 'isbfinanceproject'

# Define tickers
tickers = {
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


# App title
st.set_page_config(page_title="Stock Prediction App", page_icon="📈", layout="wide")
st.title("Stock Prediction App")

# Updated styling for lighter background
st.markdown("""
    <style>
        body {
            background-color: #FAFAFA; /* Light background */
            font-family: 'Arial', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #F0F0F5; /* Light grey for sidebar */
        }
        h1 {
            color: #2E4053; /* Darker shade for headings */
            font-family: 'Arial', sans-serif;
        }
        h2, h3 {
            color: #34495E;
        }
        .stMarkdown h3 {
            color: #1F618D;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for stock selection
st.sidebar.header("Stock Prediction Settings")

# Select vertical
stock_vertical = st.sidebar.selectbox("Select Vertical", list(tickers.keys()))

# Select stock symbol from vertical
stock_symbol = st.sidebar.selectbox("Select Stock Symbol", tickers[stock_vertical])

# Select prediction type
prediction_type = st.sidebar.radio("Select Prediction Type", ["Short-Term", "Long-Term"])
if prediction_type == "Short-Term":
    start_date = pd.to_datetime("today") - pd.Timedelta(days=30)
else:
    start_date = pd.to_datetime("2020-01-01")
end_date = pd.to_datetime("today")

# Function to fetch stock data
def fetch_stock_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Fetch and display stock data
stock_data = fetch_stock_data(stock_symbol, start_date, end_date)

# Function to fetch images from S3
def fetch_image_from_s3(bucket, key):
    s3 = boto3.client(
        's3',
          aws_access_key_id=AWS_ACCESS_KEY_ID,
          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
          region_name=AWS_DEFAULT_REGION
    )
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        return Image.open(io.BytesIO(image_data))
    except Exception as e:
        st.error(f"Error fetching image: {e}")
        return None

def get_stock_news_yfinance(ticker):
    stock = yf.Ticker(ticker)
    try:
        news = stock.news
    except AttributeError:
        return "Failed to retrieve news. Ensure the `yfinance` version supports this feature."

    if not news:
        return "No news articles found for this stock."

    formatted_news = []
    for article in news[:5]:
        title = article.get("title", "No title available")
        link = article.get("link", "No link available")
        publisher = article.get("publisher", "Unknown source")
        formatted_news.append({"title": title, "publisher": publisher, "link": link})
    
    return formatted_news

def fetch_stock_metrics(ticker):
    try:
        stock_info = yf.Ticker(ticker)
        metrics = {
            "P/E Ratio": stock_info.info.get('trailingPE', 'N/A'),
            "Beta (5Y Monthly)": stock_info.info.get('beta', 'N/A'),
            "Market Cap": stock_info.info.get('marketCap', 'N/A'),
            "Forward P/E": stock_info.info.get('forwardPE', 'N/A'),
            "EPS (TTM)": stock_info.info.get('trailingEps', 'N/A'),
            "Price": stock_info.info.get('previousClose', 'N/A'),
            "Sector": stock_info.info.get('sector', 'N/A'),
            "Industry": stock_info.info.get('industry', 'N/A'),
            "Date": datetime.now().strftime('%Y-%m-%d') 
        }
        return metrics
    except Exception as e:
        st.error(f"Error fetching metrics for {ticker}: {e}")
        return None

if stock_data is not None:
    metrics = fetch_stock_metrics(stock_symbol)
    st.subheader(f"{stock_symbol.upper()}")
    st.markdown(f"*Data as of: {metrics['Date']}*", unsafe_allow_html=True)
    closing_price = metrics['Price']
    st.markdown(f"### **₹{closing_price}**", unsafe_allow_html=True)

    st.subheader(f"Financial Metrics")
    if metrics:
        st.markdown(
            f"""
            <div style="background-color:#34495E; padding:30px; border-radius:15px; color:white; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                <h3 style="text-align:center; color:#FFD700;">Key Financial Metrics</h3>
                <ul style="list-style:none; padding-left:0; font-family: 'Arial', sans-serif; line-height: 1.8; font-size: 18px;">
                    <li style="padding-bottom: 10px;">P/E Ratio: {metrics['P/E Ratio']}</li>
                    <li style="padding-bottom: 10px;">Beta (5Y Monthly): {metrics['Beta (5Y Monthly)']}</li>
                    <li style="padding-bottom: 10px;">Market Cap: {metrics['Market Cap']}</li>
                    <li style="padding-bottom: 10px;">Forward P/E: {metrics['Forward P/E']}</li>
                    <li style="padding-bottom: 10px;">EPS (TTM): {metrics['EPS (TTM)']}</li>
                    <li style="padding-bottom: 10px;">Sector: {metrics['Sector']}</li>
                    <li style="padding-bottom: 10px;">Industry: {metrics['Industry']}</li>
                    <li style="padding-bottom: 10px;">Date: {metrics['Date']}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No financial metrics available for the selected stock.")

    forecast_image_key = (
        f"Results/{stock_vertical}/{stock_symbol}/7_day_forecast.png"
        if prediction_type == "Short-Term"
        else f"Results/{stock_vertical}/{stock_symbol}/30_day_forecast.png"
    )
    nifty_compare_image_key = f"Results/{stock_vertical}/{stock_symbol}/nifty_compare.png"

    st.subheader("Forecast and Comparison")
    forecast_image = fetch_image_from_s3(BUCKET_NAME, forecast_image_key)
    nifty_compare_image = fetch_image_from_s3(BUCKET_NAME, nifty_compare_image_key)

    if forecast_image:
        st.image(forecast_image, caption="Forecast Image", use_container_width=True)
    else:
        st.error("Forecast image not found.")

    if nifty_compare_image:
        st.image(nifty_compare_image, caption="Nifty Comparison", use_container_width=True)
    else:
        st.error("Nifty comparison image not found.")
    
    st.header(f"Latest News for {stock_symbol}")
    news = get_stock_news_yfinance(stock_symbol)

    if isinstance(news, list):
        for idx, article in enumerate(news, 1):
            # st.markdown(f"### News {idx}")
            st.markdown(f"### {article['title']}")
            st.markdown(f"**Publisher:** {article['publisher']}")
            st.markdown(f"[Read more]({article['link']})", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.warning(news)
else:
    st.error("Unable to fetch stock data.")
