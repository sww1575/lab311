# stock_api.py
import yfinance as yf

def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "name": info.get("shortName"),
            "price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps")
        }
    except Exception as e:
        return {"error": str(e)}