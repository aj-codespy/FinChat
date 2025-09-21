import json
import os

# Get the absolute path to the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the data.txt file
data_file_path = os.path.join(script_dir, '..', 'data.txt')

# Load the stock data from the text file
with open(data_file_path, 'r') as f:
    COMPREHENSIVE_STOCKS_DATABASE = json.load(f)

def get_stock_info(ticker):
    """Retrieves information for a given stock ticker from the local database."""
    print(f"ℹ️ DB: Searching for ticker '{ticker}' in the database.")
    
    # Check in Indian stocks
    if ticker in COMPREHENSIVE_STOCKS_DATABASE.get("INDIAN_STOCKS", {}):
        print(f"✅ DB: Found '{ticker}' in Indian stocks.")
        return COMPREHENSIVE_STOCKS_DATABASE["INDIAN_STOCKS"][ticker]
    
    # Check in US stocks
    if ticker in COMPREHENSIVE_STOCKS_DATABASE.get("US_STOCKS", {}):
        print(f"✅ DB: Found '{ticker}' in US stocks.")
        return COMPREHENSIVE_STOCKS_DATABASE["US_STOCKS"][ticker]
        
    print(f"⚠️ DB: Ticker '{ticker}' not found in the database.")
    return None

def search_stocks(query):
    """Searches for stocks by ticker or name in the local database."""
    if not query:
        return {}
        
    print(f"ℹ️ DB: Starting stock search for query: '{query}'")
    query = query.lower()
    results = {}
    
    # Search in Indian stocks
    for ticker, info in COMPREHENSIVE_STOCKS_DATABASE.get("INDIAN_STOCKS", {}).items():
        if query in ticker.lower() or query in info.get("name", "").lower():
            results[ticker] = info
            
    # Search in US stocks
    for ticker, info in COMPREHENSIVE_STOCKS_DATABASE.get("US_STOCKS", {}).items():
        if query in ticker.lower() or query in info.get("name", "").lower():
            results[ticker] = info
            
    print(f"✅ DB: Found {len(results)} results for query '{query}'.")
    return results

# Example Usage (for testing)
if __name__ == '__main__':
    # Test get_stock_info
    print("\n--- Testing get_stock_info ---")
    reliance_info = get_stock_info("RELIANCE.NS")
    if reliance_info:
        print("Found Reliance:")
        # print(json.dumps(reliance_info, indent=2))
    
    apple_info = get_stock_info("AAPL")
    if apple_info:
        print("\nFound Apple:")
        # print(json.dumps(apple_info, indent=2))
        
    invalid_info = get_stock_info("INVALIDTICKER")
    if not invalid_info:
        print("\nCorrectly handled invalid ticker.")

    # Test search_stocks
    print("\n--- Testing search_stocks ---")
    tata_results = search_stocks("tata")
    print(f"Found {len(tata_results)} stocks with 'tata':")
    for ticker, info in tata_results.items():
        print(f"  - {ticker}: {info['name']}")
        
    tech_results = search_stocks("tech")
    print(f"\nFound {len(tech_results)} stocks with 'tech':")
    for ticker, info in tech_results.items():
        print(f"  - {ticker}: {info['name']}")
        
    empty_results = search_stocks("")
    if not empty_results:
        print("\nCorrectly handled empty search query.")