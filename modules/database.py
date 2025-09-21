# This file contains the comprehensive database of Indian and US stocks.
# It is imported by other modules to access stock information.

COMPREHENSIVE_STOCKS_DATABASE = {
    # INDIAN STOCKS (120+ companies)
    "INDIAN_STOCKS": {
        # NIFTY 50 Companies
        "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Oil & Gas", "exchange": "NSE"},
        "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT Services", "exchange": "NSE"},
        "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking", "exchange": "NSE"},
        "INFY.NS": {"name": "Infosys", "sector": "IT Services", "exchange": "NSE"},
        "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking", "exchange": "NSE"},
        "HINDUNILVR.NS": {"name": "Hindustan Unilever", "sector": "FMCG", "exchange": "NSE"},
        "ITC.NS": {"name": "ITC Limited", "sector": "FMCG", "exchange": "NSE"},
        "SBIN.NS": {"name": "State Bank of India", "sector": "Banking", "exchange": "NSE"},
        "BHARTIARTL.NS": {"name": "Bharti Airtel", "sector": "Telecom", "exchange": "NSE"},
        "ASIANPAINT.NS": {"name": "Asian Paints", "sector": "Paints", "exchange": "NSE"},
        "MARUTI.NS": {"name": "Maruti Suzuki", "sector": "Automobile", "exchange": "NSE"},
        "HCLTECH.NS": {"name": "HCL Technologies", "sector": "IT Services", "exchange": "NSE"},
        "LT.NS": {"name": "Larsen & Toubro", "sector": "Engineering", "exchange": "NSE"},
        "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "sector": "Banking", "exchange": "NSE"},
        "TITAN.NS": {"name": "Titan Company", "sector": "Jewellery", "exchange": "NSE"},
        "WIPRO.NS": {"name": "Wipro", "sector": "IT Services", "exchange": "NSE"},
        "SUNPHARMA.NS": {"name": "Sun Pharmaceutical", "sector": "Pharmaceuticals", "exchange": "NSE"},
        "NESTLEIND.NS": {"name": "Nestle India", "sector": "FMCG", "exchange": "NSE"},
        "ULTRACEMCO.NS": {"name": "UltraTech Cement", "sector": "Cement", "exchange": "NSE"},
        "AXISBANK.NS": {"name": "Axis Bank", "sector": "Banking", "exchange": "NSE"},
        "M&M.NS": {"name": "Mahindra & Mahindra", "sector": "Automobile", "exchange": "NSE"},
        "BAJFINANCE.NS": {"name": "Bajaj Finance", "sector": "NBFC", "exchange": "NSE"},
        "POWERGRID.NS": {"name": "Power Grid Corporation", "sector": "Power", "exchange": "NSE"},
        "NTPC.NS": {"name": "NTPC Limited", "sector": "Power", "exchange": "NSE"},
        "TECHM.NS": {"name": "Tech Mahindra", "sector": "IT Services", "exchange": "NSE"},
        
        # Other Major Indian Companies
        "ADANIPORTS.NS": {"name": "Adani Ports", "sector": "Ports", "exchange": "NSE"},
        "ADANIGREEN.NS": {"name": "Adani Green Energy", "sector": "Renewable Energy", "exchange": "NSE"},
        "TATAMOTORS.NS": {"name": "Tata Motors", "sector": "Automobile", "exchange": "NSE"},
        "TATASTEEL.NS": {"name": "Tata Steel", "sector": "Steel", "exchange": "NSE"},
        "JSWSTEEL.NS": {"name": "JSW Steel", "sector": "Steel", "exchange": "NSE"},
        "VEDL.NS": {"name": "Vedanta Limited", "sector": "Mining", "exchange": "NSE"},
        "CIPLA.NS": {"name": "Cipla", "sector": "Pharmaceuticals", "exchange": "NSE"},
        "DRREDDY.NS": {"name": "Dr. Reddy's Laboratories", "sector": "Pharmaceuticals", "exchange": "NSE"},
        "EICHERMOT.NS": {"name": "Eicher Motors", "sector": "Automobile", "exchange": "NSE"},
        "BAJAJFINSV.NS": {"name": "Bajaj Finserv", "sector": "Financial Services", "exchange": "NSE"},
        "HDFCLIFE.NS": {"name": "HDFC Life Insurance", "sector": "Insurance", "exchange": "NSE"},
        "SBILIFE.NS": {"name": "SBI Life Insurance", "sector": "Insurance", "exchange": "NSE"},
        "ICICIPRULI.NS": {"name": "ICICI Prudential Life", "sector": "Insurance", "exchange": "NSE"},
        "BAJAJ-AUTO.NS": {"name": "Bajaj Auto", "sector": "Automobile", "exchange": "NSE"},
        "HEROMOTOCO.NS": {"name": "Hero MotoCorp", "sector": "Automobile", "exchange": "NSE"},
        "BRITANNIA.NS": {"name": "Britannia Industries", "sector": "FMCG", "exchange": "NSE"},
        "DABUR.NS": {"name": "Dabur India", "sector": "FMCG", "exchange": "NSE"},
        "GODREJCP.NS": {"name": "Godrej Consumer Products", "sector": "FMCG", "exchange": "NSE"},
        "MARICO.NS": {"name": "Marico", "sector": "FMCG", "exchange": "NSE"},
        "DIVISLAB.NS": {"name": "Divi's Laboratories", "sector": "Pharmaceuticals", "exchange": "NSE"},
        "BIOCON.NS": {"name": "Biocon", "sector": "Biotechnology", "exchange": "NSE"},
        "LUPIN.NS": {"name": "Lupin", "sector": "Pharmaceuticals", "exchange": "NSE"},
        "CADILAHC.NS": {"name": "Cadila Healthcare", "sector": "Pharmaceuticals", "exchange": "NSE"},
        "APOLLOHOSP.NS": {"name": "Apollo Hospitals", "sector": "Healthcare", "exchange": "NSE"},
        "FORTIS.NS": {"name": "Fortis Healthcare", "sector": "Healthcare", "exchange": "NSE"},
        "MINDTREE.NS": {"name": "Mindtree", "sector": "IT Services", "exchange": "NSE"},
        "MPHASIS.NS": {"name": "Mphasis", "sector": "IT Services", "exchange": "NSE"},
        "LTI.NS": {"name": "L&T Infotech", "sector": "IT Services", "exchange": "NSE"},
        "COFORGE.NS": {"name": "Coforge", "sector": "IT Services", "exchange": "NSE"},
        "PERSISTENT.NS": {"name": "Persistent Systems", "sector": "IT Services", "exchange": "NSE"},
        "BANKBARODA.NS": {"name": "Bank of Baroda", "sector": "Banking", "exchange": "NSE"},
        "PNB.NS": {"name": "Punjab National Bank", "sector": "Banking", "exchange": "NSE"},
        "CANBK.NS": {"name": "Canara Bank", "sector": "Banking", "exchange": "NSE"},
        "INDUSINDBK.NS": {"name": "IndusInd Bank", "sector": "Banking", "exchange": "NSE"},
        "FEDERALBNK.NS": {"name": "Federal Bank", "sector": "Banking", "exchange": "NSE"},
        "YESBANK.NS": {"name": "Yes Bank", "sector": "Banking", "exchange": "NSE"},
        "ONGC.NS": {"name": "Oil & Natural Gas Corp", "sector": "Oil & Gas", "exchange": "NSE"},
        "IOC.NS": {"name": "Indian Oil Corporation", "sector": "Oil & Gas", "exchange": "NSE"},
        "BPCL.NS": {"name": "Bharat Petroleum", "sector": "Oil & Gas", "exchange": "NSE"},
        "HPCL.NS": {"name": "Hindustan Petroleum", "sector": "Oil & Gas", "exchange": "NSE"},
        "GAIL.NS": {"name": "GAIL India", "sector": "Oil & Gas", "exchange": "NSE"},
        "COALINDIA.NS": {"name": "Coal India", "sector": "Mining", "exchange": "NSE"},
        "SAIL.NS": {"name": "Steel Authority of India", "sector": "Steel", "exchange": "NSE"},
        "HINDALCO.NS": {"name": "Hindalco Industries", "sector": "Metals", "exchange": "NSE"},
        "JINDALSTEL.NS": {"name": "Jindal Steel & Power", "sector": "Steel", "exchange": "NSE"},
        "NMDC.NS": {"name": "NMDC Limited", "sector": "Mining", "exchange": "NSE"},
        "DLF.NS": {"name": "DLF Limited", "sector": "Real Estate", "exchange": "NSE"},
        "GODREJPROP.NS": {"name": "Godrej Properties", "sector": "Real Estate", "exchange": "NSE"},
        "OBEROIRLTY.NS": {"name": "Oberoi Realty", "sector": "Real Estate", "exchange": "NSE"},
        "PRESTIGE.NS": {"name": "Prestige Estates", "sector": "Real Estate", "exchange": "NSE"},
        "SOBHA.NS": {"name": "Sobha Limited", "sector": "Real Estate", "exchange": "NSE"},
        "SIEMENS.NS": {"name": "Siemens India", "sector": "Industrial Equipment", "exchange": "NSE"},
        "ABB.NS": {"name": "ABB India", "sector": "Industrial Equipment", "exchange": "NSE"},
        "BHEL.NS": {"name": "Bharat Heavy Electricals", "sector": "Industrial Equipment", "exchange": "NSE"},
        "CUMMINSIND.NS": {"name": "Cummins India", "sector": "Industrial Equipment", "exchange": "NSE"},
        "THERMAX.NS": {"name": "Thermax Limited", "sector": "Industrial Equipment", "exchange": "NSE"},
        "CONCOR.NS": {"name": "Container Corporation", "sector": "Logistics", "exchange": "NSE"},
        "BLUEDART.NS": {"name": "Blue Dart Express", "sector": "Logistics", "exchange": "NSE"},
        "VBL.NS": {"name": "Varun Beverages", "sector": "Beverages", "exchange": "NSE"},
        "TATACONSUM.NS": {"name": "Tata Consumer Products", "sector": "FMCG", "exchange": "NSE"},
        "UBL.NS": {"name": "United Breweries", "sector": "Beverages", "exchange": "NSE"},
        "JUBLFOOD.NS": {"name": "Jubilant FoodWorks", "sector": "Food Services", "exchange": "NSE"},
        "ZOMATO.NS": {"name": "Zomato", "sector": "Food Tech", "exchange": "NSE"},
        "NYKAA.NS": {"name": "Nykaa", "sector": "E-commerce", "exchange": "NSE"},
        "PAYTM.NS": {"name": "Paytm", "sector": "Fintech", "exchange": "NSE"},
        "POLICYBZR.NS": {"name": "PB Fintech", "sector": "Fintech", "exchange": "NSE"},
        "MCDOWELL-N.NS": {"name": "United Spirits", "sector": "Alcoholic Beverages", "exchange": "NSE"},
        "PIDILITIND.NS": {"name": "Pidilite Industries", "sector": "Chemicals", "exchange": "NSE"},
        "BERGER.NS": {"name": "Berger Paints", "sector": "Paints", "exchange": "NSE"},
        "KANSAINER.NS": {"name": "Kansai Nerolac Paints", "sector": "Paints", "exchange": "NSE"},
        "SHREECEM.NS": {"name": "Shree Cement", "sector": "Cement", "exchange": "NSE"},
        "ACC.NS": {"name": "ACC Limited", "sector": "Cement", "exchange": "NSE"},
        "AMBUJACEMENT.NS": {"name": "Ambuja Cements", "sector": "Cement", "exchange": "NSE"},
        "RAMCOCEM.NS": {"name": "Ramco Cements", "sector": "Cement", "exchange": "NSE"},
        "JKCEMENT.NS": {"name": "JK Cement", "sector": "Cement", "exchange":.NS": "NSE"},
        "VOLTAS.NS": {"name": "Voltas", "sector": "Consumer Appliances", "exchange": "NSE"},
        "WHIRLPOOL.NS": {"name": "Whirlpool of India", "sector": "Consumer Appliances", "exchange": "NSE"},
        "CROMPTON.NS": {"name": "Crompton Greaves", "sector": "Consumer Appliances", "exchange": "NSE"},
        "HAVELLS.NS": {"name": "Havells India", "sector": "Electrical Equipment", "exchange": "NSE"},
        "POLYCAB.NS": {"name": "Polycab India", "sector": "Electrical Equipment", "exchange": "NSE"},
        "KEI.NS": {"name": "KEI Industries", "sector": "Electrical Equipment", "exchange": "NSE"}
    },
    
    # US STOCKS (60+ major companies)
    "US_STOCKS": {
        # Tech Giants
        "AAPL": {"name": "Apple Inc.", "sector": "Technology", "exchange": "NASDAQ"},
        "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "exchange": "NASDAQ"},
        "GOOGL": {"name": "Alphabet Inc.",.NS": "Technology", "exchange": "NASDAQ"},
        "AMZN": {"name": "Amazon.com Inc.", "sector": "E-commerce", "exchange": "NASDAQ"},
        "TSLA": {"name": "Tesla Inc.", "sector": "Electric Vehicles", "exchange": "NASDAQ"},
        "META": {"name": "Meta Platforms Inc.", "sector": "Social Media", "exchange": "NASDAQ"},
        "NFLX": {"name": "Netflix Inc.", "sector": "Streaming", "exchange": "NASDAQ"},
        "NVDA": {"name": "NVIDIA Corporation", "sector": "Semiconductors", "exchange": "NASDAQ"},
        "AMD": {"name": "Advanced Micro Devices", "sector": "Semiconductors", "exchange": "NASDAQ"},
        "INTC": {"name": "Intel Corporation", "sector": "Semiconductors", "exchange": "NASDAQ"},
        "CRM": {"name": "Salesforce Inc.", "sector": "Cloud Software", "exchange": "NYSE"},
        "ORCL": {"name": "Oracle Corporation", "sector": "Software", "exchange": "NYSE"},
        "ADBE": {"name": "Adobe Inc.", "sector": "Software", "exchange": "NASDAQ"},
        "PYPL": {"name": "PayPal Holdings", "sector": "Fintech", "exchange": "NASDAQ"},
        "UBER": {"name": "Uber Technologies", "sector": "Transportation", "exchange": "NYSE"},
        
        # Financial Services
        "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Banking", "exchange": "NYSE"},
        "BAC": {"name": "Bank of America", "sector": "Banking", "exchange": "NYSE"},
        "WFC": {"name": "Wells Fargo & Co.", "sector": "Banking", "exchange": "NYSE"},
        "C": {"name": "Citigroup Inc.", "sector": "Banking", "exchange": "NYSE"},
        "GS": {"name": "Goldman Sachs Group", "sector": "Investment Banking", "exchange": "NYSE"},
        "MS": {"name": "Morgan Stanley", "sector": "Investment Banking", "exchange": "NYSE"},
        "AXP": {"name": "American Express", "sector": "Financial Services", "exchange": "NYSE"},
        "V": {"name": "Visa Inc.", "sector": "Payment Processing", "exchange": "NYSE"},
        "MA": {"name": "Mastercard Inc.", "sector": "Payment Processing", "exchange": "NYSE"},
        "BRK.B": {"name": "Berkshire Hathaway", "sector": "Conglomerate", "exchange": "NYSE"},
        
        # Healthcare & Pharmaceuticals
        "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare", "exchange": "NYSE"},
        "PFE": {"name": "Pfizer Inc.", "sector": "Pharmaceuticals", "exchange": "NYSE"},
        "UNH": {"name": "UnitedHealth Group", "sector": "Healthcare", "exchange": "NYSE"},
        "MRNA": {"name": "Moderna Inc.", "sector": "Biotechnology", "exchange": "NASDAQ"},
        "ABBV": {"name": "AbbVie Inc.", "sector": "Pharmaceuticals", "exchange": "NYSE"},
        "TMO": {"name": "Thermo Fisher Scientific", "sector": "Life Sciences", "exchange": "NYSE"},
        "ABT": {"name": "Abbott Laboratories", "sector": "Healthcare", "exchange": "NYSE"},
        "MDT": {"name": "Medtronic plc", "sector": "Medical Devices", "exchange": "NYSE"},
        
        # Consumer Goods
        "KO": {"name": "The Coca-Cola Company", "sector": "Beverages", "exchange": "NYSE"},
        "PEP": {"name": "PepsiCo Inc.", "sector": "Beverages", "exchange": "NASDAQ"},
        "PG": {"name": "Procter & Gamble", "sector": "Consumer Products", "exchange": "NYSE"},
        "WMT": {"name": "Walmart Inc.", "sector": "Retail", "exchange": "NYSE"},
        "HD": {"name": "The Home Depot", "sector": "Retail", "exchange":.NS": "NYSE"},
        "NKE": {"name": "Nike Inc.", "sector": "Apparel", "exchange": "NYSE"},
        "MCD": {"name": "McDonald's Corporation", "sector": "Restaurants", "exchange": "NYSE"},
        "SBUX": {"name": "Starbucks Corporation", "sector": "Restaurants", "exchange": "NASDAQ"},
        
        # Industrial & Energy
        "BA": {"name": "The Boeing Company", "sector": "Aerospace", "exchange": "NYSE"},
        "CAT": {"name": "Caterpillar Inc.", "sector": "Industrial Machinery", "exchange": "NYSE"},
        "GE": {"name": "General Electric", "sector": "Conglomerate", "exchange": "NYSE"},
        "XOM": {"name": "Exxon Mobil Corporation", "sector": "Oil & Gas", "exchange": "NYSE"},
        "CVX": {"name": "Chevron Corporation", "sector": "Oil & Gas", "exchange": "NYSE"},
        "COP": {"name": "ConocoPhillips", "sector": "Oil & Gas", "exchange": "NYSE"},
        
        # Communication Services
        "DIS": {"name": "The Walt Disney Company", "sector": "Entertainment", "exchange": "NYSE"},
        "CMCSA": {"name": "Comcast Corporation", "sector": "Telecom", "exchange": "NASDAQ"},
        "VZ": {"name": "Verizon Communications", "sector": "Telecom", "exchange": "NYSE"},
        "T": {"name": "AT&T Inc.", "sector": "Telecom", "exchange": "NYSE"},
        
        # Real Estate & Utilities
        "NEE": {"name": "NextEra Energy", "sector": "Utilities", "exchange": "NYSE"},
        "DUK": {"name": "Duke Energy", "sector": "Utilities", "exchange": "NYSE"},
        "SO": {"name": "Southern Company", "sector": "Utilities", "exchange": "NYSE"},
        "AMT": {".NS": "American Tower", "sector": "REITs", "exchange": "NYSE"},
        
        # Emerging Tech
        "PLTR": {"name": "Palantir Technologies", "sector": "Data Analytics", "exchange": "NYSE"},
        "SNOW": {"name": "Snowflake Inc.", "sector": "Cloud Computing", "exchange": "NYSE"},
        "ZM": {"name": "Zoom Video Communications", "sector": "Video Conferencing", "exchange": "NASDAQ"},
        "SHOP": {"name": "Shopify Inc.", "sector": "E-commerce", "exchange": "NYSE"},
        "SQ": {"name": "Block Inc.", "sector": "Fintech", "exchange": "NYSE"},
        "ROKU": {"name": "Roku Inc.", "sector": "Streaming", "exchange": "NASDAQ"},
    }
}}}}

