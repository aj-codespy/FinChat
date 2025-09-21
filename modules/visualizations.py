import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

@st.cache_data(ttl=900) # Cache live stock data for 15 minutes
def create_candlestick_chart(ticker: str, company_name: str):
    """
    Fetches live historical data from yfinance and creates a candlestick chart.
    Includes robust error handling.
    """
    print(f"[VIZ] Attempting to fetch live stock data for Ticker: {ticker}, Company: {company_name} from yfinance...")
    try:
        # Ensure correct ticker format for Indian stocks
        if ".NS" not in ticker and "India" in company_name:
             # This logic assumes company_name will imply country. A better check could be based on a country field.
             pass # In our case, the symbol from DB is already correct.
        
        print(f"[VIZ] Attempting yf.download for ticker: {ticker}, period: 3mo")
        stock_df = yf.download(ticker, period="3mo", progress=False)
        
        # Flatten multi-level columns if yfinance returns them
        if isinstance(stock_df.columns, pd.MultiIndex):
            stock_df.columns = stock_df.columns.droplevel(1)

        print(f"[VIZ] Type of stock_df for {ticker}: {type(stock_df)}")
        
        print(f"[VIZ] DataFrame shape for {ticker}: {stock_df.shape}")
        if stock_df.empty:
            print(f"[WARN] yfinance returned an EMPTY DataFrame for {ticker}. Data fetching FAILED.")
            st.warning(f"Could not fetch live price data for **{ticker}** from Yahoo Finance. The ticker may be incorrect or the service may be temporarily unavailable.", icon="⚠️")
            return None
        else:
            print(f"[INFO] Successfully fetched {len(stock_df)} data points for {ticker}. Data fetching SUCCESSFUL.")
            print(f"[VIZ] stock_df columns for {ticker}: {stock_df.columns.tolist()}")
            print(f"[VIZ] stock_df dtypes for {ticker}:\n{stock_df.dtypes}")
            print(f"[VIZ] First 5 rows of Open, High, Low, Close for {ticker}:\n{stock_df[['Open', 'High', 'Low', 'Close']].head()}")

        fig = go.Figure(data=[go.Candlestick(
            x=stock_df.index,
            open=stock_df['Open'],
            high=stock_df['High'],
            low=stock_df['Low'],
            close=stock_df['Close'],
            name='Price'
        )])
        
        fig.update_layout(
            title=f'{company_name} Stock Performance (Last 3 Months)',
            yaxis_title='Stock Price',
            xaxis_rangeslider_visible=False,
            template="plotly_dark"
        )
        print(f"[SUCCESS] Candlestick chart created for {ticker}.")
        return fig
    except Exception as e:
        print(f"[ERROR] yfinance failed for {ticker}: {e}. Data fetching FAILED.")
        st.error(f"An error occurred while fetching live stock data: {e}", icon="🚨")
        return None

def create_sentiment_pie_chart(analyzed_news: list):
    """
    Creates a pie chart from the news sentiment data.
    """
    if not analyzed_news:
        return None
    
    print("[VIZ] Creating sentiment pie chart...")
    df = pd.DataFrame(analyzed_news)
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    
    fig = px.pie(
        sentiment_counts,
        names='sentiment',
        values='count',
        title='Hybrid News Sentiment Breakdown',
        color='sentiment',
        color_discrete_map={'Positive': '#2ca02c', 'Negative': '#d62728', 'Neutral': '#7f7f7f'}
    )
    fig.update_layout(template="plotly_dark", legend_title_text='Sentiment')
    return fig

def create_news_sentiment_df(analyzed_news: list) -> pd.DataFrame:
    """
    Creates a DataFrame for displaying the news sentiment table.
    """
    if not analyzed_news:
        return pd.DataFrame()
        
    print("[VIZ] Creating news sentiment DataFrame...")
    df = pd.DataFrame(analyzed_news)
    # Ensure all columns are present and in order
    df = df.reindex(columns=['headline', 'sentiment', 'summary', 'date', 'source'], fill_value="N/A")
    return df[['headline', 'sentiment', 'summary', 'date', 'source']]
