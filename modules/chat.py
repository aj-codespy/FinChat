import os
import google.generativeai as genai
import streamlit as st

# --- Configuration ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get('GEMINI_API_KEY'))
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(question, chat_history, company_info, news_context, doc_context=""):
    """
    Generates a response from Gemini for the general finance chatbot.
    Implements the RAG architecture by augmenting the prompt with real-time context.
    """
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured.", chat_history

    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    context = f"""
    You are FinChat, an expert AI financial assistant. Your knowledge is augmented with the following real-time information.
    Your primary goal is to provide accurate, data-driven answers based ONLY on the context provided.
    Do not make up information. If the context is insufficient, state that clearly.
    
    Current Company Context ({company_info.get('Company Name', 'N/A')}):
    - Market Cap: {company_info.get('Market Cap', 'N/A')}
    - P/E Ratio: {company_info.get('P/E Ratio', 'N/A')}

    Recent News Summary (last 7 days):
    {news_context}
    """
    
    if doc_context:
        context += f"\nInformation from an Uploaded Financial Document:\n{doc_context}"

    augmented_prompt = f"{context}\n\nBased on all the information above, answer the user's question.\nUser Question: {question}"

    chat = model.start_chat(history=chat_history)
    
    try:
        response = chat.send_message(augmented_prompt)
        return response.text, chat.history
    except Exception as e:
        return f"Sorry, I encountered an error: {e}", chat_history

