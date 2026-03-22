from fastapi import FastAPI
import yfinance as yf
from datetime import datetime

app = FastAPI(
    title="Live Global Oil Prices",
    description="Free API using yfinance - WTI & Brent updated live"
)

@app.get("/")
def home():
    return {
        "message": "✅ Live Oil Prices API is running!",
        "endpoints": ["/oil-prices"],
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/oil-prices")
def get_oil_prices():
    try:
        # Fetch latest futures prices
        wti = yf.Ticker("CL=F").fast_info.get("lastPrice")
        brent = yf.Ticker("BZ=F").fast_info.get("lastPrice")

        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "wti_crude_usd_per_barrel": round(wti, 2) if wti else None,
            "brent_crude_usd_per_barrel": round(brent, 2) if brent else None,
            "source": "Yahoo Finance (10-15 min delay outside trading hours)",
            "note": "Works 24/7 - even on weekends (shows last available price)"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
