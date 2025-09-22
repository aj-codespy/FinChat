import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio

# Import all necessary functions from your modules
from modules.data_fetcher import EnhancedFinancialDataFetcher
from modules import visualizations
from modules.chat import (
    get_comprehensive_response, 
    translate_text, 
    generate_stock_summary, 
    analyze_news_sentiment,
    analyze_ipo_document, 
    generate_retirement_plan,
    process_uploaded_file
)
from modules.doc_qa import (
    get_document_text, 
    get_text_chunks, 
    get_vector_store, 
    summarize_document_with_full_context, 
    user_input
)

# --- PAGE CONFIGURATION & DATA LOADING ---
st.set_page_config(page_title="FinChat - AI Financial Assistant", layout="wide", initial_sidebar_state="expanded")
# Create the fetcher instance once and reuse it across the app
fetcher = EnhancedFinancialDataFetcher()
all_stocks_list = fetcher.get_all_stocks()
if not all_stocks_list:
    st.error("Failed to load stock database. The application cannot start.")
    st.stop()
all_stocks_df = pd.DataFrame(all_stocks_list)


# --- PAGE RENDERING FUNCTIONS ---

def render_home_page():
    st.title("Welcome to FinChat: Your AI-Powered Financial Co-Pilot 🚀")
    st.markdown("---")
    st.markdown("""
    **FinChat is a comprehensive suite of tools designed to democratize financial analysis for everyone, from seasoned professionals to curious students.**
    
    Use the sidebar to navigate between our powerful features:
    - **Stock Analyzer:** A visual dashboard for 150+ major stocks.
    - **Doc Chat:** Chat with your own financial documents.
    - **IPO Analyzer:** Get AI-driven analysis of IPO documents.
    - **Retirement Planner:** Generate a personalized retirement roadmap.
    - **FinChat AI:** Our multi-lingual chatbot for all your financial questions.
    """)

def render_stock_analyzer_page():
    st.header("📊 Stock Analyzer Dashboard")
    
    st.sidebar.header("Stock Analyzer Filters")
    all_company_names = sorted(all_stocks_df['name'].unique())
    selected_company = st.sidebar.selectbox("Select a Stock for Detailed Analysis", ["None"] + all_company_names)
    selected_country = st.sidebar.selectbox("Filter Dashboard by Country", ["All", "India", "USA"])
    unique_sectors = sorted(all_stocks_df['sector'].unique())
    selected_sector = st.sidebar.selectbox("Filter Dashboard by Sector", ["All"] + unique_sectors)

    filtered_df = all_stocks_df.copy()
    if selected_country != "All": filtered_df = filtered_df[filtered_df['country'] == selected_country]
    if selected_sector != "All": filtered_df = filtered_df[filtered_df['sector'] == selected_sector]

    if filtered_df.empty:
        st.warning("No stocks match the selected filters.")
        st.stop()
        
    st.subheader("Key Metrics for Selected Scope")
    col1, col2, col3 = st.columns(3)
    col1.metric("Companies Shown", f"{filtered_df.shape[0]}")
    col2.metric("Average Market Cap (USD B)", f"{filtered_df['market_cap_usd_b'].mean():.2f}")
    col3.metric("Average P/E Ratio", f"{filtered_df['pe_ratio'].mean():.2f}")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top 15 Companies by Market Cap")
        fig1 = px.bar(filtered_df.nlargest(15, 'market_cap_usd_b'), x='name', y='market_cap_usd_b', color='sector')
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.subheader("Sector Composition by Company Count")
        fig3 = px.pie(filtered_df, names='sector')
        st.plotly_chart(fig3, use_container_width=True)
        
    if selected_company != "None":
        st.divider()
        st.header(f"Deep Dive Analysis for {selected_company}")
        stock_data_filtered = filtered_df[filtered_df['name'] == selected_company]
        
        if not stock_data_filtered.empty:
            stock_info = stock_data_filtered.iloc[0].to_dict()
            ticker = stock_info.get('symbol', '')
            
            with st.spinner("Generating AI-powered summary..."):
                st.subheader("📝 AI-Generated Summary")
                st.info(generate_stock_summary(stock_info))

            col1, col2 = st.columns([2, 1])
            with col1:
                fig = visualizations.create_candlestick_chart(ticker, selected_company)
                if fig: st.plotly_chart(fig, use_container_width=True)
            with col2:
                with st.spinner("Analyzing news sentiment..."):
                    news = analyze_news_sentiment(fetcher.get_hybrid_news(stock_info))
                    fig = visualizations.create_sentiment_pie_chart(news)
                    if fig: st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Hybrid News Feed (Database + Live)")
            if 'news' in locals() and news:
                st.dataframe(visualizations.create_news_sentiment_df(news), use_container_width=True, hide_index=True)
        else:
            st.warning(f"**{selected_company}** is not in the current filter.")


