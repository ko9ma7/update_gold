# update_gold.py
import urllib.request
import json
import os

# 빠르고 차단 없는 글로벌 금시세 API (1트로이온스 기준)
url = "https://open.er-api.com/v6/latest/XAU"

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        # XAU(금 1트로이온스) -> KRW(원화) 환산
        krw_per_ounce = data['rates']['KRW']
        krw_per_gram = round(krw_per_ounce / 31.1034768, 2)

        # index.html이 읽기 편하도록 JSON 형태로 저장
        output = {
            "status": "success",
            "pgc": krw_per_gram,
            "source": "github_actions_bot"
        }
        
        with open("update.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 금시세 업데이트 성공: 1g당 {krw_per_gram}원")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
