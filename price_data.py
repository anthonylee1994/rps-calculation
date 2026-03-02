import yfinance as yf
from datetime import datetime, timedelta

TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "JPM",
    "V", "UNH", "XOM", "LLY", "JNJ", "WMT", "MA", "PG", "HD", "AVGO",
    "CVX", "ABBV", "COST", "KO", "PEP", "ADBE", "CSCO", "TMO",
    "AMD", "INTC", "NFLX", "CRM", "MCD", "BAC", "QCOM", "AMGN",
    "HON", "IBM", "CAT", "GE", "SBUX", "RTX"
]

END_DATE   = datetime.today()
START_DATE = END_DATE - timedelta(days=400)

def get_close_prices():
    result = yf.download(
        TICKERS,
        start=START_DATE.strftime("%Y-%m-%d"),
        end=END_DATE.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False
    )["Close"]

    result = result.dropna(axis=1, thresh=int(len(result) * 0.9))

    return result
