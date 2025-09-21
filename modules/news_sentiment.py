import os
import pandas as pd
import plotly.express as px
import requests
import google.generativeai as genai
from datetime import datetime, timedelta, date
import json
import streamlit as st

# --- Configuration ---
# It's recommended to set API keys as environment variables
# For Streamlit sharing, use st.secrets
FINNHUB_API_KEY = st.secrets.get("FINNHUB_API_KEY", os.environ.get('FINNHUB_API_KEY'))
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get('GEMINI_API_KEY'))

# Initialize clients if keys are available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_sentiment_and_summary_from_gemini(headline, content, company_name):
    """
    Analyzes sentiment and generates a summary for a news article using a single Gemini API call.
    """
    if not GEMINI_API_KEY:
        return {"sentiment": "neutral", "summary": "API key not configured."}
    if not headline or not isinstance(headline, str):
        return {"sentiment": "neutral", "summary": "Invalid headline."}

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyze the sentiment of the following news article about {company_name}.
    The sentiment must be strictly one of: 'positive', 'negative', or 'neutral'.
    Then, provide a concise one-sentence summary of the article.
    
    Format your response as a valid JSON object with two keys: "sentiment" and "summary".

    Headline: "{headline}"
    Content: "{content}"
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's valid JSON
        cleaned_response = response.text.strip()
        
        # Remove markdown code blocks if present
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        
        # Try to find JSON object in the response
        start_idx = cleaned_response.find('{')
        end_idx = cleaned_response.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = cleaned_response[start_idx:end_idx + 1]
            result = json.loads(json_str)
        else:
            # Fallback: try to parse the whole response
            result = json.loads(cleaned_response)
        
        # Validate keys
        if "sentiment" not in result or "summary" not in result:
             return {"sentiment": "neutral", "summary": "Invalid format from API."}
        return result
    except Exception as e:
        print(f"Error processing article with Gemini: {e}")
        return {"sentiment": "neutral", "summary": "Could not process article."}


def fetch_and_process_news(company_name, days=7):
    """
    Fetches news, analyzes sentiment, and generates summaries for a company using Finnhub and Gemini.
    """
    print(f"🔍 NEWS: Starting fetch_and_process_news for {company_name}")
    
    if not company_name or not FINNHUB_API_KEY:
        print(f"❌ NEWS: Missing company_name or FINNHUB_API_KEY")
        st.error("Finnhub API key is not configured. Please set it as an environment variable or Streamlit secret.")
        return pd.DataFrame()

    # Calculate date range
    today = datetime.now().date()
    last_week = today - timedelta(days=days)
    print(f"📅 NEWS: Date range: {last_week} to {today}")

    try:
        # Fetch news from Finnhub using the simpler approach
        url = f"https://finnhub.io/api/v1/company-news?symbol={company_name.upper()}&from={last_week}&to={today}&token={FINNHUB_API_KEY}"
        print(f"🌐 NEWS: Fetching from URL: {url[:100]}...")
        response = requests.get(url)
        response.raise_for_status()
        all_articles = response.json()
        print(f"✅ NEWS: Fetched {len(all_articles)} raw articles from Finnhub")
        
        # Handle case where no articles are found
        if not all_articles:
            print("⚠️ NEWS: No articles found, returning empty DataFrame")
            return pd.DataFrame(columns=['Published At', 'Headline', 'Sentiment', 'Summary', 'URL'])
            
    except Exception as e:
        print(f"❌ NEWS: Error fetching news from Finnhub: {e}")
        st.error(f"Error fetching news from Finnhub: {e}")
        return pd.DataFrame(columns=['Published At', 'Headline', 'Sentiment', 'Summary', 'URL'])

    processed_articles = []
    print(f"🔄 NEWS: Processing {len(all_articles)} articles...")
    
    for i, article in enumerate(all_articles):
        headline = article.get('headline', '')
        content = article.get('summary', '')
        url = article.get('url', '')
        published_at = pd.to_datetime(article.get('datetime'), unit='s')
        
        print(f"📰 NEWS: Processing article {i+1}: {headline[:50]}...")

        if headline and content and "[Removed]" not in headline:
            print(f"🤖 NEWS: Analyzing sentiment for article {i+1}")
            analysis = get_sentiment_and_summary_from_gemini(headline, content, company_name)
            
            processed_articles.append({
                'Published At': published_at,
                'Headline': headline,
                'Sentiment': analysis.get('sentiment', 'neutral'),
                'Summary': analysis.get('summary', 'N/A'),
                'URL': url
            })
            print(f"✅ NEWS: Added article {i+1} with sentiment: {analysis.get('sentiment', 'neutral')}")
            # Limit to the top 10 most relevant processed articles
            if len(processed_articles) >= 10:
                print(f"🛑 NEWS: Reached limit of 10 articles, stopping processing")
                break
        else:
            print(f"⏭️ NEWS: Skipping article {i+1} (no headline/content or removed)")

    print(f"📊 NEWS: Processed {len(processed_articles)} articles total")
    
    if not processed_articles:
        print("⚠️ NEWS: No processed articles, returning empty DataFrame")
        return pd.DataFrame()

    df = pd.DataFrame(processed_articles)
    df['Date'] = df['Published At'].dt.date
    print(f"✅ NEWS: Returning DataFrame with shape {df.shape}")
    return df

def create_sentiment_pie_chart(df):
    """Creates a pie chart of sentiment distribution."""
    if df.empty or 'Sentiment' not in df.columns:
        return None
    sentiment_counts = df['Sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    fig = px.pie(
        sentiment_counts,
        names='Sentiment',
        values='Count',
        title='News Sentiment Distribution',
        color='Sentiment',
        color_discrete_map={'positive': '#2ca02c', 'negative': '#d62728', 'neutral': '#7f7f7f'}
    )
    fig.update_layout(template="plotly_dark", legend_title_text='Sentiment')
    return fig

def create_sentiment_trend_chart(df):
    """Creates a line chart showing sentiment trends over time."""
    if df.empty or 'Date' not in df.columns or 'Sentiment' not in df.columns:
        return None
    
    sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    df['Sentiment Score'] = df['Sentiment'].map(sentiment_map)
    
    trend_data = df.groupby('Date')['Sentiment Score'].mean().reset_index()
    
    fig = px.line(
        trend_data,
        x='Date',
        y='Sentiment Score',
        title='Sentiment Trend Over Last 7 Days',
        labels={'Sentiment Score': 'Average Sentiment'}
    )
    fig.add_hline(y=0, line_dash="dash", line_color="grey")
    fig.update_layout(template="plotly_dark")
    return fig

