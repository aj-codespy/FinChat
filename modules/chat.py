import os
import feedparser
from datetime import datetime
import google.generativeai as genai
import streamlit as st
from urllib.parse import quote_plus

# --- Configuration ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- News Fetcher (Google RSS) ---
@st.cache_data(ttl=900) # Cache news results for 15 minutes
def fetch_news_for_companies(company_names: list[str], max_articles_per_company: int = 5) -> str:
    """
    Fetches the latest financial news for a list of companies using Google News RSS.
    Returns a single formatted string of all news, ready to be used as context for Gemini.
    """
    print(f"[INFO] Fetching news for: {company_names}")
    all_news_context = []
    
    for name in company_names:
        query = f'"{name}" stock financial earnings revenue'
        rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            articles = []
            all_news_context.append(f"\n--- RECENT NEWS FOR {name.upper()} ---")
            
            for entry in feed.entries[:max_articles_per_company]:
                try:
                    pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
                except Exception:
                    pub_date = "Recent"
                
                # We'll just use title and date for a concise context
                articles.append(f"- {entry.title} ({pub_date})")

            if not articles:
                all_news_context.append("No recent news found.")
            else:
                all_news_context.extend(articles)

        except Exception as e:
            print(f"[ERROR] Failed to fetch news for {name}: {e}")
            all_news_context.append(f"Failed to fetch news for {name}.")

    return "\n".join(all_news_context)

# --- Gemini Response Generator (RAG) ---
def get_gemini_response(question: str, news_context: str, chat_history):
    """
    Generates a response from Gemini, using the provided news as context.
    """
    if not GEMINI_API_KEY:
        return "❌ Gemini API key is not configured.", chat_history

    system_instruction = """You are "FinChat", a specialized financial assistant AI from Pune, India. Your purpose is to provide clear, concise, and accurate financial insights. You must answer the user's question based *only* on the real-time news context provided. Do not use any external knowledge or make up information. Format your answers clearly using Markdown. If the context does not contain the answer, state that you couldn't find the information in the recent news feed.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    
    chat_session = model.start_chat(history=chat_history)

    # Construct the final prompt for the model
    prompt = f"**LATEST NEWS CONTEXT:**\n{news_context}\n\n**USER'S QUESTION:** {question}\n\n**YOUR ANALYSIS:**"
    
    try:
        print("[INFO] Sending final prompt with live news context to Gemini...")
        response = chat_session.send_message(prompt)
        
        # Convert history to a serializable format for session state
        dict_history = [{'role': msg.role, 'parts': [part.text for part in msg.parts]} for msg in chat_session.history]
        
        print("[SUCCESS] Received response from Gemini.")
        return response.text, dict_history
        
    except Exception as e:
        st.error(f"An error occurred with the Gemini API: {e}")
        return "Sorry, I couldn't process your request at the moment.", chat_history