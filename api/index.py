from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import yfinance as yf
from datetime import datetime

app = FastAPI(title="Live Global Oil Prices")

# Only the benchmarks that actually exist on Yahoo Finance
BENCHMARKS = {
    "WTI Crude": "CL=F",
    "Brent Crude": "BZ=F",
    "Natural Gas": "NG=F",
    "Gasoline": "RB=F",
    "Heating Oil": "HO=F",
}

def fetch_all_prices():
    data = []
    for name, symbol in BENCHMARKS.items():
        try:
            t = yf.Ticker(symbol)
            info = t.info
            fast = t.fast_info
            
            last = fast.get("lastPrice") or info.get("regularMarketPrice")
            prev = info.get("regularMarketPreviousClose")
            change = round(last - prev, 2) if last and prev else 0
            pct = round((change / prev * 100), 2) if prev else 0
            
            data.append({
                "name": name,
                "last": round(last, 2) if last else "—",
                "change": change,
                "pct": pct,
                "symbol": symbol
            })
        except:
            pass  # skip if any ticker fails
    return data

@app.get("/")
def dashboard():
    prices = fetch_all_prices()
    rows = ""
    for p in prices:
        color = "lime" if p["change"] >= 0 else "red"
        rows += f"""
        <tr>
            <td>{p['name']}</td>
            <td><strong>${p['last']}</strong></td>
            <td style="color:{color}">{p['change']:+.2f}</td>
            <td style="color:{color}">{p['pct']:+.2f}%</td>
            <td>Real-time / 10-15 min delay (Yahoo)</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌍 Live Oil Prices Worldwide</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ font-family: system-ui; background: #0f172a; color: white; padding: 40px; }}
            table {{ width: 100%; max-width: 900px; margin: 0 auto; border-collapse: collapse; background: #1e2937; }}
            th, td {{ padding: 14px; text-align: left; border-bottom: 1px solid #334155; }}
            th {{ background: #22c55e; color: black; }}
            tr:hover {{ background: #334155; }}
            .positive {{ color: lime; }}
            .negative {{ color: red; }}
            h1 {{ text-align: center; color: #22c55e; }}
        </style>
    </head>
    <body>
        <h1>🌍 Live Oil Prices from Around the World</h1>
        <p style="text-align:center;color:#94a3b8;">Auto-refreshes every 30 seconds • Data from Yahoo Finance via yfinance</p>
        <table>
            <tr>
                <th>Benchmark</th>
                <th>Last</th>
                <th>Change</th>
                <th>% Change</th>
                <th>Last Updated</th>
            </tr>
            {rows}
        </table>
        <p style="text-align:center;margin-top:30px;">
            <a href="/oil-prices" style="color:#60a5fa">View raw JSON API →</a> | 
            Full screenshot table not possible with free yfinance (missing Murban/Dubai/Urals etc.)
        </p>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.get("/oil-prices")
def json_api():
    prices = fetch_all_prices()
    return {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "data": prices,
        "source": "Yahoo Finance via yfinance",
        "note": "Only major benchmarks available. Obscure ones (Murban, Urals...) require paid APIs."
    }
