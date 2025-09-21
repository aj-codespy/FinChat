import re
import feedparser
from datetime import datetime
from urllib.parse import quote_plus
from typing import List, Dict, Optional
from .database import COMPREHENSIVE_STOCKS_DATABASE
import streamlit as st

class EnhancedFinancialDataFetcher:
    """
    Handles all data retrieval from the in-memory JSON database and live sources.
    """
    def __init__(self):
        self.stocks_db = COMPREHENSIVE_STOCKS_DATABASE

    def get_all_stocks(self) -> List[Dict]:
        """Returns a single list of all stock dictionaries."""
        all_stocks = []
        for symbol, data in self.stocks_db.get("INDIAN_STOCKS", {}).items():
            all_stocks.append({**data, "symbol": symbol, "country": "India"})
        for symbol, data in self.stocks_db.get("US_STOCKS", {}).items():
             all_stocks.append({**data, "symbol": symbol, "country": "USA"})
        return all_stocks

    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get info for a single stock by its symbol."""
        if symbol in self.stocks_db.get("INDIAN_STOCKS", {}):
            return {**self.stocks_db["INDIAN_STOCKS"][symbol], "symbol": symbol, "country": "India"}
        if symbol in self.stocks_db.get("US_STOCKS", {}):
            return {**self.stocks_db["US_STOCKS"][symbol], "symbol": symbol, "country": "USA"}
        return None

    @st.cache_data(ttl=900) # Cache live news for 15 minutes
    def get_hybrid_news(_self, stock_info: dict, max_live_articles: int = 5) -> List[Dict]:
        """
        Creates a hybrid news list: curated news from the database plus live news from Google RSS.
        """
        # 1. Get curated news from the static database
        hybrid_news_list = stock_info.get("news", [])
        
        # 2. Fetch live news from Google News RSS
        company_name = stock_info.get("name")
        print(f"[INFO] Fetching LIVE news for: {company_name}")
        
        query = f'"{company_name}" stock financial earnings revenue'
        rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:max_live_articles]:
                live_article = {
                    "date": datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d") if entry.published_parsed else "Recent",
                    "source": entry.source.title if 'source' in entry else "Google News",
                    "headline": entry.title,
                    "summary": entry.get("summary", "No summary available.").split('<')[0] # Clean up HTML tags
                }
                # Avoid adding duplicate headlines
                if not any(d['headline'] == live_article['headline'] for d in hybrid_news_list):
                    hybrid_news_list.append(live_article)
        except Exception as e:
            print(f"[ERROR] Failed to fetch live news for {company_name}: {e}")

        print(f"[SUCCESS] Hybrid news fetch complete. Total articles: {len(hybrid_news_list)}")
        return hybrid_news_list

