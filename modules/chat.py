import os
import feedparser
from datetime import datetime
import google.generativeai as genai
import streamlit as st

# ==========================================================
# CONFIGURATION
# ==========================================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY"))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ==========================================================
# NEWS FETCHER (Google RSS)
# ==========================================================
def fetch_news(query: str, max_articles: int = 5) -> str:
    """
    Fetch latest financial news for a company using Google News RSS.
    Returns a formatted string usable inside Gemini prompt context.
    """
    rss_url = f"https://news.google.com/rss/search?q={query}+stock&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        return f"❌ Failed to fetch news: {e}"

    articles = []
    for entry in feed.entries[:max_articles]:
        try:
            pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pub_date = "Unknown Date"
        articles.append(f"- [{entry.title}]({entry.link}) ({pub_date})")

    if not articles:
        return "No recent news found."

    return "\n".join(articles)

# ==========================================================
# GEMINI RESPONSE GENERATOR (RAG)
# ==========================================================
def get_gemini_response(
    question: str,
    chat_history,
    companies,
    docs_context: str = "",
):
    """
    Generates a response from Gemini for the finance chatbot.
    Augments context with multiple companies + live news.
    """

    # normalize input
    if isinstance(companies, dict):
        companies = [companies.get("Company Name", "Unknown")]
    elif isinstance(companies, str):
        companies = [c.strip() for c in companies.split(",") if c.strip()]

    if not GEMINI_API_KEY:
        return "❌ Gemini API key is not configured.", chat_history

    # --- Build the prompt ---
    system_instruction = """
    You are "FinChat", a specialized financial assistant AI. 
    Your purpose is to provide clear, concise, and accurate financial insights.
    You must answer the user's question based *only* on the context provided.
    Do not use any external knowledge or make up information.
    Format your answers clearly using Markdown.
    If the context does not contain the answer, state that clearly.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    
    chat_session = model.start_chat(history=chat_history)

    prompt = f"CONTEXT:\n{docs_context}\n\nQUESTION: {question}"
    
    try:
        response = chat_session.send_message(prompt)
        
        # Convert history to list of dicts for consistency
        dict_history = []
        for message in chat_session.history:
            dict_history.append({
                'role': message.role,
                'parts': [part.text for part in message.parts]
            })
        
        return response.text, dict_history
    except Exception as e:
        st.error(f"An error occurred with the Gemini API: {e}")
        return "Sorry, I couldn't process your request.", chat_history