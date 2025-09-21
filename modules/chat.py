import os
import re
import json
import google.generativeai as genai
import streamlit as st
from .data_fetcher import EnhancedFinancialDataFetcher
from googletrans import Translator

# --- Configuration ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)



async def translate_text(text: str, target_language_code: str, source_language: str = "auto") -> str:
    """Translates text using the Google Translate library."""
    if not text or target_language_code == 'en': return text
    try:
        translator = Translator()
        translation = await translator.translate(text, dest=target_language_code, src=source_language)
        print(f"[CHAT] Type of translation object: {type(translation)}")
        print(f"[CHAT] Translation object: {translation}")
        return translation.text
    except Exception as e: return f"Translation Error: {e}"

@st.cache_data(ttl=1800)
def generate_stock_summary(stock_info: dict) -> str:
    """Generates a concise summary for a single stock for the dashboard."""
    if not GEMINI_API_KEY: return "Gemini API key is not configured."
    model = genai.GenerativeModel('gemini-1.5-flash')
    news_context = "\n".join([f"- {item['headline']}: {item['summary']}" for item in stock_info.get('news', [])])
    prompt = f"Based on the following data and news for {stock_info['name']}, provide a concise, analytical summary (3-4 sentences) for a financial dashboard. Start with a concluding sentence about its current position.\n\nDATA:\n- Sector: {stock_info['sector']}\n- P/E Ratio: {stock_info['pe_ratio']}\n\nNEWS:\n{news_context}\n\nSUMMARY:"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"Could not generate AI summary: {e}"

@st.cache_data(ttl=1800)
def analyze_news_sentiment(news_list: list) -> list:
    """Analyzes sentiment for a list of news items."""
    if not news_list or not GEMINI_API_KEY: return []
    model = genai.GenerativeModel('gemini-1.5-flash')
    headlines_to_analyze = "\n".join([f"Article {i+1}: {item['headline']}" for i, item in enumerate(news_list)])
    prompt = f'Analyze the sentiment for each news headline below as "Positive", "Negative", or "Neutral". Return a valid JSON object like {{"Article 1": "Positive"}}.\n\nHEADLINES:\n{headlines_to_analyze}'
    try:
        response = model.generate_content(prompt)
        sentiments = json.loads(response.text.strip().lstrip("```json").rstrip("```"))
        for i, item in enumerate(news_list):
            item['sentiment'] = sentiments.get(f"Article {i+1}", "Neutral")
        return news_list
    except Exception as e:
        for item in news_list: item['sentiment'] = "Neutral"
        return news_list

def _expand_query_with_gemini(question: str) -> list[str]:
    if not GEMINI_API_KEY: return [question]
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f'Based on the user\'s financial question, generate 3-5 specific search keywords. Return ONLY a Python list of strings.\n\nQUESTION: "{question}"\n\nKEYWORDS:'
        response = model.generate_content(prompt)
        text_list = response.text.strip().replace("'", '"').replace('[', '').replace(']', '').replace('`', '')
        keywords = [kw.strip().strip('"') for kw in text_list.split(',') if kw.strip()]
        return keywords if keywords else [question]
    except Exception: return [question]

def _search_internal_database(keywords: list[str], fetcher: EnhancedFinancialDataFetcher) -> str:
    all_stocks, relevant_news, found_articles = fetcher.get_all_stocks(), [], set()
    for keyword in keywords:
        for stock in all_stocks:
            for news_item in stock.get("news", []):
                headline, summary = news_item.get("headline", ""), news_item.get("summary", "")
                if (keyword.lower() in headline.lower() or keyword.lower() in summary.lower()) and headline not in found_articles:
                    relevant_news.append(f"- **{headline}** ({stock['name']}): {summary}")
                    found_articles.add(headline)
    return "\n".join(relevant_news) or "No specific news articles found."

@st.cache_resource
def get_data_fetcher():
    return EnhancedFinancialDataFetcher()

# Define a custom hash function for EnhancedFinancialDataFetcher
def _hash_enhanced_financial_data_fetcher(fetcher: EnhancedFinancialDataFetcher):
    # Since EnhancedFinancialDataFetcher is likely a singleton via @st.cache_resource,
    # its object ID can serve as a unique identifier for hashing purposes.
    return id(fetcher)


@st.cache_data(ttl=600, hash_funcs={EnhancedFinancialDataFetcher: _hash_enhanced_financial_data_fetcher})
def get_comprehensive_response(question_in_english: str, _fetcher: EnhancedFinancialDataFetcher):
    if not GEMINI_API_KEY: return "Gemini API key is not configured."
    news_context = _search_internal_database(_expand_query_with_gemini(question_in_english), _fetcher)
    system_instruction = "You are 'FinChat', an expert financial analyst AI. You MUST provide a structured, insightful, and data-driven response based on the provided context. Begin with a direct summary, then a detailed analysis. Never say you have 'insufficient information'. Synthesize the given information to form a conclusive analysis. Always include a disclaimer that this is not financial advice."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
    prompt = f"CONTEXT:\n{news_context}\n\nUSER'S QUESTION: {question_in_english}\n\nYOUR ANALYSIS:"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"Sorry, I encountered an error: {e}"