def get_all_tickers():
    """Returns a list of all stock tickers in the database."""
    indian_tickers = list(COMPREHENSIVE_STOCKS_DATABASE["INDIAN_STOCKS"].keys())
    us_tickers = list(COMPREHENSIVE_STOCKS_DATABASE["US_STOCKS"].keys())
    return indian_tickers + us_tickers

def get_stock_info(ticker):
    """
    Retrieves stock information for a given ticker from the database.

    Args:
        ticker (str): The stock ticker (e.g., "RELIANCE.NS", "AAPL").

    Returns:
        dict: A dictionary containing stock information (name, sector, exchange)
              or None if the ticker is not found.
    """
    if not isinstance(ticker, str) or not ticker:
        print("Error: Ticker must be a non-empty string.")
        return None

    ticker = ticker.upper()
    
    if ticker in COMPREHENSIVE_STOCKS_DATABASE["INDIAN_STOCKS"]:
        return COMPREHENSIVE_STOCKS_DATABASE["INDIAN_STOCKS"][ticker]
    elif ticker in COMPREHENSIVE_STOCKS_DATABASE["US_STOCKS"]:
        return COMPREHENSIVE_STOCKS_DATABASE["US_STOCKS"][ticker]
    else:
        print(f"Warning: Ticker '{ticker}' not found in the local database.")
        return None

