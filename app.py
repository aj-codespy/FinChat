import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

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
st.set_page_config(
    page_title="FinChat - AI Financial Assistant", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

fetcher = EnhancedFinancialDataFetcher()
all_stocks_list = fetcher.get_all_stocks()
if not all_stocks_list:
    st.error("Failed to load stock database. The application cannot start.")
    st.stop()
all_stocks_df = pd.DataFrame(all_stocks_list)

# --- ENHANCED CUSTOM THEMES & STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Navigation Bar Styling */
    .nav-container {
        background: rgba(26, 26, 46, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 0px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 255, 127, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: sticky;
        top: 20px;
        z-index: 100;
    }
    
    /* Enhanced Navigation Button Styling */
    .stButton > button {
        background: rgba(26, 26, 46, 0.8) !important;
        color: #a0a0b0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 48px !important;
        backdrop-filter: blur(10px) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: rgba(0, 255, 127, 0.1) !important;
        color: #00ff7f !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(0, 255, 127, 0.2) !important;
        border-color: rgba(0, 255, 127, 0.3) !important;
    }
    
    /* Main Content Container */
    .main-content {
        padding: 20px 0;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 30px 20px;
        background: radial-gradient(circle at center, rgba(0, 255, 127, 0.1) 0%, transparent 70%);
        border-radius: 24px;
        margin-bottom: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #00ff7f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #a0a0b0;
        max-width: 800px;
        margin: 0 auto 40px;
        line-height: 1.6;
            text-align: center;
    
    }
    
    /* Feature Cards Grid */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 24px;
        margin: 40px 0;
    }
    
    .feature-card {
        background: rgba(26, 26, 46, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 32px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        
        background: linear-gradient(90deg, transparent, #00ff7f, transparent);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .feature-card:hover::before {
        transform: translateX(100%);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 255, 127, 0.2);
        border-color: rgba(0, 255, 127, 0.3);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 20px;
        display: block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 12px;
    }
    
    .feature-description {
        color: #a0a0b0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Stats Cards */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .stat-card {
        background: rgba(26, 26, 46, 0.6);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 255, 127, 0.15);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #00ff7f;
        display: block;
        margin-bottom: 8px;
    }
    
    .stat-label {
        color: #a0a0b0;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Form and Input Styling */
    .stSelectbox > div > div {
        background: rgba(26, 26, 46, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stNumberInput > div > div > input {
        background: rgba(26, 26, 46, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(26, 26, 46, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Action Button Styling (for form submits, etc.) */
    .stButton > button[data-testid="stFormSubmitButton"],
    .stButton > button:not([data-testid]) {
        background: linear-gradient(135deg, #00ff7f 0%, #28a745 100%) !important;
        color: #000 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 255, 127, 0.3) !important;
    }
    
    .stButton > button[data-testid="stFormSubmitButton"]:hover,
    .stButton > button:not([data-testid]):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 255, 127, 0.4) !important;
    }
    
    /* File Uploader */
    .stFileUploader > div {
        background: rgba(26, 26, 46, 0.8);
        border: 2px dashed rgba(0, 255, 127, 0.3);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: rgba(0, 255, 127, 0.6);
        background: rgba(26, 26, 46, 0.9);
    }
    
    /* Chat Styling */
    .stChatMessage {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 10px 0;
    }
    
    /* Metrics Styling */
    .stMetric {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 16px;
        border-left: 4px solid #00ff7f;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Plotly Chart Container */
    .plotly-graph-div {
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar when used */
    .stSidebar > div {
        background: linear-gradient(180deg, rgba(26, 26, 46, 0.95) 0%, rgba(10, 10, 10, 0.95) 100%);
        backdrop-filter: blur(20px);
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess {
        background: rgba(0, 255, 127, 0.1);
        border: 1px solid rgba(0, 255, 127, 0.3);
        border-radius: 12px;
        color: #00ff7f;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 12px;
        color: #ffc107;
    }
    
    .stError {
        background: rgba(220, 53, 69, 0.1);
        border: 1px solid rgba(220, 53, 69, 0.3);
        border-radius: 12px;
        color: #dc3545;
    }
    
    .stInfo {
        background: rgba(13, 202, 240, 0.1);
        border: 1px solid rgba(13, 202, 240, 0.3);
        border-radius: 12px;
        color: #0dcaf0;
    }
    
    /* Divider */
    .stDivider {
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        height: 1px;
        border: none;
        margin: 30px 0;
    }
    
    /* Loading Spinner */
    .stSpinner {
        color: #00ff7f;
    }
    
    /* DataFrame Styling */
    .stDataFrame {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00ff7f, #28a745);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Plotly Theme
pio.templates["finchat_premium"] = go.layout.Template(
    layout=go.Layout(
        font={"color": "#ffffff", "family": "Inter, sans-serif"},
        title={"font": {"color": "#ffffff", "size": 18, "family": "Inter, sans-serif"}},
        paper_bgcolor="rgba(26, 26, 46, 0.8)",
        plot_bgcolor="rgba(26, 26, 46, 0.8)",
        xaxis={
            "gridcolor": "rgba(255, 255, 255, 0.1)", 
            "linecolor": "rgba(255, 255, 255, 0.2)",
            "tickcolor": "rgba(255, 255, 255, 0.3)",
            "zerolinecolor": "rgba(255, 255, 255, 0.2)"
        },
        yaxis={
            "gridcolor": "rgba(255, 255, 255, 0.1)", 
            "linecolor": "rgba(255, 255, 255, 0.2)",
            "tickcolor": "rgba(255, 255, 255, 0.3)",
            "zerolinecolor": "rgba(255, 255, 255, 0.2)"
        },
        legend={
            "bgcolor": "rgba(26, 26, 46, 0.8)", 
            "bordercolor": "rgba(255, 255, 255, 0.2)",
            "font": {"color": "#ffffff"}
        },
        colorway=['#00ff7f', '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14', '#20c997']
    )
)
pio.templates.default = "finchat_premium"

# --- PAGE RENDERING FUNCTIONS ---

def render_navigation():
    """Render the enhanced navigation bar using pure Streamlit components"""
    PAGES = {
        "Home": {"icon": "🏠", "function": render_home_page},
        "Stock Analyzer": {"icon": "📊", "function": render_stock_analyzer_page},
        "Doc Chat": {"icon": "📄", "function": render_doc_chat_page},
        "IPO Analyzer": {"icon": "📈", "function": render_ipo_analyzer_page},
        "Retirement Planner": {"icon": "💰", "function": render_retirement_planner_page},
        "FinChat AI": {"icon": "💬", "function": render_fin_chat_page},
    }
    
    # Create navigation using Streamlit columns with enhanced styling
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    cols = st.columns(len(PAGES))
    for i, (page_name, page_info) in enumerate(PAGES.items()):
        with cols[i]:
            # Apply custom styling based on active state
            button_style = ""
            if st.session_state.current_page == page_name:
                button_style = """
                <style>
                div[data-testid="column"]:nth-child({}) button {{
                    background: linear-gradient(135deg, #00ff7f 0%, #28a745 100%) !important;
                    color: #000 !important;
                    border: none !important;
                    font-weight: 600 !important;
                    box-shadow: 0 4px 20px rgba(0, 255, 127, 0.3) !important;
                }}
                </style>
                """.format(i + 1)
                st.markdown(button_style, unsafe_allow_html=True)
            
            if st.button(
                f"{page_info['icon']} {page_name}", 
                key=f"nav_{page_name}",
                help=f"Go to {page_name}",
                use_container_width=True
            ):
                st.session_state.current_page = page_name
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    return PAGES

def render_home_page():
    """Enhanced home page with beautiful hero section and feature cards"""
    # Hero Section
    st.markdown("""
    <div class="hero-section", style="text-align: center;">
        <h1 class="hero-title">FinChat</h1>
        <div class="hero-subtitle">Your AI-Powered Financial Co-Pilot for Smarter Investment Decisions</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <span class="stat-value">150+</span>
            <span class="stat-label">Stocks Analyzed</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <span class="stat-value">5+</span>
            <span class="stat-label">Languages Supported</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <span class="stat-value">24/7</span>
            <span class="stat-label">AI Assistant</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <span class="stat-value">∞</span>
            <span class="stat-label">Possibilities</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Features Grid - Using Streamlit columns instead of pure HTML
    st.markdown("### 🌟 **Explore Our Features**")
    
    # First row of features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 class="feature-title">Advanced Stock Analyzer</h3>
                <p class="feature-description">Deep dive into comprehensive stock analysis with interactive charts, real-time data, and AI-powered insights for 150+ major Indian and US stocks.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <h3 class="feature-title">Intelligent Doc Chat</h3>
                <p class="feature-description">Upload financial documents and get instant answers. Our AI reads annual reports, research papers, and financial statements to provide contextual insights.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <h3 class="feature-title">IPO Analyzer Pro</h3>
                <p class="feature-description">Comprehensive IPO analysis from DRHP documents. Get business model insights, financial health assessment, risk analysis, and valuation metrics.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Second row of features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">💰</div>
                <h3 class="feature-title">Smart Retirement Planner</h3>
                <p class="feature-description">Create personalized retirement strategies with AI-driven projections, investment recommendations, and goal-based financial planning.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <h3 class="feature-title">Multi-lingual AI Assistant</h3>
                <p class="feature-description">Ask complex financial questions in Hindi, Marathi, Tamil, Bengali, or English. Get comprehensive, localized financial advice powered by advanced AI.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3 class="feature-title">Secure & Private</h3>
                <p class="feature-description">Your financial data is protected with enterprise-grade security. All analysis is performed securely without storing personal information.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("🚀 **Get started by selecting a feature from the navigation above and unlock the power of AI-driven financial analysis!**")

def render_stock_analyzer_page():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("📊 Advanced Stock Analyzer")
    st.markdown("Comprehensive analysis dashboard for Indian and US markets")
    
    # --- FILTERS ---
    with st.expander("🔍 Show Analysis Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_country = st.selectbox("🌍 Market Region", ["All", "India", "USA"])
        with col2:
            unique_sectors = sorted(all_stocks_df['sector'].unique())
            selected_sector = st.selectbox("🏢 Industry Sector", ["All"] + unique_sectors)
        
        # Filter company list based on the selections above
        temp_df = all_stocks_df.copy()
        if selected_country != "All": temp_df = temp_df[temp_df['country'] == selected_country]
        if selected_sector != "All": temp_df = temp_df[temp_df['sector'] == selected_sector]
        available_company_names = sorted(temp_df['name'].unique())
        
        with col3:
            selected_company = st.selectbox("🔍 Select Stock for Deep Dive", ["None"] + available_company_names)

    # --- FILTERING LOGIC (for the main charts) ---
    filtered_df = all_stocks_df.copy()
    if selected_country != "All": filtered_df = filtered_df[filtered_df['country'] == selected_country]
    if selected_sector != "All": filtered_df = filtered_df[filtered_df['sector'] == selected_sector]

    if filtered_df.empty:
        st.warning("⚠️ No stocks match the selected filters.")
        st.stop()

    # --- RENDER DASHBOARD ---
    st.subheader("📈 Market Overview")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Companies Shown", f"{filtered_df.shape[0]}")
    kpi_col2.metric("Average Market Cap (USD B)", f"{filtered_df['market_cap_usd_b'].mean():.2f}")
    kpi_col3.metric("Average P/E Ratio", f"{filtered_df['pe_ratio'].mean():.2f}")

    st.divider()
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("🏆 Top Companies by Market Cap")
        
        # --- CHANGE IS HERE ---
        # The 'labels' argument is updated to your exact specifications.
        fig1 = px.bar(
            filtered_df.nlargest(15, 'market_cap_usd_b'), 
            x='name', 
            y='market_cap_usd_b', 
            color='sector',
            labels={
                "name": "Company Name",
                "market_cap_usd_b": "Market Cap (USD B)" # Kept B for billions for clarity
            }
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        st.subheader("🥧 Sector Distribution")
        sector_counts = filtered_df['sector'].value_counts()
        fig2 = px.pie(values=sector_counts.values, names=sector_counts.index, title="Companies by Sector")
        st.plotly_chart(fig2, use_container_width=True)
    
    # --- INDIVIDUAL STOCK ANALYSIS ---
    if selected_company != "None":
        st.divider()
        st.header(f"🔍 Deep Dive: {selected_company}")
        
        stock_data = all_stocks_df[all_stocks_df['name'] == selected_company]
        
        if not stock_data.empty:
            stock_info = stock_data.iloc[0].to_dict()
            ticker = stock_info.get('symbol', '')
            
            with st.spinner("🧠 Generating AI analysis..."):
                st.subheader("🤖 AI-Powered Analysis")
                summary = generate_stock_summary(stock_info)
                st.success(summary)
            
            charts_col1, charts_col2 = st.columns([2, 1])
            with charts_col1:
                st.subheader("📈 Price Chart")
                with st.spinner("Loading price data..."):
                    fig = visualizations.create_candlestick_chart(ticker, selected_company)
                    if fig: st.plotly_chart(fig, use_container_width=True)
            
            with charts_col2:
                st.subheader("📰 News Sentiment")
                with st.spinner("Analyzing market sentiment..."):
                    news = analyze_news_sentiment(fetcher.get_hybrid_news(stock_info))
                    if news:
                        fig_sentiment = visualizations.create_sentiment_pie_chart(news)
                        if fig_sentiment: st.plotly_chart(fig_sentiment, use_container_width=True)
            
            st.subheader("📰 Latest News & Analysis")
            if 'news' in locals() and news:
                news_df = visualizations.create_news_sentiment_df(news)
                st.dataframe(news_df, use_container_width=True, hide_index=True)
        else:
            st.error(f"❌ **{selected_company}** not found.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_doc_chat_page():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("📄 Intelligent Document Chat")
    st.markdown("Upload financial documents and get instant AI-powered insights")
    
    # Enhanced file uploader
    st.markdown("### 📁 Upload Your Document")
    uploaded_file = st.file_uploader(
        "Choose a financial PDF or DOCX file",
        type=['pdf', 'docx'],
        help="Supported formats: PDF, DOCX. Max size: 200MB"
    )
    
    if "doc_processed" not in st.session_state:
        st.session_state.doc_processed = False
    
    if uploaded_file:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Process Document", use_container_width=True):
                with st.spinner("🧠 Analyzing document content..."):
                    progress_bar = st.progress(0)
                    
                    # Simulate progress
                    progress_bar.progress(25)
                    raw_text = get_document_text(uploaded_file)
                    
                    if raw_text:
                        progress_bar.progress(50)
                        text_chunks = get_text_chunks(raw_text)
                        
                        progress_bar.progress(75)
                        get_vector_store(text_chunks)
                        
                        progress_bar.progress(90)
                        st.session_state.doc_summary = summarize_document_with_full_context(text_chunks)
                        st.session_state.doc_processed = True
                        
                        progress_bar.progress(100)
                        st.success("✅ Document processed successfully!")
                    else:
                        st.error("❌ Failed to extract text from document.")

    if st.session_state.doc_processed:
        st.divider()
        
        # Document Summary Section
        st.subheader("📋 AI-Generated Document Summary")
        st.markdown(f"""
        <div style="background: rgba(0, 255, 127, 0.1); border: 1px solid rgba(0, 255, 127, 0.3); 
                    border-radius: 12px; padding: 20px; margin: 20px 0;">
            {st.session_state.doc_summary}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Chat Interface
        st.subheader("💬 Ask Questions About Your Document")
        
        # Initialize chat history if not exists
        if "doc_chat_history" not in st.session_state:
            st.session_state.doc_chat_history = []
        
        # Display chat history
        for message in st.session_state.doc_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if user_question := st.chat_input("💭 Ask about the document's content..."):
            # Add user message to chat history
            st.session_state.doc_chat_history.append({"role": "user", "content": user_question})
            
            with st.chat_message("user"):
                st.markdown(user_question)
            
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching through document..."):
                    response = user_input(user_question)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.doc_chat_history.append({"role": "assistant", "content": response})
    
    else:
        # Show example usage when no document is uploaded
        st.markdown("### 💡 How to Use Document Chat")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📄 Step 1: Upload**
            - Choose your PDF or DOCX file
            - Financial reports work best
            - Annual reports, research papers, etc.
            """)
        
        with col2:
            st.markdown("""
            **⚡ Step 2: Process**
            - Click "Process Document"
            - AI analyzes the content
            - Get an instant summary
            """)
        
        with col3:
            st.markdown("""
            **💬 Step 3: Chat**
            - Ask specific questions
            - Get contextual answers
            - Explore document insights
            """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_ipo_analyzer_page():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("📈 Advanced IPO Analyzer")
    st.markdown("AI-powered analysis of IPO documents and prospectuses")
    
    # Language Selection
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🌐 Analysis Language")
        lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Bengali": "bn"}
        selected_lang_name = st.selectbox(
            "Choose your preferred language",
            list(lang_map.keys()),
            help="Analysis will be provided in your selected language"
        )
        target_lang_code = lang_map[selected_lang_name]
    
    with col2:
        st.markdown("### 📁 Upload IPO Document")
        uploaded_file = st.file_uploader(
            "Upload IPO prospectus (DRHP, Red Herring, etc.)",
            type=['pdf', 'docx'],
            help="Supported: PDF, DOCX files up to 200MB"
        )
    
    if uploaded_file:
        # File info
        st.info(f"📋 **File:** {uploaded_file.name} | **Size:** {uploaded_file.size/1024/1024:.1f} MB")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔬 Analyze IPO Document", use_container_width=True):
                with st.spinner(f"🧠 Performing comprehensive analysis in {selected_lang_name}..."):
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📄 Extracting document content...")
                    progress_bar.progress(20)
                    
                    raw_text = get_document_text(uploaded_file)
                    
                    if raw_text:
                        status_text.text("🔍 Analyzing business model and financials...")
                        progress_bar.progress(50)
                        
                        status_text.text("⚖️ Assessing risks and opportunities...")
                        progress_bar.progress(75)
                        
                        status_text.text(f"🌐 Generating analysis in {selected_lang_name}...")
                        progress_bar.progress(90)
                        
                        response = analyze_ipo_document(raw_text, target_lang_code)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Analysis complete!")
                        
                        st.divider()
                        st.subheader("📊 Comprehensive IPO Analysis")
                        
                        # Display analysis in a styled container
                        st.markdown(f"""
                        <div style="background: rgba(26, 26, 46, 0.8); border-radius: 16px; 
                                    padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1);
                                    box-shadow: 0 8px 25px rgba(0, 255, 127, 0.1);">
                            {response}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.error("❌ Could not extract text from the document. Please ensure the file is not corrupted.")
    
    else:
        # Show example and instructions
        st.markdown("### 💡 How IPO Analyzer Works")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 What We Analyze:**
            - Business model and revenue streams
            - Financial performance and ratios
            - Management team and governance
            - Risk factors and mitigation strategies
            - Competitive positioning
            - Valuation metrics and pricing
            - Growth prospects and market opportunity
            """)
        
        with col2:
            st.markdown("""
            **📋 Supported Documents:**
            - Draft Red Herring Prospectus (DRHP)
            - Red Herring Prospectus (RHP)
            - Final Prospectus
            - Offer documents
            - Investor presentations
            - Annual reports of pre-IPO companies
            """)
        
        st.info("🔹 **Pro Tip:** For best results, upload the complete DRHP or prospectus document. The AI will analyze all sections and provide comprehensive insights.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_retirement_planner_page():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("💰 Smart Retirement Planner")
    st.markdown("Create your personalized retirement strategy with AI-powered projections")
    
    # Language Selection
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🌐 Report Language")
        lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Bengali": "bn"}
        selected_lang_name = st.selectbox(
            "Choose language for your report",
            list(lang_map.keys()),
            help="Your retirement plan will be generated in the selected language"
        )
        target_lang_code = lang_map[selected_lang_name]
    
    # Enhanced Retirement Planning Form
    with st.form("enhanced_retirement_form", clear_on_submit=False):
        st.markdown("### 👤 Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            current_age = st.number_input(
                "Current Age", 
                min_value=18, 
                max_value=60, 
                value=30,
                help="Your current age in years"
            )
            
            monthly_salary = st.number_input(
                "Monthly Salary (₹)", 
                min_value=0, 
                value=75000, 
                step=5000,
                help="Your current monthly gross salary"
            )
            
            current_savings = st.number_input(
                "Current Savings (₹ Lakhs)", 
                min_value=0.0, 
                value=10.0, 
                step=0.5,
                help="Total savings across all accounts"
            )
        
        with col2:
            retirement_age = st.number_input(
                "Target Retirement Age", 
                min_value=40, 
                max_value=70, 
                value=60,
                help="Age at which you plan to retire"
            )
            
            monthly_expenses = st.number_input(
                "Monthly Expenses (₹)", 
                min_value=0, 
                value=40000, 
                step=5000,
                help="Your current monthly expenses"
            )
            
            salary_growth = st.slider(
                "Expected Annual Salary Growth (%)", 
                min_value=0, 
                max_value=20, 
                value=8,
                help="Expected percentage increase in salary per year"
            )
        
        st.markdown("### 📊 Investment Profile")
        
        col1, col2 = st.columns(2)
        with col1:
            risk_appetite = st.radio(
                "Risk Tolerance", 
                ["Conservative", "Moderate", "Aggressive"], 
                index=1,
                horizontal=True,
                help="Conservative: Low risk, stable returns | Moderate: Balanced approach | Aggressive: Higher risk, higher returns"
            )
        
        with col2:
            investment_experience = st.selectbox(
                "Investment Experience",
                ["Beginner", "Intermediate", "Advanced"],
                index=1,
                help="Your familiarity with investment products"
            )
        
        # Additional preferences
        st.markdown("### 🎯 Retirement Goals")
        
        col1, col2 = st.columns(2)
        with col1:
            retirement_lifestyle = st.selectbox(
                "Desired Retirement Lifestyle",
                ["Basic", "Comfortable", "Luxurious"],
                index=1,
                help="The lifestyle you want to maintain post-retirement"
            )
        
        with col2:
            inflation_assumption = st.slider(
                "Expected Inflation Rate (%)",
                min_value=3,
                max_value=8,
                value=6,
                help="Expected average inflation rate"
            )
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Generate My Retirement Plan", 
                use_container_width=True
            )

    if submitted:
        # Validation
        if retirement_age <= current_age:
            st.error("⚠️ Retirement age must be greater than current age!")
        else:
            # Prepare user data
            user_data = {
                "current_age": current_age,
                "retirement_age": retirement_age,
                "monthly_salary_inr": monthly_salary,
                "monthly_expenses_inr": monthly_expenses,
                "current_savings_inr": int(current_savings * 100000),
                "expected_salary_growth_percent": salary_growth,
                "risk_appetite": risk_appetite,
                "investment_experience": investment_experience,
                "retirement_lifestyle": retirement_lifestyle,
                "expected_inflation_percent": inflation_assumption
            }
            
            with st.spinner(f"🧠 Creating your personalized retirement plan in {selected_lang_name}..."):
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("📊 Analyzing your financial profile...")
                progress_bar.progress(25)
                
                status_text.text("💰 Calculating retirement corpus requirements...")
                progress_bar.progress(50)
                
                status_text.text("📈 Optimizing investment strategy...")
                progress_bar.progress(75)
                
                status_text.text(f"🌐 Generating report in {selected_lang_name}...")
                progress_bar.progress(90)
                
                response = generate_retirement_plan(user_data, target_lang_code)
                
                progress_bar.progress(100)
                status_text.text("✅ Your retirement plan is ready!")
                
                st.divider()
                st.subheader("📋 Your Personalized Retirement Roadmap")
                
                # Display in styled container
                st.markdown(f"""
                <div style="background: rgba(26, 26, 46, 0.8); border-radius: 16px; 
                            padding: 30px; border: 1px solid rgba(255, 255, 255, 0.1);
                            box-shadow: 0 8px 25px rgba(0, 255, 127, 0.1);">
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
                # Quick action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info("💡 **Next Step:** Review and implement the suggested investment strategy")
                with col2:
                    st.info("📅 **Reminder:** Review your plan annually and adjust as needed")
                with col3:
                    st.info("🎯 **Goal:** Stay disciplined and consistent with your savings")
    
    else:
        # Show retirement planning tips when form is not submitted
        st.markdown("### 💡 Retirement Planning Tips")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **⏰ Start Early**
            - Time is your biggest asset
            - Compound interest works wonders
            - Even small amounts help
            """)
        
        with col2:
            st.markdown("""
            **🎯 Set Clear Goals**
            - Define retirement lifestyle
            - Calculate required corpus
            - Plan for inflation
            """)
        
        with col3:
            st.markdown("""
            **📊 Diversify Investments**
            - Don't put all eggs in one basket
            - Balance risk and returns
            - Review periodically
            """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_fin_chat_page():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("💬 FinChat AI Assistant")
    st.markdown("Your intelligent financial advisor - Ask questions in any language!")
    
    # Enhanced language selection and settings
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🌐 Language Settings")
        lang_map = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Tamil": "ta", "Bengali": "bn"}
        selected_lang_name = st.selectbox(
            "Choose your language",
            list(lang_map.keys()),
            help="Ask questions and receive answers in your preferred language"
        )
        target_lang_code = lang_map[selected_lang_name]
        
        st.info(f"🗣️ **Active:** {selected_lang_name}")
    
    with col2:
        st.markdown("### 📁 Add Context (Optional)")
        uploaded_file = st.file_uploader(
            "Upload a file to provide additional context",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload documents or images for more contextual responses"
        )
        
        if uploaded_file:
            st.success(f"📄 **File loaded:** {uploaded_file.name}")

    st.divider()

    # Initialize chat history
    if "fin_messages" not in st.session_state:
        st.session_state.fin_messages = []
        # Add welcome message
        welcome_msg = f"👋 Hello! I'm your FinChat AI assistant. Ask me anything about finance, investments, markets, or personal financial planning in {selected_lang_name}!"
        st.session_state.fin_messages.append({"role": "assistant", "content": welcome_msg})

    # Display chat history with enhanced styling
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.fin_messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Enhanced chat input with suggestions
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Sample questions based on language
        sample_questions = {
            "English": [
                "What are the best investment options for beginners?",
                "How should I plan for retirement at age 30?",
                "Explain the current market trends in Indian stocks"
            ],
            "Hindi": [
                "नए निवेशकों के लिए सबसे अच्छे विकल्प क्या हैं?",
                "30 साल की उम्र में रिटायरमेंट की योजना कैसे बनाऊं?",
                "भारतीय शेयर बाजार के रुझान बताएं"
            ],
            "Marathi": [
                "नवीन गुंतवणूकदारांसाठी सर्वोत्तम पर्याय कोणते आहेत?",
                "३० वयात निवृत्तीची योजना कशी करावी?",
                "भारतीय शेअर बाजारातील ट्रेंड समजावा"
            ]
        }
        
        # Show sample questions
        if selected_lang_name in sample_questions:
            with st.expander("💡 Sample Questions"):
                for q in sample_questions[selected_lang_name]:
                    if st.button(q, key=f"sample_{hash(q)}"):
                        # Use the sample question as input
                        user_prompt = q
                        # Process the question
                        st.session_state.fin_messages.append({"role": "user", "content": user_prompt})
                        
                        with st.spinner("🧠 Thinking..."):
                            file_context = ""
                            if uploaded_file:
                                file_context = process_uploaded_file(uploaded_file)
                            
                            # Translate to English for processing if needed
                            english_prompt = translate_text(user_prompt, 'en') if target_lang_code != 'en' else user_prompt
                            english_response = get_comprehensive_response(english_prompt, fetcher, file_context)
                            
                            # Translate response back to target language if needed
                            final_response = translate_text(english_response, target_lang_code, "English") if target_lang_code != 'en' else english_response
                            
                            st.session_state.fin_messages.append({"role": "assistant", "content": final_response})
                            st.rerun()

    # Main chat input
    if prompt := st.chat_input(f"💭 Ask a financial question in {selected_lang_name}..."):
        # Add user message to chat history
        st.session_state.fin_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🧠 Analyzing your question..."):
                # Process uploaded file if available
                file_context = ""
                if uploaded_file:
                    with st.status("📄 Processing uploaded file..."):
                        file_context = process_uploaded_file(uploaded_file)
                
                # Translate question to English for processing if needed
                english_prompt = translate_text(prompt, 'en') if target_lang_code != 'en' else prompt
                
                # Get response from AI
                english_response = get_comprehensive_response(english_prompt, fetcher, file_context)
                
                # Translate response back to target language if needed
                final_response = translate_text(english_response, target_lang_code, "English") if target_lang_code != 'en' else english_response
                
                st.markdown(final_response)
        
        # Add assistant response to chat history
        st.session_state.fin_messages.append({"role": "assistant", "content": final_response})
        st.rerun()

    # Chat controls
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Clear Chat", help="Start a fresh conversation"):
            st.session_state.fin_messages = []
            welcome_msg = f"👋 Hello! I'm your FinChat AI assistant. Ask me anything about finance in {selected_lang_name}!"
            st.session_state.fin_messages.append({"role": "assistant", "content": welcome_msg})
            st.rerun()
    
    with col2:
        message_count = len([msg for msg in st.session_state.fin_messages if msg["role"] == "user"])
        st.metric("💬 Questions Asked", message_count)
    
    with col3:
        st.info("🔒 **Privacy:** Your conversations are secure and not stored permanently")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN APPLICATION LOGIC ---

# Initialize session state for current page
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Render navigation and get pages
PAGES = render_navigation()

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# Render the selected page
try:
    PAGES[st.session_state.current_page]["function"]()
except Exception as e:
    st.error(f"❌ An error occurred while loading the page: {str(e)}")
    st.info("🔄 Please try refreshing the page or contact support if the issue persists.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p>🚀 <strong>FinChat</strong> - Democratizing Financial Intelligence with AI</p>
</div>
""", unsafe_allow_html=True)
