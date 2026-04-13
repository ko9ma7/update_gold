import yfinance as yf
import pandas as pd
import json
from datetime import datetime

try:
    print("⏳ Yahoo Finance에서 금시세(USD) 및 환율(KRW) 과거 데이터를 가져옵니다...")
    
    # 국제 금 선물(GC=F) 및 달러/원 환율(USDKRW=X) 데이터 로드 (재작년 1월부터).
    gold = yf.Ticker("GC=F")
    usdkrw = yf.Ticker("USDKRW=X")

    df_gold = gold.history(start="2022-01-01")['Close'].rename('Gold_USD')
    df_krw = usdkrw.history(start="2022-01-01")['Close'].rename('USD_KRW')

    # 두 데이터를 날짜 기준으로 병합
    df = pd.concat([df_gold, df_krw], axis=1).dropna()

    # 1g당 원화 가격 계산 (1 트로이온스 = 31.1034768g)
    df['KRW_per_Gram'] = (df['Gold_USD'] * df['USD_KRW']) / 31.1034768

    # 날짜별 딕셔너리로 변환
    history_dict = {}
    for index, row in df.iterrows():
        date_str = index.strftime('%Y-%m-%d')
        history_dict[date_str] = round(row['KRW_per_Gram'], 2)

    # 가장 최근(오늘) 데이터 추출
    latest_date = df.index[-1].strftime('%Y-%m-%d')
    latest_price = round(df['KRW_per_Gram'].iloc[-1], 2)

    output = {
        "status": "success",
        "latest_date": latest_date,
        "pgc": latest_price,
        "history": history_dict, # 재작년부터의 모든 일자별 데이터가 여기에 담깁니다!
        "source": "yfinance_github_bot"
    }

    with open("update.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ 업데이트 성공! {latest_date} 기준 최신 단가: 1g당 {latest_price}원")
    print(f"✅ 누적된 과거 데이터 일수: 총 {len(history_dict)}일")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
