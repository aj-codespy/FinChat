import streamlit as st
import pandas as pd
from modules import news_sentiment, stock_data, doc_qa, chat

# --- Page Configuration ---
st.set_page_config(
    page_title="FinChat: Financial Insights Assistant",
    page_icon="🚀",
    layout="wide"
)

# --- App State Management ---
if 'company' not in st.session_state:
    st.session_state.company = 'Infosys' # Default company
if 'news_df' not in st.session_state:
    st.session_state.news_df = pd.DataFrame()
if 'stock_df' not in st.session_state:
    st.session_state.stock_df = pd.DataFrame()
if 'company_info' not in st.session_state:
    st.session_state.company_info = {}
if 'doc_summary' not in st.session_state:
    st.session_state.doc_summary = ""
if 'doc_text_chunks' not in st.session_state:
    st.session_state.doc_text_chunks = []
if 'fin_chat_history' not in st.session_state:
    st.session_state.fin_chat_history = []


# --- Helper Functions ---
def load_data_for_company(company_name):
    """Loads all necessary data when a company is selected."""
    with st.spinner(f"Fetching data for {company_name}..."):
        st.session_state.company = company_name
        # Use a common ticker mapping or derive from name
        ticker_map = {"Infosys": "INFY", "Apple": "AAPL", "Tesla": "TSLA", "TCS": "TCS.NS"}
        ticker = ticker_map.get(company_name, company_name) # Default to name if not in map

        st.session_state.news_df = news_sentiment.fetch_and_process_news(company_name)
        st.session_state.stock_df = stock_data.get_stock_data(ticker)
        st.session_state.company_info = stock_data.get_company_info(ticker)
        # Reset chat and doc states when company changes
        st.session_state.doc_summary = ""
        st.session_state.doc_text_chunks = []
        st.session_state.fin_chat_history = []


# --- Sidebar ---
with st.sidebar:
    st.title("🚀 FinChat")
    
    st.selectbox(
        "Select Company",
        ("Infosys", "Apple", "Tesla", "TCS"),
        key='selected_company',
        on_change=lambda: load_data_for_company(st.session_state.selected_company)
    )
    
    st.header("Upload Financial Report")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=['pdf', 'docx'])

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document..."):
            raw_text = doc_qa.get_document_text(uploaded_file)
            st.session_state.doc_text_chunks = doc_qa.get_text_chunks(raw_text)
            doc_qa.get_vector_store(st.session_state.doc_text_chunks)
            st.session_state.doc_summary = doc_qa.summarize_document(st.session_state.doc_text_chunks)
            st.success("Document processed! Go to the 'Doc Chat' tab to query it.")

    st.info("Note: Please provide your own API keys for Finnhub and Gemini in the code for full functionality.")


# --- Main Area Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📄 Doc Chat", "💬 Fin Chat"])

# --- Dashboard Tab ---
with tab1:
    st.header(f"Dashboard for {st.session_state.company}")
    
    # Load data on first run
    if st.session_state.news_df.empty:
        load_data_for_company(st.session_state.company)

    # Top Panel: Company Overview
    st.subheader("Company Overview")
    info = st.session_state.company_info
    col1, col2, col3 = st.columns(3)
    col1.metric("Market Cap", info.get("Market Cap", "N/A"))
    col2.metric("Sector", info.get("Sector", "N/A"))
    col3.metric("Website", info.get("Website", "N/A"), label_visibility="hidden")


    # Middle Panel: Charts
    st.subheader("Market & Sentiment Analysis")
    col1, col2 = st.columns(2)
    with col1:
        sentiment_pie_fig = news_sentiment.create_sentiment_pie_chart(st.session_state.news_df)
        if sentiment_pie_fig:
            st.plotly_chart(sentiment_pie_fig, use_container_width=True)
        else:
            st.warning("Not enough sentiment data to display pie chart.")
    
    with col2:
        stock_fig = stock_data.create_stock_price_chart(st.session_state.stock_df, st.session_state.company)
        # Overlay sentiment trend on the stock chart
        if stock_fig:
            # We recreate the sentiment trend chart logic here for overlay
            trend_fig = news_sentiment.create_sentiment_trend_chart(st.session_state.news_df)
            stock_fig_with_sentiment = stock_data.overlay_sentiment_on_chart(stock_fig, st.session_state.news_df)
            st.plotly_chart(stock_fig_with_sentiment, use_container_width=True)
        else:
            st.warning("Could not load stock data.")
            

    # Bottom Panel: Latest News
    st.subheader("Latest News")
    if not st.session_state.news_df.empty:
        st.dataframe(
            st.session_state.news_df[['Published At', 'Headline', 'Sentiment', 'Summary']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No recent news found for this company. Check your Finnhub API key.")


# --- Doc Chat Tab ---
with tab2:
    st.header("Document Q&A")
    
    if not st.session_state.doc_summary:
        st.info("Please upload and process a financial document using the sidebar to activate this tab.")
    else:
        st.subheader("AI-Generated Summary")
        st.markdown(st.session_state.doc_summary)
        st.divider()

        st.subheader("Chat with Your Document")
        user_question = st.text_input("Ask a question about the document:")
        if user_question:
            with st.spinner("Finding answer..."):
                response = doc_qa.user_input(user_question)
                st.write(response)

# --- Fin Chat Tab ---
with tab3:
    st.header("Finance Chat")
    st.info("Ask general financial questions or compare companies.")

    # Display chat messages
    for message in st.session_state.fin_chat_history:
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Chat input
    if prompt := st.chat_input("Ask me anything about finance..."):
        # Add user message to chat history
        st.session_state.fin_chat_history.append({"role": "user", "parts": [prompt]})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.spinner("Thinking..."):
            # Prepare context for the chat model
            news_context = st.session_state.news_df[['Headline', 'Summary']].to_string()
            doc_context_summary = st.session_state.doc_summary if st.session_state.doc_summary else "No document uploaded."
            
            response_text, updated_history = chat.get_gemini_response(
                prompt,
                st.session_state.fin_chat_history,
                st.session_state.company_info,
                news_context,
                doc_context_summary
            )
            
            st.session_state.fin_chat_history = updated_history
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response_text)
