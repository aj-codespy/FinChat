import os
import requests
import feedparser
from datetime import datetime
import google.generativeai as genai
import streamlit as st

# --- CONFIGURATION ---
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
    company_info: dict,
    news_context: str = "",
    doc_context: str = "",
):
    """
    Generates a response from Gemini for the finance chatbot.
    Implements a structured RAG workflow:
      - Augments prompt with company fundamentals, latest news, and docs.
      - Enforces a clear output schema (Understanding, Response, Reasoning, Sources, Confidence).
    """

    print("💬 CHAT: Starting get_gemini_response")

    if not GEMINI_API_KEY:
        print("❌ CHAT: GEMINI_API_KEY not configured")
        return "Gemini API key is not configured.", chat_history

    # ---- Fetch news if not provided ----
    if not news_context:
        ticker_or_name = company_info.get("Company Name", "finance")
        news_context = fetch_news(ticker_or_name)

    print("🤖 CHAT: Configuring Gemini model")
    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    # ---- Context Augmentation ----
    context = f"""
You are **FinChat**, an expert AI financial analyst.
You are grounded with the following **real-time retrieved facts**.
Never invent numbers. If facts are insufficient, say so clearly.

-- COMPANY CONTEXT --
Company: {company_info.get("Company Name", "N/A")}
- Market Cap: {company_info.get("Market Cap", "N/A")}
- P/E Ratio: {company_info.get("P/E Ratio", "N/A")}
- Revenue (TTM): {company_info.get("Revenue TTM", "N/A")}
- YoY Growth: {company_info.get("YoY Growth", "N/A")}
- Gross Margin: {company_info.get("Gross Margin", "N/A")}
- R&D Spend: {company_info.get("R&D Spend", "N/A")}

-- RECENT NEWS (last 7 days) --
{news_context}
"""

    if doc_context:
        context += f"-- DOCUMENT CONTEXT (e.g. 10-Q, PDF filings) --\n{doc_context}\n\n"

    # ---- Strict Prompting ----
    augmented_prompt = f"""
{context}
If the prompt is not related to finance in any way just end it and say "I'm sorry, I can only answer questions about finance."
User Question: {question}

Respond in the following structured format (strictly follow this):

### 1. Understanding
Explain in one or two sentences how you interpret the user’s query.

### 2. Response
Give a **direct, concise answer** to the question. Prefer tabular or bulleted comparisons for clarity.

### 3. Reasoning
Provide **3–5 numbered points** explaining why you gave that answer. 
Each point must **cite the source IDs or facts** from the context above.

### 4. Sources
List all source IDs/URLs you used.

### 5. Confidence
Rate confidence as Low / Medium / High and state why (e.g. “data from 2023 filing, no newer results”).
"""

    # ---- Run Gemini Chat ----
    chat = model.start_chat(history=chat_history)
    try:
        response = chat.send_message(augmented_prompt)
        return response.text, chat.history
    except Exception as e:
        return f"❌ Error from Gemini: {e}", chat_history


# ==========================================================
# STREAMLIT DASHBOARD
# ==========================================================
st.set_page_config(page_title="FinChat - AI Finance Assistant", layout="wide")

st.title("🤖 FinChat: AI Financial Assistant")

# Sidebar for input
st.sidebar.header("Company Lookup")
company_name = st.sidebar.text_input("Enter Company Name", "NVIDIA")
user_question = st.text_input("Ask FinChat anything:", "Compare NVIDIA with AMD in AI chips.")

if st.button("🔍 Get Insights"):
    # Fetch live news
    news = fetch_news(company_name)

    # Fake placeholder fundamentals (replace with API like Yahoo Finance later)
    company_info = {
        "Company Name": company_name,
        "Market Cap": "N/A",
        "P/E Ratio": "N/A",
        "Revenue TTM": "N/A",
        "YoY Growth": "N/A",
        "Gross Margin": "N/A",
        "R&D Spend": "N/A",
    }

    st.subheader("📈 Latest News")
    st.markdown(news, unsafe_allow_html=True)

    # Get Gemini response
    response, _ = get_gemini_response(
        question=user_question,
        chat_history=[],
        company_info=company_info,
        news_context=news,
    )

    st.subheader("🤖 FinChat Answer")
    st.markdown(response)
