import yfinance as yf
import pandas as pd
import numpy as np
import ta
import requests
import time
import os

# ==========================================================
# 1. CONFIGURAZIONE TELEGRAM (Corretta negli spazi)
# ==========================================================
def send_telegram_report(message):
    # Tutto questo blocco deve essere rientrato di 4 spazi
    TOKEN = os.environ["TELEGRAM_TOKEN"]
    CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Se il messaggio è troppo lungo, Telegram lo blocca. Lo tagliamo se serve.
    if len(message) > 4000:
        message = message[:4000] + "\n... (Tagliato per lunghezza)"
        
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
        print("🚀 Report inviato a Telegram!")
    except Exception as e:
        print(f"❌ Errore invio Telegram: {e}")


# ==========================================================
# 2. LOGICA SEMAFORO MACRO (VIX)
# ==========================================================
def get_macro_sentiment():
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        if vix > 25: return f"PAURA (VIX: {vix:.2f}) - Ottima finestra di ingresso"
        if vix < 15: return f"EUFORIA (VIX: {vix:.2f}) - Meglio essere prudenti"
        return f"NEUTRALE (VIX: {vix:.2f})"
    except:
        return "NON DISPONIBILE"

# ==========================================================
# 3. LISTA TICKER UNIVOCI
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
print(f"--- ANALISI AVVIATA ---")
print(f"Contesto Macro: {macro_status}\n")

# ==========================================================
# 4. LOOP DI ANALISI PROTOCOLLO MAESTRO
# ==========================================================

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")

        if len(hist) < 200:
            continue

        close = hist["Close"]

        # [span_0](start_span)1️⃣ FONDAMENTALI (max 35)[span_0](end_span)
        roe = info.get("returnOnEquity", 0)
        debt_equity = info.get("debtToEquity", 999)
        margin = info.get("profitMargins", 0)

        f_score = 0
        [span_1](start_span)if roe and roe > 0.20: f_score += 15 # Regola ROE > 15%[span_1](end_span)
        [span_2](start_span)if debt_equity and debt_equity < 80: f_score += 10 # Regola Debito < 1[span_2](end_span)
        [span_3](start_span)if margin and margin > 0.20: f_score += 10 # Regola Profit Margin[span_3](end_span)

        # [span_4](start_span)2️⃣ VALUTAZIONE (max 25)[span_4](end_span)
        current_price = info.get("currentPrice", None)
        fair_value = info.get("targetMeanPrice", None)

        v_score = 0
        discount = 0
        if current_price and fair_value:
            discount = (fair_value - current_price) / current_price
            if discount > 0.25: v_score += 25
            elif discount > 0.15: v_score += 15
            elif discount > 0.05: v_score += 5

        # 3️⃣ TREND PRIMARIO (max 15)
        sma200 = close.rolling(200).mean()
        trend_score = 0
        if not pd.isna(sma200.iloc[-1]):
            if close.iloc[-1] > sma200.iloc[-1]:
                trend_score += 15

        # [span_5](start_span)[span_6](start_span)4️⃣ TIMING DPO (max 15)[span_5](end_span)[span_6](end_span)
        ma20 = close.rolling(20).mean()
        dpo = close - ma20.shift(11)
        timing_score = 0
        if len(dpo.dropna()) > 2:
            [span_7](start_span)if dpo.iloc[-1] > dpo.iloc[-2] and dpo.iloc[-2] < 0: # Regola DPO risale[span_7](end_span)
                timing_score += 15
            elif dpo.iloc[-1] > 0:
                timing_score += 5

        # [span_8](start_span)5️⃣ VOLUME (max 5)[span_8](end_span)
        volume_score = 0
        if hist["Volume"].iloc[-1] > hist["Volume"].mean() * 1.5:
            volume_score += 5

        # [span_9](start_span)[span_10](start_span)6️⃣ MACRO (max 5)[span_9](end_span)[span_10](end_span)
        macro_score = 0
        try:
            vix_value = yf.Ticker("^VIX").history(period="1d")["Close"].iloc[-1]
            [span_11](start_span)if vix_value > 25: # Corrisponde a "Fear"[span_11](end_span)
                macro_score += 5
        except:
            pass

        total_score = f_score + v_score + trend_score + timing_score + volume_score + macro_score

        if total_score >= 60:
            verdict = "🔥 BUY" if total_score >= 80 else "👀 ATTENDI"
            results.append({
                "Ticker": ticker,
                "Score": total_score,
                "Verdetto": verdict,
                "Sconto": round(discount * 100, 1)
            })
            print(f"{ticker}: {total_score} ({verdict})")

    except Exception as e:
        continue

# ==========================================================
# 5. GENERAZIONE REPORT E INVIO
# ==========================================================
df_final = pd.DataFrame(results)

if not df_final.empty:
    df_final = df_final.sort_values(by="Score", ascending=False)
    buy_df = df_final[df_final["Score"] >= 80]

    if not buy_df.empty:
        report_text = f"📊 REPORT PROTOCOLLO DA MAESTRO\n"
        report_text += f"Mood Mercato: {macro_status}\n"
        report_text += "--------------------------------\n"
        report_text += buy_df.to_string(index=False)
        print("\n" + report_text)
        send_telegram_report(report_text)
    else:
        print("Nessun BUY ≥ 80 questa settimana. Nessuna notifica inviata.")
else:
    print("Nessun titolo analizzato correttamente.")
