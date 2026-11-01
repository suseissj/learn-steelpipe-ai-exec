"""교재 그림 두 장을 SVG로 만든다 (제작 기록용).

실행: python3 -I forge/make_figures.py <패키지 폴더>
- 그림 1: 철관 밸류체인 지도 (수치 없음)
- 그림 2: 열연 제조원가 추정과 유통가 — 숫자는 forge/research/facts.csv 의 F12·F09·F11 에서만 읽는다
"""
import csv, re, sys
from pathlib import Path

pkg = Path(sys.argv[1])
out = pkg / "textbook" / "fig"
out.mkdir(parents=True, exist_ok=True)
FONT = ("<style>@import url('https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css');"
        "text{font-family:'Pretendard Variable',Pretendard,'Malgun Gothic',sans-serif}</style>")
NAVY, ORANGE, INK, MUTED, LINE, SOFT = "#14284b", "#e8772e", "#1d2433", "#5b6475", "#d5dbe5", "#f5f7fa"

# ── 그림 1. 밸류체인 지도 ─────────────────────────────────────
steps = [
    ("코일 투입", "열연코일을 풀어 편다", "규격·재질 성적서", "소재 편차 ↔ 불량 관계"),
    ("조관(성형)", "롤로 둥글게 만다", "롤 회전·전류·진동", "롤·베어링 예지보전"),
    ("ERW 용접", "이음매를 전류로 붙인다", "용접 전류·전압·속도", "이상 조건 경보"),
    ("비파괴검사", "용접부를 검사한다", "검사 신호·판정 결과", "판정 보조·불량 분류"),
    ("절단·출하", "길이대로 잘라 내보낸다", "생산 본수·로트 기록", "로트별 품질 추적"),
]
W, H, bw, gap, x0 = 1200, 560, 204, 30, 30
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">', FONT,
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     f'<text x="{x0}" y="44" font-size="26" font-weight="700" fill="{NAVY}">철관 밸류체인 지도 — 공정별 데이터와 AI 적용 지점</text>',
     f'<text x="{x0}" y="74" font-size="16" fill="{MUTED}">위: 공정 · 가운데: 쌓이는 데이터 · 아래: AI가 할 수 있는 일 (주황 = 이 강의 1순위 후보 영역)</text>']
for i, (name, what, data, ai) in enumerate(steps):
    x = x0 + i * (bw + gap)
    hot = i == 1
    s.append(f'<rect x="{x}" y="100" width="{bw}" height="110" rx="10" fill="{NAVY}"/>')
    s.append(f'<text x="{x + bw / 2}" y="148" font-size="22" font-weight="700" fill="#fff" text-anchor="middle">{name}</text>')
    s.append(f'<text x="{x + bw / 2}" y="180" font-size="15" fill="#d9e0ec" text-anchor="middle">{what}</text>')
    if i < len(steps) - 1:
        ax = x + bw + 4
        s.append(f'<path d="M{ax} 155 L{ax + gap - 10} 155" stroke="{NAVY}" stroke-width="3"/>'
                 f'<path d="M{ax + gap - 10} 148 L{ax + gap - 2} 155 L{ax + gap - 10} 162 Z" fill="{NAVY}"/>')
    s.append(f'<rect x="{x}" y="232" width="{bw}" height="96" rx="10" fill="{SOFT}" stroke="{LINE}"/>')
    s.append(f'<text x="{x + bw / 2}" y="264" font-size="14" fill="{MUTED}" text-anchor="middle">쌓이는 데이터</text>')
    s.append(f'<text x="{x + bw / 2}" y="298" font-size="17" font-weight="600" fill="{INK}" text-anchor="middle">{data}</text>')
    s.append(f'<path d="M{x + bw / 2} 332 L{x + bw / 2} 352" stroke="{MUTED}" stroke-width="2"/>')
    fill, stroke, tc = ("#fdf1e8", ORANGE, ORANGE) if hot else ("#ffffff", NAVY, NAVY)
    s.append(f'<rect x="{x}" y="356" width="{bw}" height="96" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    s.append(f'<text x="{x + bw / 2}" y="388" font-size="14" fill="{MUTED}" text-anchor="middle">AI 적용</text>')
    s.append(f'<text x="{x + bw / 2}" y="422" font-size="17" font-weight="700" fill="{tc}" text-anchor="middle">{ai}</text>')
s.append(f'<rect x="{x0}" y="478" width="{W - 2 * x0}" height="56" rx="10" fill="{SOFT}"/>')
s.append(f'<text x="{x0 + 20}" y="512" font-size="17" fill="{INK}">경영 AI(2장)는 이 흐름 바깥에서 붙는다 — 열연코일 구매·판가·수주 데이터로 마진 시나리오를 본다.</text>')
s.append("</svg>")
(out / "fig1-valuechain.svg").write_text("\n".join(s), encoding="utf-8")

# ── 그림 2. facts.csv 숫자로 그린 막대 차트 ─────────────────────
facts = {r["번호"]: r for r in csv.DictReader(open(pkg / "forge/research/facts.csv", encoding="utf-8-sig"))}


def man_won(text):
    """'79만 9,000원' / '90만원' 형식을 만원 단위 숫자로"""
    m = re.search(r"(\d+)만\s?([\d,]+)?", text)
    return int(m.group(1)) + (int(m.group(2).replace(",", "")) / 10000 if m.group(2) else 0)


bars = [("2026년 4월\n제조원가(추정)", man_won(facts["F12"]["값(원문)"]), "F12 · S8", MUTED),
        ("2026년 4월 첫 주\n열연 유통가", man_won(facts["F09"]["값(원문)"]), "F09 · S8", NAVY),
        ("2026년 5월 중순\n열연 유통가", man_won(facts["F11"]["값(원문)"]), "F11 · S9", ORANGE)]
W, H, left, base, top = 900, 560, 110, 440, 110
scale = (base - top) / 100                    # 0~100만원
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">', FONT,
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     f'<text x="40" y="46" font-size="26" font-weight="700" fill="{NAVY}">국내 열연 — 제조원가 추정과 유통가 (만원/톤)</text>',
     f'<text x="40" y="76" font-size="16" fill="{MUTED}">출처: 하나증권 「철강금속 Weekly」 2026.04.06 [S8] · 2026.05.18 [S9]. 제조원가는 추정치.</text>']
