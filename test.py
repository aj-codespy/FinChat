import requests
import json
from datetime import datetime
from urllib.parse import quote_plus, urljoin
import time
from typing import List, Dict, Optional
import feedparser

# API Keys - Get these for free from the respective services
BRAVE_API_KEY = "YOUR_BRAVE_API_KEY"  # Get from https://brave.com/search/api/
SERPAPI_KEY = "YOUR_SERPAPI_KEY"      # Get from https://serpapi.com/
FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_KEY"  # Get from https://firecrawl.dev/

class EnhancedNewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def jina_extract_content(self, url: str) -> str:
        """
        Use Jina Reader API for LLM-optimized content extraction (FREE)
        No API key required - just prepend the URL
        """
        try:
            jina_url = f"https://r.jina.ai/{url}"
            print(f"    🤖 Using Jina AI to extract content...")
            
            response = self.session.get(jina_url, timeout=20)
            response.raise_for_status()
            
            content = response.text
            
            # Jina returns markdown-formatted content, perfect for LLMs
            if content and len(content.strip()) > 100:
                # Limit to first 300 words for preview
                words = content.split()[:300]
                result = ' '.join(words)
                return result + ('...' if len(content.split()) > 300 else '')
            
            return "Content too short or extraction failed"
            
        except Exception as e:
            return f"❌ Jina extraction failed: {str(e)[:100]}"
    
    def firecrawl_extract_content(self, url: str) -> str:
        """
        Use FireCrawl API for advanced content extraction
        """
        if FIRECRAWL_API_KEY == "YOUR_FIRECRAWL_KEY":
            return "⚠️ FireCrawl API key not configured"
        
        try:
            firecrawl_url = "https://api.firecrawl.dev/v0/scrape"
            headers = {
                'Authorization': f'Bearer {FIRECRAWL_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': url,
                'formats': ['markdown'],
                'onlyMainContent': True
            }
            
            print(f"    🔥 Using FireCrawl to extract content...")
            response = self.session.post(firecrawl_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if data.get('success') and data.get('data', {}).get('markdown'):
                content = data['data']['markdown']
                words = content.split()[:300]
                result = ' '.join(words)
                return result + ('...' if len(content.split()) > 300 else '')
            
            return "FireCrawl extraction failed"
            
        except Exception as e:
            return f"❌ FireCrawl error: {str(e)[:100]}"
    
    def extract_with_multiple_methods(self, url: str) -> str:
        """
        Try multiple extraction methods in order of preference
        """
        methods = [
            ("Jina AI (Free)", lambda: self.jina_extract_content(url)),
            ("FireCrawl", lambda: self.firecrawl_extract_content(url)),
        ]
        
        for method_name, method_func in methods:
            try:
                result = method_func()
                if result and not result.startswith("❌") and not result.startswith("⚠️") and len(result) > 50:
                    return f"[{method_name}] {result}"
            except Exception:
                continue
        
        return "❌ All extraction methods failed"

class EnhancedLinkFetcher:
    def __init__(self):
        self.session = requests.Session()
    
    def search_brave_api(self, query: str, count: int = 10) -> List[Dict]:
        """
        Use Brave Search API for clean, direct article URLs
        """
        if BRAVE_API_KEY == "YOUR_BRAVE_API_KEY":
            return []
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': BRAVE_API_KEY
            }
            
            params = {
                'q': f'{query} financial news stock market',
                'count': count,
                'search_lang': 'en',
                'country': 'US',
                'safesearch': 'moderate',
                'freshness': 'pw'  # Past week
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for result in data.get('web', {}).get('results', []):
                # Filter for financial news domains
                financial_domains = [
                    'finance.yahoo.com', 'marketwatch.com', 'bloomberg.com',
                    'reuters.com', 'cnbc.com', 'fool.com', 'seekingalpha.com',
                    'benzinga.com', 'investorplace.com', 'thestreet.com'
                ]
                
                url = result.get('url', '')
                if any(domain in url for domain in financial_domains):
                    articles.append({
                        'title': result.get('title', ''),
                        'url': url,
                        'description': result.get('description', ''),
                        'source': 'Brave Search',
                        'published': 'Recent'  # Brave doesn't always provide dates
                    })
            
            return articles
            
        except Exception as e:
            print(f"❌ Brave Search API error: {e}")
            return []
    
    def search_serpapi(self, query: str, count: int = 10) -> List[Dict]:
        """
        Use SerpAPI for Google News results
        """
        if SERPAPI_KEY == "YOUR_SERPAPI_KEY":
            return []
        
        try:
            url = "https://serpapi.com/search"
            params = {
                'engine': 'google_news',
                'q': f'{query} stock financial news',
                'api_key': SERPAPI_KEY,
                'num': count,
                'hl': 'en',
                'gl': 'us'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for result in data.get('news_results', []):
                articles.append({
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'description': result.get('snippet', ''),
                    'source': result.get('source', 'Google News'),
                    'published': result.get('date', 'Recent')
                })
            
            return articles
            
        except Exception as e:
            print(f"❌ SerpAPI error: {e}")
            return []
    
    def search_bing_news_api(self, query: str, count: int = 10) -> List[Dict]:
        """
        Use Bing News API (requires Azure subscription)
        """
        # Note: Bing requires Azure subscription, so this is a placeholder
        # You can implement this if you have Azure credits
        return []
    
    def get_comprehensive_links(self, query: str, max_articles: int = 15) -> List[Dict]:
        """
        Get links from multiple search APIs
        """
        print(f"🔍 Searching for '{query}' across multiple search engines...")
        all_articles = []
        
        # Try Brave Search first (best for direct URLs)
        print("🔍 Searching Brave API...")
        brave_results = self.search_brave_api(query, max_articles//2)
        if brave_results:
            all_articles.extend(brave_results)
            print(f"   ✅ Found {len(brave_results)} articles from Brave")
        
        # Try SerpAPI for Google News
        if len(all_articles) < max_articles:
            print("🔍 Searching Google News via SerpAPI...")
            serp_results = self.search_serpapi(query, max_articles - len(all_articles))
            if serp_results:
                all_articles.extend(serp_results)
                print(f"   ✅ Found {len(serp_results)} articles from SerpAPI")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles[:max_articles]

def comprehensive_financial_news_search(query: str, max_articles: int = 10, extract_full_content: bool = False) -> str:
    """
    Main function that combines enhanced link fetching with LLM-based content extraction
    """
    link_fetcher = EnhancedLinkFetcher()
    scraper = EnhancedNewsScraper()
    
    # Get articles from multiple search engines
    articles = link_fetcher.get_comprehensive_links(query, max_articles)
    
    if not articles:
        return f"⚠️ No articles found for '{query}'. Please check your internet connection and API keys."
    
    results = []
    results.append(f"📊 Found {len(articles)} relevant financial articles")
    results.append("🤖 Using AI-powered content extraction")
    results.append("=" * 80)
    
    for i, article in enumerate(articles, 1):
        article_info = f"""📰 Article {i}:
- Title: {article['title']}
- Source: {article['source']}
- Published: {article['published']}
- URL: {article['url']}"""
        
        if extract_full_content:
            print(f"  🤖 AI-extracting content from article {i}/{len(articles)}...")
            extracted_content = scraper.extract_with_multiple_methods(article['url'])
            article_info += f"\n- 📄 AI-Extracted Content:\n  {extracted_content}"
            time.sleep(2)  # Be respectful to APIs
        elif article.get('description'):
            article_info += f"\n- 📄 Description: {article['description']}"
        
        results.append(article_info)
    
    return "\n\n".join(results)

if __name__ == "__main__":
    print("🤖 AI-Powered Financial News Aggregator")
    print("🔍 Enhanced with LLM-based content extraction and advanced search APIs")
    print("=" * 80)
    print("📝 Setup for best results:")
    print("1. Brave Search API (Free): https://brave.com/search/api/")
    print("2. SerpAPI (Free tier): https://serpapi.com/")  
    print("3. FireCrawl API (Free tier): https://firecrawl.dev/")
    print("4. Jina Reader works without API key! 🎉")
    print("=" * 80)
    
    company = input("\nEnter company name (default: NVIDIA): ") or "NVIDIA"
    
    try:
        max_articles = int(input("Number of articles (default: 10): ") or "10")
    except:
        max_articles = 10
    
    extract_choice = input("Use AI-powered full content extraction? (y/N): ").lower().strip()
    extract_content = extract_choice in ['y', 'yes']
    
    print(f"\n🚀 Searching and analyzing news for {company}...")
    print("=" * 80)
    
    results = comprehensive_financial_news_search(
        query=company,
        max_articles=max_articles, 
        extract_full_content=extract_content
    )
    
    print(results)
    
    if extract_content:
        print(f"\n✅ AI content extraction completed!")
        print("💡 The extracted content is optimized for LLM analysis and ready for your financial AI model.")
    else:
        print(f"\n💡 Tip: Enable AI extraction (y) for full article content optimized for language models.")