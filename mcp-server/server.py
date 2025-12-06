from fastmcp import FastMCP
import yfinance as yf
from newsapi import NewsApiClient
import os
from datetime import datetime

# Initialize the MCP Server
mcp = FastMCP("MarketMind-Finance")

# Initialize NewsAPI (We will set the key in the terminal later)
# If no key is found, it will just warn us, not crash immediately
news_api_key = os.getenv("NEWS_API_KEY")
newsapi = NewsApiClient(api_key=news_api_key) if news_api_key else None

@mcp.tool()
def get_stock_price(ticker: str, toolCallId: str = None) -> str:
    """
    Get the current stock price and basic info for a given US ticker symbol (e.g. AAPL, MSFT).
    Returns a formatted string with price and 50-day average.
    """

    # ✅ Handle MCP sending dict instead of string
    if isinstance(ticker, dict):
        ticker = (
            ticker.get("ticker")
            or ticker.get("TICKER")
            or next(iter(ticker.values()), None)
        )

    if not ticker:
        return "Error: No ticker provided."

    ticker = str(ticker).upper().strip()
    print(f"Fetching price for {ticker}...")

    try:
        stock = yf.Ticker(ticker)

        # ✅ More robust than fast_info alone (avoids currentTradingPeriod crash)
        hist = stock.history(period="1d")
        if hist.empty:
            return f"No price data found for {ticker}."

        price = float(hist["Close"].iloc[-1])

        try:
            currency = stock.fast_info.get("currency", "USD")
        except Exception:
            currency = "USD"

        try:
            fifty_day = stock.info.get("fiftyDayAverage", "N/A")
        except Exception:
            fifty_day = "N/A"

        return (
            f"Ticker: {ticker}\n"
            f"Current Price: {price:.2f} {currency}\n"
            f"50-Day Avg: {fifty_day}"
        )

    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"

@mcp.tool()
def get_market_news(query: str, toolCallId: str = None, ticker: str = None) -> str:
    """
    Get the top 3 recent news headlines for a company or topic.
    """
    if not newsapi:
        return "Error: NEWS_API_KEY not set in environment variables."
    
    print(f"Fetching news for {query}...")
    try:
        top_headlines = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            page_size=3
        )
        
        if not top_headlines['articles']:
            return f"No news found for {query}."
            
        result = f"--- News for {query} ---\n"
        for article in top_headlines['articles']:
            result += f"- {article['title']} ({article['source']['name']})\n"
            
        return result
    except Exception as e:
        return f"Error fetching news: {str(e)}"

if __name__ == "__main__":
    # We run on port 8000
    mcp.run(transport="sse", port=8000)