for v in range(0, 101, 20):
    y = base - v * scale
    s.append(f'<line x1="{left}" y1="{y}" x2="{W - 40}" y2="{y}" stroke="{LINE}"/>')
    s.append(f'<text x="{left - 12}" y="{y + 5}" font-size="14" fill="{MUTED}" text-anchor="end">{v}</text>')
slot = (W - 40 - left) / len(bars)
for i, (label, v, src, color) in enumerate(bars):
    cx = left + slot * (i + 0.5)
    h = v * scale
    s.append(f'<rect x="{cx - 70}" y="{base - h}" width="140" height="{h}" rx="4" fill="{color}"/>')
    s.append(f'<text x="{cx}" y="{base - h - 12}" font-size="22" font-weight="700" fill="{INK}" text-anchor="middle">{v:g}</text>')
    for j, line in enumerate(label.split("\n")):
        s.append(f'<text x="{cx}" y="{base + 28 + j * 22}" font-size="16" fill="{INK}" text-anchor="middle">{line}</text>')
    s.append(f'<text x="{cx}" y="{base + 78}" font-size="13" fill="{MUTED}" text-anchor="middle">{src}</text>')
s.append("</svg>")
(out / "fig2-hrc-price.svg").write_text("\n".join(s), encoding="utf-8")
print("ok", [b[1] for b in bars])

# ── 덱용 그림 1 (1600×640 와이드, 본문 30px 이상 — report-navy-deck 16pt 규칙) ──
cols = [("코일 투입", ["규격·재질", "성적서"], ["소재 편차와", "불량 관계"]),
        ("조관(성형)", ["롤 회전·전류", "진동"], ["롤·베어링", "예지보전"]),
        ("ERW 용접", ["용접 전류", "전압·속도"], ["이상 조건", "경보"]),
        ("비파괴검사", ["검사 신호", "판정 결과"], ["판정 보조", "불량 분류"]),
        ("절단·출하", ["생산 본수", "로트 기록"], ["로트별", "품질 추적"])]
W, H, bw, gap, x0 = 1600, 640, 284, 30, 20
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">', FONT,
     f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
for i, (name, data, ai) in enumerate(cols):
    x, cx, hot = x0 + i * (bw + gap), x0 + i * (bw + gap) + bw / 2, i == 1
    s.append(f'<rect x="{x}" y="20" width="{bw}" height="130" rx="12" fill="{NAVY}"/>')
    s.append(f'<text x="{cx}" y="98" font-size="36" font-weight="700" fill="#fff" text-anchor="middle">{name}</text>')
    if i < len(cols) - 1:
        ax = x + bw + 3
        s.append(f'<path d="M{ax} 85 L{ax + gap - 9} 85" stroke="{NAVY}" stroke-width="4"/>'
                 f'<path d="M{ax + gap - 11} 76 L{ax + gap - 2} 85 L{ax + gap - 11} 94 Z" fill="{NAVY}"/>')
    s.append(f'<rect x="{x}" y="176" width="{bw}" height="190" rx="12" fill="{SOFT}" stroke="{LINE}" stroke-width="2"/>')
    for j, t in enumerate(data):
        s.append(f'<text x="{cx}" y="{256 + j * 46}" font-size="32" font-weight="600" fill="{INK}" text-anchor="middle">{t}</text>')
    s.append(f'<path d="M{cx} 372 L{cx} 404" stroke="{MUTED}" stroke-width="3"/>')
    fill, stroke, tc = ("#fdf1e8", ORANGE, ORANGE) if hot else ("#ffffff", NAVY, NAVY)
    s.append(f'<rect x="{x}" y="410" width="{bw}" height="210" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="4"/>')
    for j, t in enumerate(ai):
        s.append(f'<text x="{cx}" y="{500 + j * 48}" font-size="34" font-weight="700" fill="{tc}" text-anchor="middle">{t}</text>')
s.append("</svg>")
(out / "fig1-valuechain-deck.svg").write_text("\n".join(s), encoding="utf-8")
