import os
import re
import json
import google.generativeai as genai
import streamlit as st
from .data_fetcher import EnhancedFinancialDataFetcher
import asyncio
from googletrans import Translator
from PIL import Image
# We reuse the PDF text extraction from our doc_qa module
from .doc_qa import get_document_text

# --- Configuration ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- Core Utility Functions ---

def translate_text(text: str, target_language_code: str, source_language: str = "auto") -> str:
    """
    Translates text using the Google Translate library (synchronous).
    """
    if not text or target_language_code == 'en':
        return text
    try:
        translator = Translator()
        # Wrap the async call in asyncio.run to make it synchronous
        translation = asyncio.run(translator.translate(text, dest=target_language_code, src=source_language))
        return translation.text
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        return f"Translation Error: Could not translate text."

@st.cache_data(ttl=1800)
def generate_stock_summary(stock_info: dict) -> str:
    """
    Generates a concise summary for a single stock for the dashboard.
    """
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured."
    model = genai.GenerativeModel('gemini-1.5-flash')
    news_context = "\n".join([f"- {item['headline']}: {item['summary']}" for item in stock_info.get('news', [])])
    prompt = f"""
    Based on the following data and recent news for {stock_info['name']}, provide a concise, analytical summary (3-4 sentences) for a financial dashboard.
    Start with a concluding sentence about its current position or outlook.

    **Fundamental Data:**
    - Sector: {stock_info['sector']}
    - P/E Ratio: {stock_info['pe_ratio']}

    **Recent News:**
    {news_context}

    **Dashboard Summary:**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not generate AI summary: {e}"

@st.cache_data(ttl=1800)
def analyze_news_sentiment(news_list: list) -> list:
    """
    Analyzes sentiment for a list of news items.
    """
    if not news_list or not GEMINI_API_KEY:
        return []
    model = genai.GenerativeModel('gemini-1.5-flash')
    headlines_to_analyze = "\n".join([f"Article {i+1}: {item['headline']}" for i, item in enumerate(news_list)])
    prompt = f'Analyze the sentiment for each news headline below as "Positive", "Negative", or "Neutral". Return a valid JSON object like {{"Article 1": "Positive"}}.\n\nHEADLINES:\n{headlines_to_analyze}'
    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip().lstrip("```json").rstrip("```")
        sentiments = json.loads(clean_response)
        for i, item in enumerate(news_list):
            item['sentiment'] = sentiments.get(f"Article {i+1}", "Neutral")
        return news_list
    except Exception as e:
        print(f"[ERROR] Sentiment analysis failed: {e}")
        for item in news_list:
            item['sentiment'] = "Neutral"
        return news_list

# --- FinChat AI Helper Functions ---

def _expand_query_with_gemini(question: str) -> list[str]:
    """
    Uses Gemini to expand a user question into search keywords.
    """
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
    """
    Searches the internal database for news matching the keywords.
    """
    all_stocks, relevant_news, found_articles = fetcher.get_all_stocks(), [], set()
    for keyword in keywords:
        for stock in all_stocks:
            for news_item in stock.get("news", []):
                headline, summary = news_item.get("headline", ""), news_item.get("summary", "")
                if (keyword.lower() in headline.lower() or keyword.lower() in summary.lower()) and headline not in found_articles:
                    relevant_news.append(f"- **{headline}** ({stock['name']}): {summary}")
                    found_articles.add(headline)
    return "\n".join(relevant_news) or "No specific news articles found."

# --- Main Feature Functions ---

@st.cache_data(ttl=600)
def process_uploaded_file(uploaded_file) -> str:
    """
    Extracts text and key information from an uploaded image or PDF file.
    """
    if uploaded_file is None: return ""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if not GEMINI_API_KEY: return "Cannot process file: Gemini API key is missing."
    try:
        if file_extension == ".pdf":
            extracted_text = get_document_text(uploaded_file)
            if not extracted_text: return "Could not extract text from the PDF."
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Summarize the key financial figures and main points from the following PDF text:\n\n{extracted_text[:4000]}"
            response = model.generate_content(prompt)
            return response.text
        elif file_extension in [".png", ".jpg", ".jpeg"]:
            model = genai.GenerativeModel('gemini-1.5-flash')
            image = Image.open(uploaded_file)
            prompt = "Analyze this image. Extract all text, describe any charts or key financial information present, and provide a concise summary."
            response = model.generate_content([prompt, image])
            return response.text
        else:
            return "Unsupported file type."
    except Exception as e: return f"An error occurred while processing the file: {e}"

@st.cache_data(ttl=600)
def get_comprehensive_response(question_in_english: str, _fetcher: EnhancedFinancialDataFetcher, uploaded_file_context: str = ""):
    """
    The main RAG function for the FinChat AI, now with file context.
    """
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured."

    news_context = _search_internal_database(_expand_query_with_gemini(question_in_english), _fetcher)
    system_instruction = "You are 'FinChat', an expert financial analyst AI. You MUST provide a structured, insightful, and data-driven response based on all context provided (internal database news and uploaded file data). Begin with a direct summary, then a detailed analysis. Never say you have 'insufficient information'. Synthesize all information to form a conclusive analysis. Always include a disclaimer that this is not financial advice."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
    
    prompt = f"""
    **INTERNAL DATABASE CONTEXT (Recent News):**
    {news_context}

    **CONTEXT FROM UPLOADED FILE:**
    {uploaded_file_context if uploaded_file_context else "No file was uploaded."}

    ---
    **USER'S QUESTION (in English):**
    {question_in_english}

    ---
    **YOUR COMPREHENSIVE ANALYSIS (Synthesize all provided context to answer):**
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {e}"

@st.cache_data(ttl=600)
def analyze_ipo_document(document_text: str, target_language: str) -> str:
    """
    Analyzes the text of an IPO document.
    """
    if not GEMINI_API_KEY or not document_text:
        return "Gemini API key is not configured or the document is empty."
    system_instruction = "You are an expert IPO Analyst. Analyze the provided IPO prospectus text and create a structured, unbiased report covering: Business Overview, Financial Health, Industry Outlook, Objectives of the Offer, Key Risks, and Valuation. If info is missing, state that. End with a neutral summary."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
    prompt = f"Please analyze the following IPO document text:\n\n{document_text[:30000]}"
    try:
        english_response = model.generate_content(prompt).text
        return translate_text(english_response, target_language, source_language="English")
    except Exception as e:
        return f"An error occurred during IPO analysis: {e}"

@st.cache_data(ttl=600)
def generate_retirement_plan(user_data: dict, target_language: str) -> str:
    """
    Generates a personalized retirement plan.
    """
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured."
    system_instruction = "You are a helpful Financial Planning AI. Create a simplified, illustrative retirement plan based on the user's data. Structure it into: Financial Snapshot, Retirement Goal, Investment Strategy, and Projected Outcome. End with actionable next steps and a bold disclaimer that this is not professional financial advice."
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
    prompt = f"Please generate a retirement plan for the following user:\n\n{json.dumps(user_data, indent=2)}"
    try:
        english_response = model.generate_content(prompt).text
        return translate_text(english_response, target_language, source_language="English")
    except Exception as e:
        return f"An error occurred during retirement plan generation: {e}"