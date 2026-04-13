import yfinance as yf
import pandas as pd
import json

try:
    print("⏳ Yahoo Finance에서 금시세(USD) 및 환율(KRW) 과거 데이터를 가져옵니다...")
    
    gold = yf.Ticker("GC=F")
    usdkrw = yf.Ticker("USDKRW=X")

    df_gold = gold.history(start="2022-01-01")['Close'].rename('Gold_USD')
    df_krw = usdkrw.history(start="2022-01-01")['Close'].rename('USD_KRW')

    # [핵심 수정] 타임존(시간대) 정보 제거 및 순수 날짜(Date) 기준으로 정규화
    df_gold.index = df_gold.index.tz_localize(None).normalize()
    df_krw.index = df_krw.index.tz_localize(None).normalize()

    # 데이터 병합: 휴장일이 달라 빈 값이 생기면 이전 날짜 값으로 채움(ffill)
    df = pd.concat([df_gold, df_krw], axis=1).ffill().dropna()

    if df.empty:
        raise ValueError("병합된 데이터가 없습니다. API를 확인하세요.")

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
        "history": history_dict,
        "source": "yfinance_github_bot"
    }

    with open("update.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ 업데이트 성공! {latest_date} 기준 최신 단가: 1g당 {latest_price}원")
    print(f"✅ 누적된 과거 데이터 일수: 총 {len(history_dict)}일")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