def render_doc_chat_page():
    st.header("📄 Chat with Your Document")
    st.info("Upload a financial PDF or DOCX file to get started.")
    uploaded_file = st.file_uploader("Upload document", type=['pdf', 'docx'], label_visibility="collapsed")
    
    if "doc_processed" not in st.session_state: st.session_state.doc_processed = False
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Analyzing document..."):
            raw_text = get_document_text(uploaded_file)
            if raw_text:
                get_vector_store(get_text_chunks(raw_text))
                st.session_state.doc_summary = summarize_document_with_full_context(get_text_chunks(raw_text))
                st.session_state.doc_processed = True
                st.success("Document processed!")

    if st.session_state.doc_processed:
        st.subheader("AI-Generated Document Summary")
        st.markdown(st.session_state.doc_summary)
        st.divider()
        st.subheader("Ask a Question About the Document")
        if user_question := st.chat_input("Ask about the document's content:"):
            with st.chat_message("user"): st.markdown(user_question)
            with st.chat_message("assistant"):
                with st.spinner("Searching..."): st.markdown(user_input(user_question))

def render_ipo_analyzer_page():
    st.header("📄 IPO Analyzer")
    st.info("Upload an IPO document (like a DRHP) to receive an AI-powered analysis.")
    lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta"}
    selected_lang_name = st.selectbox("Select Analysis Language", list(lang_map.keys()))
    target_lang_code = lang_map[selected_lang_name]
    uploaded_file = st.file_uploader("Upload IPO Document (PDF or DOCX)", type=['pdf', 'docx'])

    if uploaded_file and st.button("Analyze IPO Document"):
        with st.spinner(f"Analyzing in {selected_lang_name}..."):
            raw_text = get_document_text(uploaded_file)
            if raw_text:
                response = analyze_ipo_document(raw_text, target_lang_code)
                st.subheader("AI Analysis of IPO Document")
                st.markdown(response)
            else:
                st.error("Could not extract text from the document.")

def render_retirement_planner_page():
    st.header("💰 Retirement Planner")
    st.info("Fill in your financial details to generate an illustrative retirement plan.")
    lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta"}
    selected_lang_name = st.selectbox("Select Report Language", list(lang_map.keys()))
    target_lang_code = lang_map[selected_lang_name]

    with st.form("retirement_form"):
        st.subheader("Your Financial Profile")
        col1, col2 = st.columns(2)
        with col1:
            current_age = st.number_input("Current Age", 18, 60, 30)
            monthly_salary = st.number_input("Monthly Salary (INR)", 0, value=75000, step=5000)
            current_savings = st.number_input("Total Current Savings (Lakhs INR)", 0.0, value=10.0, step=0.5)
        with col2:
            retirement_age = st.number_input("Target Retirement Age", 40, 70, 60)
            monthly_expenses = st.number_input("Monthly Expenses (INR)", 0, value=40000, step=5000)
            salary_growth = st.slider("Expected Annual Salary Growth (%)", 0, 20, 8)
        st.subheader("Your Investment Profile")
        risk_appetite = st.radio("Risk Appetite", ["Conservative", "Moderate", "Aggressive"], horizontal=True)
        submitted = st.form_submit_button("Generate My Retirement Plan")

    if submitted:
        user_data = {
            "current_age": current_age, "retirement_age": retirement_age,
            "monthly_salary_inr": monthly_salary, "monthly_expenses_inr": monthly_expenses,
            "current_savings_inr": int(current_savings * 100000),
            "expected_salary_growth_percent": salary_growth, "risk_appetite": risk_appetite
        }
        with st.spinner(f"Generating your plan in {selected_lang_name}..."):
            response = generate_retirement_plan(user_data, target_lang_code)
            st.subheader("Your Personalized Retirement Roadmap")
            st.markdown(response)

def render_fin_chat_page():
    st.header("💬 Multi-lingual FinChat AI")
    lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Bengali": "bn"}
    selected_lang_name = st.selectbox("Select Language", list(lang_map.keys()))
    target_lang_code = lang_map[selected_lang_name]

    st.info(f"Ask questions in {selected_lang_name}. The AI will reply in {selected_lang_name}.")
    uploaded_file = st.file_uploader("Add context from a file (Optional)", type=['pdf', 'png', 'jpg', 'jpeg'])

    if "fin_messages" not in st.session_state: st.session_state.fin_messages = []
    for msg in st.session_state.fin_messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input(f"Ask a financial question in {selected_lang_name}..."):
        st.session_state.fin_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                file_context = ""
                if uploaded_file:
                    file_context = process_uploaded_file(uploaded_file)
                
                english_prompt = translate_text(prompt, 'en')
                english_response = get_comprehensive_response(english_prompt, fetcher, file_context)
                final_response = translate_text(english_response, target_lang_code, "English")
                st.markdown(final_response)
        st.session_state.fin_messages.append({"role": "assistant", "content": final_response})
        st.rerun()

# --- MAIN APP LOGIC ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Home", "Stock Analyzer", "Doc Chat", "IPO Analyzer", "Retirement Planner", "FinChat AI"
], key="navigation_radio")

if page == "Home": render_home_page()
elif page == "Stock Analyzer": render_stock_analyzer_page()
elif page == "Doc Chat": render_doc_chat_page()
elif page == "IPO Analyzer": render_ipo_analyzer_page()
elif page == "Retirement Planner": render_retirement_planner_page()
elif page == "FinChat AI": render_fin_chat_page()
