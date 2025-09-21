import os
import streamlit as st
import pandas as pd
from modules import news_sentiment, stock_data, doc_qa, chat

# Fix OpenMP library conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# --- Page Configuration ---
st.set_page_config(
    page_title="FinChat: Financial Insights Assistant",
    page_icon="🚀",
    layout="wide"
)

# --- App State Management ---
if 'company' not in st.session_state:
    st.session_state.company = 'NVIDIA'
if 'ticker' not in st.session_state:
    st.session_state.ticker = 'NVDA'
if 'news_df' not in st.session_state:
    st.session_state.news_df = pd.DataFrame()
if 'stock_df' not in st.session_state:
    st.session_state.stock_df = pd.DataFrame()
if 'company_info' not in st.session_state:
    st.session_state.company_info = {}
if 'doc_summary' not in st.session_state:
    st.session_state.doc_summary = ""
if 'doc_processed' not in st.session_state:
    st.session_state.doc_processed = False
if 'fin_chat_history' not in st.session_state:
    st.session_state.fin_chat_history = []

# --- Helper Functions ---
TICKER_MAP = {"NVIDIA": "NVDA", "Apple": "AAPL", "Tesla": "TSLA", "Infosys": "INFY", "TCS": "TCS.NS"}

def load_data_for_company(company_name):
    """Loads all necessary data when a company is selected."""
    print(f"🏢 APP: Starting load_data_for_company for {company_name}")
    
    with st.spinner(f"Fetching data for {company_name}..."):
        st.session_state.company = company_name
        ticker = TICKER_MAP.get(company_name, company_name)
        st.session_state.ticker = ticker
        print(f"📈 APP: Ticker mapped to {ticker}")
        
        print(f"📰 APP: Fetching news for {company_name}")
        st.session_state.news_df = news_sentiment.fetch_and_process_news(ticker)
        print(f"📊 APP: News DataFrame shape: {st.session_state.news_df.shape}")
        
        print(f"📈 APP: Fetching stock data for {ticker}")
        st.session_state.stock_df = stock_data.get_stock_data(ticker)
        print(f"📊 APP: Stock DataFrame shape: {st.session_state.stock_df.shape}")
        
        print(f"ℹ️ APP: Fetching company info for {ticker}")
        st.session_state.company_info = stock_data.get_company_info(ticker)
        print(f"ℹ️ APP: Company info: {st.session_state.company_info}")
        
        # Reset other states
        st.session_state.doc_summary = ""
        st.session_state.doc_processed = False
        st.session_state.fin_chat_history = []
        print(f"✅ APP: Completed load_data_for_company for {company_name}")

# Initialize data for the default company on first load
if st.session_state.stock_df.empty:
    load_data_for_company(st.session_state.company)


# --- Sidebar ---
with st.sidebar:
    st.image("https://i.imgur.com/M2J52aH.png", width=100)
    st.title("FinChat")
    
    company_list = list(TICKER_MAP.keys())
    selected_company = st.selectbox(
        "Select Company",
        company_list,
        index=company_list.index(st.session_state.company)
    )

    # If selection changes, reload data
    if selected_company != st.session_state.company:
        load_data_for_company(selected_company)
        st.rerun()

    st.divider()
    
    st.header("Upload Financial Report")
    uploaded_file = st.file_uploader("Upload PDF or DOCX", type=['pdf', 'docx'], label_visibility="collapsed")

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document... This may take a moment."):
            raw_text = doc_qa.get_document_text(uploaded_file)
            if raw_text:
                text_chunks = doc_qa.get_text_chunks(raw_text)
                doc_qa.get_vector_store(text_chunks)
                st.session_state.doc_summary = doc_qa.summarize_document_map_reduce(text_chunks)
                st.session_state.doc_processed = True
                st.success("Document processed! Navigate to 'Doc Chat'.")
            else:
                st.error("Could not read text from the document.")

    st.divider()
    st.info("Ensure API keys for NewsAPI and Gemini are set in Streamlit secrets for deployed apps.")


