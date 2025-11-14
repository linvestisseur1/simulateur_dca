import json
import yfinance as yf

def handler(request):
    # lire les paramètres
    query = request.get("query", {})
    ticker = query.get("ticker", "AAPL")
    montant = float(query.get("montant", 100))
    start = query.get("start", "2000-01-01")

    try:
        data = yf.download(ticker, start=start)
        if data.empty:
            return {
                "status": 400,
                "body": json.dumps({"error": "Ticker introuvable"})
            }

        close_prices = data["Close"]
        shares = 0
        invested = 0

        for price in close_prices:
            shares += montant / price
            invested += montant

        final_value = shares * close_prices.iloc[-1]

        return {
            "status": 200,
            "body": json.dumps({
                "ticker": ticker,
                "invested": invested,
                "value": final_value
            })
        }

    except Exception as e:
        return {
            "status": 500,
            "body": json.dumps({"error": str(e)})
        }
