import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from modules.database import get_stock_info, search_stocks

def get_stock_data(ticker, period="1mo"):
    """Fetches historical stock data for a given ticker."""
    if not ticker:
        print("❌ STOCK: Ticker cannot be empty.")
        return pd.DataFrame()
        
    print(f"📈 STOCK: Starting get_stock_data for {ticker}")
    try:
        stock = yf.Ticker(ticker)
        print(f"📈 STOCK: Created yfinance Ticker for {ticker}")
        hist = stock.history(period=period)
        if hist.empty:
            print(f"⚠️ STOCK: No historical data found for {ticker} for the period {period}.")
        else:
            print(f"📈 STOCK: Fetched {len(hist)} days of data for {ticker}")
        return hist
    except Exception as e:
        print(f"❌ STOCK: Error fetching stock data for {ticker}: {e}")
        return pd.DataFrame()

def get_company_info(ticker):
    """Fetches basic company information from yfinance and our local database."""
    if not ticker:
        print("❌ STOCK: Ticker cannot be empty.")
        return {}

    print(f"ℹ️ STOCK: Starting get_company_info for {ticker}")
    
    # Fetch from yfinance
    info_yf = {}
    try:
        stock = yf.Ticker(ticker)
        print(f"ℹ️ STOCK: Created yfinance Ticker for {ticker}")
        info_yf = stock.info
        print(f"ℹ️ STOCK: Fetched company info for {ticker} from yfinance")
    except Exception as e:
        print(f"⚠️ STOCK: Could not fetch company info for {ticker} from yfinance: {e}")

    # Fetch from our database
    info_db = get_stock_info(ticker)
    if not info_db:
        info_db = {}

    # Format market cap for readability
    market_cap = info_yf.get('marketCap', 0)
    if market_cap:
        if market_cap > 1_000_000_000_000:
            market_cap_str = f"${market_cap / 1_000_000_000_000:.2f} T"
        elif market_cap > 1_000_000_000:
            market_cap_str = f"${market_cap / 1_000_000_000:.2f} B"
        elif market_cap > 1_000_000:
            market_cap_str = f"${market_cap / 1_000_000:.2f} M"
        else:
            market_cap_str = f"${market_cap}"
    else:
        market_cap_str = "N/A"

    # Combine info, giving preference to yfinance data
    combined_info = {
        "Company Name": info_yf.get("longName") or info_db.get("name", "N/A"),
        "Sector": info_yf.get("sector") or info_db.get("sector", "N/A"),
        "Industry": info_yf.get("industry", "N/A"),
        "Market Cap": market_cap_str,
        "Website": info_yf.get("website", "N/A"),
        "P/E Ratio": info_yf.get("trailingPE", "N/A"),
        "Exchange": info_db.get("exchange", "N/A"),
    }
    
    # Final validation
    for key, value in combined_info.items():
        if not value:
            combined_info[key] = "N/A"
            
    print(f"ℹ️ STOCK: Successfully combined information for {ticker}.")
    return combined_info

def get_stock_suggestions(query):
    """Gets stock suggestions based on a search query."""
    if not query:
        return []
    
    results = search_stocks(query)
    suggestions = []
    for ticker, info in results.items():
        suggestions.append(f"{ticker} - {info['name']}")
        
    return suggestions

def create_stock_price_chart(stock_df, company_name):
    """Creates a candlestick chart for the stock price."""
    if not isinstance(stock_df, pd.DataFrame) or stock_df.empty:
        print("⚠️ CHART: Stock data is empty or invalid. Cannot create chart.")
        return None

    fig = go.Figure(data=[go.Candlestick(
        x=stock_df.index,
        open=stock_df['Open'],
        high=stock_df['High'],
        low=stock_df['Low'],
        close=stock_df['Close'],
        name='Price'
    )])

    fig.update_layout(
        title=f'{company_name} Stock Performance (Last Month)',
        yaxis_title='Stock Price (USD)',
        xaxis_title='Date',
        xaxis_rangeslider_visible=False,
        template="plotly_dark"
    )
    print(f"📊 CHART: Created stock price chart for {company_name}.")
    return fig

def overlay_sentiment_on_chart(fig, sentiment_df):
    """Overlays sentiment scores on the stock price chart."""
    if fig is None:
        print("⚠️ CHART: Figure is None. Cannot overlay sentiment.")
        return fig
    if not isinstance(sentiment_df, pd.DataFrame) or sentiment_df.empty:
        print("⚠️ CHART: Sentiment data is empty or invalid. Cannot overlay.")
        return fig
        
    sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    
    if 'Sentiment' not in sentiment_df.columns or 'Published At' not in sentiment_df.columns:
        print("❌ CHART: Sentiment data is missing required 'Sentiment' or 'Published At' columns.")
        return fig
        
    sentiment_df['Sentiment Score'] = sentiment_df['Sentiment'].map(sentiment_map)
    
    daily_sentiment = sentiment_df.groupby(pd.to_datetime(sentiment_df['Published At']).dt.date)['Sentiment Score'].mean().reset_index()

    fig.add_trace(go.Scatter(
        x=daily_sentiment['Published At'],
        y=daily_sentiment['Sentiment Score'],
        mode='lines+markers',
        name='Avg. News Sentiment',
        yaxis='y2',
        line=dict(color='#FFD700', dash='dot')
    ))

    fig.update_layout(
        yaxis2=dict(
            title="Sentiment Score",
            overlaying="y",
            side="right",
            range=[-1.1, 1.1],
            showgrid=False,
            tickfont=dict(color="#FFD700")
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    print("📊 CHART: Overlayed sentiment data on the chart.")
    return fig