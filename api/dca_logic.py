import yfinance as yf

def calcul_dca(ticker: str, montant: float, start_date: str):
    data = yf.download(ticker, start=start_date)

    if data.empty:
        return {"error": "Ticker introuvable"}

    total_shares = 0
    total_investi = 0

    for date, row in data.iterrows():
        price = row["Close"]
        if not price or price <= 0:
            continue
        shares = montant / price
        total_shares += shares
        total_investi += montant

    valeur_finale = float(total_shares * data["Close"].iloc[-1])

    return {
        "ticker": ticker,
        "invest_total": round(total_investi, 2),
        "valeur_portefeuille": round(valeur_finale, 2),
        "variation": round(valeur_finale - total_investi, 2),
    }
