import yfinance as yf
import plotly.graph_objects as go

def get_stock_data(ticker, period="1mo"):
    """Fetches historical stock data for a given ticker."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def get_company_info(ticker):
    """Fetches basic company information."""
    stock = yf.Ticker(ticker)
    info = stock.info
    # Format market cap for readability
    market_cap = info.get('marketCap', 0)
    if market_cap > 1_000_000_000_000:
        market_cap_str = f"${market_cap / 1_000_000_000_000:.2f} T"
    elif market_cap > 1_000_000_000:
        market_cap_str = f"${market_cap / 1_000_000_000:.2f} B"
    elif market_cap > 1_000_000:
        market_cap_str = f"${market_cap / 1_000_000:.2f} M"
    else:
        market_cap_str = f"${market_cap}"


    return {
        "Company Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Market Cap": market_cap_str,
        "Website": info.get("website", "N/A"),
        "P/E Ratio": info.get("trailingPE", "N/A")
    }

def create_stock_price_chart(stock_df, company_name):
    """Creates a candlestick chart for the stock price."""
    if stock_df.empty:
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
    return fig

def overlay_sentiment_on_chart(fig, sentiment_df):
    """Overlays sentiment scores on the stock price chart."""
    if fig is None or sentiment_df.empty:
        return fig
        
    sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    sentiment_df['Sentiment Score'] = sentiment_df['Sentiment'].map(sentiment_map)
    
    daily_sentiment = sentiment_df.groupby(sentiment_df['Published At'].dt.date)['Sentiment Score'].mean().reset_index()

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
    return fig

