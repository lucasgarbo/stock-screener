import yfinance as yf
import pandas as pd
import numpy as np
import ta
import requests
import time
import os

# ==========================================================
# 1. CONFIGURAZIONE TELEGRAM
# ==========================================================
def send_telegram_report(message):
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    if not TOKEN or not CHAT_ID:
        print("Errore: Variabili TELEGRAM_TOKEN o TELEGRAM_CHAT_ID non trovate.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    if len(message) > 4000:
        message = message[:4000] + "\n... (Tagliato)"
        
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print("🚀 Report inviato a Telegram!")
        else:
            print(f"❌ Errore API Telegram: {r.text}")
    except Exception as e:
        print(f"❌ Errore connessione Telegram: {e}")

# ==========================================================
# 2. LOGICA SEMAFORO MACRO (VIX)
# ==========================================================
def get_macro_sentiment():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        if vix > 25: return f"PAURA (VIX: {vix:.2f}) - Ottima finestra"
        if vix < 15: return f"EUFORIA (VIX: {vix:.2f}) - Prudenza"
        return f"NEUTRALE (VIX: {vix:.2f})"
    except:
        return "NON DISPONIBILE"

# ==========================================================
# 3. LISTA TICKER
# ==========================================================
tickers = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "BRK-B", "LLY",
    "V", "JPM", "UNH", "XOM", "MA", "HD", "PG", "COST", "MRK", "ABBV",
    "CRM", "ADBE", "PEP", "KO", "WMT", "AMD", "NFLX", "INTC", "ORCL", "CSCO",
    "TMO", "ACN", "MCD", "LIN", "ABT", "DHR", "VZ", "CMCSA", "NKE", "TXN",
    "PM", "NEE", "RTX", "HON", "UPS", "LOW", "IBM", "INTU", "AMAT", "GS",
    "CAT", "DE", "BLK", "AXP", "SPGI", "MDT", "ELV", "ISRG", "BKNG", "CI",
    "CVX", "COP", "ADP", "CB", "PLD", "MMC", "MO", "GILD", "GE", "SYK",
    "PNC", "BDX", "C", "SO", "DUK", "ZTS", "ITW", "ICE", "USB", "FIS",
    "EQIX", "LRCX", "TGT", "REGN", "APD", "ETN", "PH", "EMR", "AON", "MCO",
    "FDX", "WM", "HCA", "PSA", "CCI", "O", "EQR", "ANET", "FTNT", "WDAY",
    "SQ", "PYPL", "DOCU", "TWLO", "HUBS", "FISV", "GPN", "PAYX", "CDW", "ROP",
    "KEYS", "TER", "HPQ", "SLB", "HAL", "EOG", "MPC", "PSX", "VLO", "KMI",
    "OKE", "TRP", "SU", "NEM", "FCX", "ALB", "LYB", "DOW", "CTRA", "DVN",
    "APA", "OXY", "SBUX", "CMG", "YUM", "MAR", "HLT", "EBAY", "ETSY", "ULTA",
    "ROST", "DG", "DLTR", "KR", "KHC", "HSY", "EL", "STZ", "CLX", "ADM",
    "TSN", "BIIB", "ILMN", "BAX", "MRNA", "DXCM", "IDXX", "WST", "CAH", "CNC",
    "IQV", "LH", "RMD", "EW", "HOLX", "UHS", "VTRS", "PODD", "VRTX", "SNPS",
    "CDNS", "PANW", "CRWD", "DDOG", "MDB", "NET", "ZS", "TEAM", "NOW", "SNOW",
    "SHOP", "PLTR", "OKTA", "ON", "MRVL", "NXPI", "ADI", "MCHP", "QCOM", "ASML",
    "TSM", "SMCI", "ARM", "MU", "KLAC", "TEL", "APH", "CSX", "NSC", "UNP",
    "CP", "CNI", "DAL", "AAL", "UAL", "LUV", "RCL", "CCL", "NCLH", "BK",
    "TFC", "SCHW", "MS", "MET", "PRU", "AIG", "TRV", "ALL", "PGR", "AJG",
    "CBRE", "WY", "LEN", "DHI", "PHM", "NVR", "TROW", "BEN", "IVZ", "STT",
    "NTRS", "CME", "MGM", "WYNN", "LVS", "VICI", "ORLY", "AZO", "TSCO", "FAST",
    "GPC", "ODFL", "CHRW", "JBHT", "URI", "SWK", "ROK", "IR", "TT", "CARR",
    "OTIS", "GD", "LMT", "NOC", "BA", "TXT", "EXC", "AEP", "XEL", "SRE",
    "ED", "WEC", "PEG", "ES", "EIX", "PCG", "FE", "CMS", "DTE", "ATO",
    "NI", "PNW", "LNT", "EVRG", "NRG", "AES", "ADSK", "ANSS", "CRL", "INCY",
    "MTD", "TECH", "WAT", "PKI", "CTAS", "PAYC", "ZBRA", "DPZ", "POOL", "RSG",
    "WMB", "EPD", "MRO", "PXD", "FANG", "AFL", "HIG", "DFS", "SYF", "COF",
    "FITB", "RF", "HBAN", "CFG", "KEY", "MTB", "ZION", "CINF", "WRB", "L",
    "GL", "BRO", "MKTX", "EXPE", "ABNB", "UBER", "LYFT", "DASH", "SPOT", "TTD",
    "ROKU", "BIDU", "JD", "BABA", "PDD", "SE", "MELI", "CPNG", "SQM", "RIO",
    "BHP", "VALE"
]