def search_stocks(query):
    """
    Searches for stocks by ticker or company name.

    Args:
        query (str): The search query (e.g., "Reliance", "TCS.NS").

    Returns:
        dict: A dictionary of matching stocks, with ticker as key and info as value.
    """
    if not isinstance(query, str) or not query:
        print("Error: Search query must be a non-empty string.")
        return {}
        
    query = query.lower()
    results = {}
    
    for ticker, info in COMPREHENSIVE_STOCKS_DATABASE["INDIAN_STOCKS"].items():
        if query in ticker.lower() or query in info["name"].lower():
            results[ticker] = info
            
    for ticker, info in COMPREHENSIVE_STOCKS_DATABASE["US_STOCKS"].items():
        if query in ticker.lower() or query in info["name"].lower():
            results[ticker] = info
            
    return results

# Validation check to ensure the database is not empty
def is_database_valid():
    """
    Validates the integrity of the stocks database.
    
    Returns:
        bool: True if the database is valid, False otherwise.
    """
    if not COMPREHENSIVE_STOCKS_DATABASE:
        print("Error: The comprehensive stocks database is empty.")
        return False
    if "INDIAN_STOCKS" not in COMPREHENSIVE_STOCKS_DATABASE or "US_STOCKS" not in COMPREHENSIVE_STOCKS_DATABASE:
        print("Error: The database is missing 'INDIAN_STOCKS' or 'US_STOCKS'.")
        return False
    if not isinstance(COMPREHENSIVE_STOCKS_DATABASE["INDIAN_STOCKS"], dict) or not isinstance(COMPREHENSIVE_STOCKS_DATABASE["US_STOCKS"], dict):
        print("Error: Stock lists must be dictionaries.")
        return False
    
    print("Database validation successful.")
    return True

# Run a validation check when the module is loaded
is_database_valid()