# --- Main Area Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📄 Doc Chat", "💬 Fin Chat"])

# --- Dashboard Tab ---
with tab1:
    st.header(f"Dashboard for {st.session_state.company} ({st.session_state.ticker})")
    
    # Top Panel: Company Overview
    info = st.session_state.company_info
    st.subheader("Company Fundamentals")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", info.get("Market Cap", "N/A"))

    pe_ratio = info.get('P/E Ratio')
    col2.metric("P/E Ratio", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
    
    col3.metric("Sector", info.get("Sector", "N/A"))
    col4.metric("Industry", info.get("Industry", "N/A"))

    website = info.get('Website', 'N/A')
    if website and website != 'N/A':
        st.markdown(f"**Website:** [{website}]({website})")

    st.divider()

    # Middle Panel: Charts
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Market Performance & Sentiment")
        stock_fig = stock_data.create_stock_price_chart(st.session_state.stock_df, st.session_state.company)
        if stock_fig:
            stock_fig_with_sentiment = stock_data.overlay_sentiment_on_chart(stock_fig, st.session_state.news_df)
            st.plotly_chart(stock_fig_with_sentiment, use_container_width=True)
        else:
            st.warning("Could not load stock data.")
    with col2:
        st.subheader("News Sentiment")
        sentiment_pie_fig = news_sentiment.create_sentiment_pie_chart(st.session_state.news_df)
        if sentiment_pie_fig:
            st.plotly_chart(sentiment_pie_fig, use_container_width=True)
        else:
            st.warning("Not enough sentiment data for a chart.")

    # Bottom Panel: Latest News
    st.subheader("Latest News")
    print(f"📰 APP: Displaying news section - DataFrame empty: {st.session_state.news_df.empty}")
    print(f"📊 APP: News DataFrame shape: {st.session_state.news_df.shape}")
    
    if not st.session_state.news_df.empty:
        print(f"✅ APP: Showing news DataFrame with {len(st.session_state.news_df)} articles")
        st.dataframe(
            st.session_state.news_df[['Published At', 'Headline', 'Sentiment', 'Summary']],
            use_container_width=True, hide_index=True
        )
    else:
        print(f"⚠️ APP: News DataFrame is empty, showing warning")
        st.warning("No recent news found. Check your Finnhub API key.")

# --- Doc Chat Tab ---
with tab2:
    st.header("Document Q&A")
    
    if not st.session_state.doc_processed:
        st.info("Upload and process a financial document via the sidebar to enable this feature.")
        st.image("https://i.imgur.com/s8aFE9U.png", caption="Upload a document to get started.")
    else:
        st.subheader("AI-Generated Document Summary")
        with st.expander("Click to view summary", expanded=True):
            st.markdown(st.session_state.doc_summary)
        st.divider()

        st.subheader("Chat with Your Document")
        if user_question := st.chat_input("Ask a specific question about the document's content:"):
            with st.chat_message("user"):
                st.markdown(user_question)
            
            with st.spinner("Searching for the answer..."):
                response = doc_qa.user_input(user_question)
                with st.chat_message("assistant"):
                    st.write(response)

# --- Fin Chat Tab ---
with tab3:
    st.header("Finance Chat")
    st.info("Ask general financial questions or compare companies using real-time data.")

    for message in st.session_state.fin_chat_history:
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    if prompt := st.chat_input("Ask about market trends, compare stocks, etc."):
        st.session_state.fin_chat_history.append({"role": "user", "parts": [prompt]})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            news_context = st.session_state.news_df[['Headline', 'Summary']].to_string(index=False)
            doc_context = st.session_state.doc_summary if st.session_state.doc_processed else ""
            
            response_text, updated_history = chat.get_gemini_response(
                prompt, st.session_state.fin_chat_history,
                st.session_state.company_info, news_context, doc_context
            )
            st.session_state.fin_chat_history = updated_history
            
            with st.chat_message("assistant"):
                st.markdown(response_text)

