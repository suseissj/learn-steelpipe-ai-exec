"""실습용 가상 데이터 3종을 만든다 (제작 기록용 — 수강생은 실행하지 않는다).

실행: python3 -I forge/make_lab_data.py <패키지 폴더>
결과: .claude/skills/learn-steelpipe-ai-exec/assets/lab/ 에 csv 3개
"""
import csv, random, sys
from datetime import date, timedelta
from pathlib import Path

pkg = Path(sys.argv[1])
lab = pkg / ".claude/skills/learn-steelpipe-ai-exec/assets/lab"
lab.mkdir(parents=True, exist_ok=True)
rng = random.Random(20261031)          # 같은 값이 다시 나오도록 시드 고정

# 1. 생산 로트 60건 — 17번 로트 한 번 튐(노이즈), 48번 로트부터 꾸준한 상승(추세)
items = ["구조관 Φ100", "배관용 강관 Φ150", "구조관 Φ200"]
rows, d = [], date(2026, 7, 1)
for i in range(1, 61):
    while d.weekday() >= 5:            # 주말 제외
        d += timedelta(days=1)
    qty = rng.randint(2000, 2600)
    if i == 17:
        vib, rate = 3.8, 0.0085        # 한 번 튄 값, 불량률은 평소 수준
    elif i == 47:
        vib, rate = 1.40, 0.0080
    elif i >= 48:
        k = i - 48                     # 0~12
        vib = round(1.30 + 0.11 * k, 2)          # 1.30 → 2.62
        rate = 0.0085 + 0.0006 * k               # 0.85% → 1.57%
    else:
        vib = round(rng.uniform(1.05, 1.40), 2)
        rate = rng.uniform(0.0065, 0.0095)
    rows.append([f"L{i:03d}", d.isoformat(), items[(i - 1) % 3], qty, round(qty * rate), vib])
    d += timedelta(days=1)
with open(lab / "production_lots.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["로트", "일자", "품목", "생산본수", "용접불량본수", "조관기진동(mm/s)"])
    w.writerows(rows)

# 2. 열연코일 가격과 품목별 판가·원가 (2025-10 ~ 2026-09, 12개월 × 3품목)
coil = [835, 842, 861, 880, 902, 918, 931, 924, 907, 889, 896, 912]   # 천원/톤
prod = {  # 품목: (판가 기준 천원/톤, 코일 소요 톤/톤, 가공비 천원/톤, 판매량 톤)
    "구조관": (1080, 1.06, 110, 9000),
    "배관용 강관": (1270, 1.07, 175, 6000),
    "유정용 강관": (1560, 1.08, 340, 3000),
}
with open(lab / "coil_price_margin.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["월", "품목", "판가(원/톤)", "열연코일가격(원/톤)", "코일소요(톤/톤)", "가공비(원/톤)", "판매량(톤)"])
    for m, c in enumerate(coil, start=1):
        for name, (p, use, proc, vol) in prod.items():
            price = p + round((c - 835) * 0.55)          # 판가는 코일가 상승의 일부만 따라간다
            ym = f"{2025 + (m + 8) // 12}-{(m + 8) % 12 + 1:02d}"
            w.writerow([ym, name, price * 1000, c * 1000, use, proc * 1000,
                        vol + rng.randint(-300, 300)])

# 3. AI 후보 과제 6개
cands = [
    ["조관기 예지보전", "제조", 6.0, 2.0, "상", "진동·전류 센서로 롤·베어링 이상을 미리 알림"],
    ["용접 비전검사", "제조", 9.0, 6.0, "중", "용접 비드 영상으로 불량 자동 판정"],
    ["생산계획 최적화", "제조", 8.0, 5.0, "중", "수주·설비 가동률로 품목 순서와 교체 시간 최적화"],
    ["열연코일 구매 시점 예측", "경영", 14.0, 4.0, "하", "코일가 흐름을 예측해 구매 시점과 물량 결정"],
    ["견적·수주 자동화", "경영", 2.2, 0.8, "상", "고객 문의에서 규격·수량을 뽑아 견적서 초안 작성"],
    ["월간 경영보고 자동화", "경영", 1.0, 0.4, "상", "ERP 숫자로 월간 보고서 초안 작성"],
]
with open(lab / "ai_candidates.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["과제", "영역", "연간기대효과(억원)", "초기투자(억원)", "데이터준비도", "설명"])
    w.writerows(cands)
print("ok", lab)
