import requests
from datetime import date, timedelta

API_KEY = "d37s5gpr01qskrehl3o0d37s5gpr01qskrehl3og"
symbol = "INFY"   # Infosys
today = date.today()
last_week = today - timedelta(days=7)

url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={last_week}&to={today}&token={API_KEY}"
resp = requests.get(url).json()

for article in resp[:5]:
    print(article["datetime"], article["headline"], article["url"])
