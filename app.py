import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio

# Import all necessary functions from your modules
from modules.data_fetcher import EnhancedFinancialDataFetcher
from modules import visualizations
from modules.stock_data import get_company_info # Import get_company_info
from modules.chat import (
    get_comprehensive_response, 
    translate_text, 
    generate_stock_summary, 
    analyze_news_sentiment,
    get_data_fetcher
)
from modules.doc_qa import (
    get_document_text, 
    get_text_chunks, 
    get_vector_store, 
    summarize_document_with_full_context, 
    user_input
)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FinChat - AI Financial Assistant", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- DATA LOADING ---
# This loads the data once using the functions from your modules
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
    
    Navigating the world of finance can be complex. Information is scattered, data is overwhelming, and reliable analysis is hard to come by. FinChat solves this by integrating a powerful, curated database with advanced AI to give you clear, actionable insights in seconds.
    """)
    
    st.subheader("What We Offer:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Stock Analyzer**")
        st.write("An interactive dashboard to visualize and analyze data for major Indian and US companies. Compare market caps, P/E ratios, and sector compositions with dynamic charts.")
    
    with col2:
        st.success("📄 **Doc Chat**")
        st.write("Upload your own financial documents (like annual reports or PDFs) and chat with them. Our AI will read the document and answer your specific questions based on its content.")
        
    with col3:
        st.warning("💬 **Multi-lingual FinChat AI**")
        st.write("Our advanced conversational AI, designed for all users across India. Ask complex financial questions in languages like Hindi, Marathi, or Tamil, and get comprehensive, data-driven answers in the same language.")
        
    st.markdown("---")
    st.write("**Get started by selecting a feature from the sidebar on the left.**")


def render_stock_analyzer_page():
    st.header("📊 Stock Analyzer Dashboard")
    
    # --- FILTERS ---
    st.sidebar.header("Stock Analyzer Filters")
    
    selected_country = st.sidebar.selectbox("Filter Dashboard by Country", ["All", "India", "USA"])
    unique_sectors = sorted(all_stocks_df['sector'].unique())
    selected_sector = st.sidebar.selectbox("Filter Dashboard by Sector", ["All"] + unique_sectors)

    # --- FILTERING LOGIC ---
    filtered_df = all_stocks_df.copy()
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df['sector'] == selected_sector]
        
    # Dynamically update the list of available companies based on the filters
    all_company_names = sorted(all_stocks_df['name'].unique())
    selected_company = st.sidebar.selectbox("Select a Stock for Detailed Analysis", ["None"] + all_company_names)

    # --- RENDER DASHBOARD ---
    if filtered_df.empty:
        st.warning("No stocks match the selected filters.")
        st.stop()

    st.subheader("Key Metrics for Selected Scope")
    col1, col2, col3 = st.columns(3)
    avg_mkt_cap = filtered_df['market_cap_usd_b'].mean()
    avg_pe = filtered_df['pe_ratio'].mean()
    col1.metric("Companies Shown", f"{filtered_df.shape[0]}")
    col2.metric("Average Market Cap (USD B)", f"{avg_mkt_cap:.2f}")
    col3.metric("Average P/E Ratio", f"{avg_pe:.2f}")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top 15 Companies by Market Cap")
        fig1 = px.bar(filtered_df.nlargest(15, 'market_cap_usd_b'), x='name', y='market_cap_usd_b', color='sector')
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.subheader("Sector Composition by Company Count")
        fig3 = px.pie(filtered_df, names='sector', title="Sector Distribution")
        st.plotly_chart(fig3, use_container_width=True)
        
    # --- DETAILED SINGLE-STOCK ANALYSIS VIEW ---
    if selected_company != "None":
        st.divider()
        st.header(f"Deep Dive Analysis for {selected_company}")
        
        # This logic is now safe and won't cause an IndexError
        stock_data_filtered = filtered_df[filtered_df['name'] == selected_company]
        
        if not stock_data_filtered.empty:
            stock_info = stock_data_filtered.iloc[0].to_dict()
            ticker = stock_info.get('symbol', '')
            
            with st.spinner("Generating AI-powered summary..."):
                st.subheader("📝 AI-Generated Summary")
                st.info(generate_stock_summary(stock_info))

            st.subheader("📊 Key Financial Metrics")
            company_details = get_company_info(ticker)
            if company_details:
                col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                col_kpi1.metric("Market Cap", company_details.get("Market Cap", "N/A"))
                col_kpi2.metric("P/E Ratio", company_details.get("P/E Ratio", "N/A"))
                col_kpi3.metric("Sector", company_details.get("Sector", "N/A"))
                col_kpi4.metric("Industry", company_details.get("Industry", "N/A"))
                if company_details.get("Website") and company_details["Website"] != "N/A":
                    st.markdown(f"**Website:** [{company_details["Website"]}]({company_details["Website"]})")
            else:
                st.warning("Could not fetch detailed company metrics.")

            col1, col2 = st.columns([2, 1])
            with col1:
                with st.spinner(f"Fetching live stock chart for {ticker}..."):
                    print(f"[APP] Calling create_candlestick_chart with Ticker: {ticker}, Company: {selected_company}")
                    candlestick_fig = visualizations.create_candlestick_chart(ticker, selected_company)
                    if candlestick_fig:
                        st.plotly_chart(candlestick_fig, use_container_width=True)
                    else:
                        st.warning("Could not load live stock price chart.")
            
            with col2:
                with st.spinner("Analyzing news sentiment..."):
                    # Fetch hybrid news (static + live) before analyzing sentiment
                    hybrid_news_list = fetcher.get_hybrid_news(stock_info)
                    news_with_sentiment = analyze_news_sentiment(hybrid_news_list)
                    sentiment_pie_fig = visualizations.create_sentiment_pie_chart(news_with_sentiment)
                    if sentiment_pie_fig:
                        st.plotly_chart(sentiment_pie_fig, use_container_width=True)
                    else:
                        st.write("No news available for sentiment analysis.")

            st.subheader("News Sentiment Analysis")
            if 'news_with_sentiment' in locals() and news_with_sentiment:
                news_df = visualizations.create_news_sentiment_df(news_with_sentiment)
                st.dataframe(news_df, use_container_width=True, hide_index=True)


def render_doc_chat_page():
    st.header("📄 Chat with Your Document")
    st.info("Upload a financial PDF or DOCX file to get started. The AI will generate a summary and allow you to ask specific questions about its content.")
    
    uploaded_file = st.file_uploader("Upload your document", type=['pdf', 'docx'], label_visibility="collapsed")
    
    if "doc_processed" not in st.session_state:
        st.session_state.doc_processed = False

    if uploaded_file:
        if st.button("Process Document"):
            with st.spinner("Reading and analyzing document..."):
                raw_text = get_document_text(uploaded_file)
                if raw_text:
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.session_state.doc_summary = summarize_document_with_full_context(text_chunks)
                    st.session_state.doc_processed = True
                    st.success("Document processed successfully!")
                else:
                    st.error("Could not extract text from the document.")

    if st.session_state.doc_processed:
        st.divider()
        st.subheader("AI-Generated Document Summary")
        st.markdown(st.session_state.doc_summary)
        st.divider()

        st.subheader("Ask a Question About the Document")
        if user_question := st.chat_input("e.g., 'What were the key revenue drivers mentioned?'"):
            with st.chat_message("user"):
                st.markdown(user_question)
            with st.chat_message("assistant"):
                with st.spinner("Searching for the answer..."):
                    response = user_input(user_question)
                    st.markdown(response)

async def render_fin_chat_page():
    st.header("💬 Multi-lingual FinChat AI")
    lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Bengali": "bn"}
    selected_lang_name = st.selectbox("Select Language", list(lang_map.keys()))
    target_lang_code = lang_map[selected_lang_name]

    st.info(f"You can now ask questions in {selected_lang_name}. The AI will analyze the data in English and reply to you in {selected_lang_name}.")

    if "fin_messages" not in st.session_state:
        st.session_state.fin_messages = []

    for message in st.session_state.fin_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Ask a financial question in {selected_lang_name}..."):
        st.session_state.fin_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking... Analyzing data and translating..."):
                # The translation calls are now synchronous
                english_prompt = await translate_text(prompt, 'en')
                # Get the cached data fetcher instance
                data_fetcher_instance = get_data_fetcher()
                english_response = get_comprehensive_response(question_in_english=english_prompt, _fetcher=data_fetcher_instance)
                final_response = await translate_text(english_response, target_lang_code, source_language="English")
                st.markdown(final_response)
        
        st.session_state.fin_messages.append({"role": "assistant", "content": final_response})
        st.rerun()

# --- MAIN APP LOGIC ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Stock Analyzer", "Doc Chat", "FinChat AI"], key="navigation_radio")

if page == "Home":
    render_home_page()
elif page == "Stock Analyzer":
    render_stock_analyzer_page()
elif page == "Doc Chat":
    render_doc_chat_page()
elif page == "FinChat AI":
    asyncio.run(render_fin_chat_page())