results = []
macro_status = get_macro_sentiment()
print(f"--- ANALISI AVVIATA: {macro_status} ---")

# ==========================================================
# 4. LOOP DI ANALISI
# ==========================================================
for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")

        if len(hist) < 200: continue

        close = hist["Close"]
        roe = info.get("returnOnEquity", 0)
        debt_equity = info.get("debtToEquity", 999)
        margin = info.get("profitMargins", 0)

        f_score = 0
        if roe and roe > 0.20: f_score += 15
        if debt_equity and debt_equity < 80: f_score += 10
        if margin and margin > 0.20: f_score += 10

        current_price = info.get("currentPrice", 0)
        fair_value = info.get("targetMeanPrice", 0)
        v_score = 0
        discount = 0

        if current_price and fair_value:
            discount = (fair_value - current_price) / current_price
            if discount > 0.25: v_score += 25
            elif discount > 0.15: v_score += 15
            elif discount > 0.05: v_score += 5

        sma200 = close.rolling(200).mean().iloc[-1]
        trend_score = 15 if (not np.isnan(sma200) and close.iloc[-1] > sma200) else 0

        ma20 = close.rolling(20).mean()
        dpo = close - ma20.shift(11)
        timing_score = 0
        if len(dpo.dropna()) > 2:
            if dpo.iloc[-1] > dpo.iloc[-2] and dpo.iloc[-2] < 0: timing_score += 15
            elif dpo.iloc[-1] > 0: timing_score += 5

        vol_score = 5 if hist["Volume"].iloc[-1] > hist["Volume"].mean() * 1.5 else 0
        
        total_score = f_score + v_score + trend_score + timing_score + vol_score

        if total_score >= 80:
            results.append({
                "Ticker": ticker,
                "Score": total_score,
                "Sconto": f"{round(discount * 100, 1)}%"
            })
            print(f"Trovato BUY: {ticker} (Score: {total_score})")

    except Exception as e:
        continue

# ==========================================================
# 5. INVIO REPORT
# ==========================================================
if results:
    df_final = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    report_text = f"📊 REPORT PROTOCOLLO MAESTRO\nMacro: {macro_status}\n\n"
    report_text += df_final.to_string(index=False)
    send_telegram_report(report_text)
else:
    print("Nessun segnale BUY ≥ 80 trovato.")
