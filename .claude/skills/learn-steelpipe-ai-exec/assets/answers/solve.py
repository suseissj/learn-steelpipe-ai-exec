"""정답 예시 — Block 1~3을 한 번에 풀어 out/*.md · index.html · expected.json 을 만든다.

실행 위치: data/ 폴더(production_lots.csv · coil_price_margin.csv · ai_candidates.csv)가 있는 작업 폴더
"""
import csv, json, statistics, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # 윈도우 콘솔에서도 한글·기호가 깨지지 않게


def read(name):
    return list(csv.DictReader(open(f"data/{name}", encoding="utf-8-sig")))


lots, coil_rows, cands = read("production_lots.csv"), read("coil_price_margin.csv"), read("ai_candidates.csv")
Path("out").mkdir(exist_ok=True)

# ── Block 1 제조 AI ─────────────────────────────────────────────
# 1. 불량률 — 로트별 불량률과 전체 평균(전체 불량 본수 ÷ 전체 생산 본수)
for r in lots:
    r["불량률"] = int(r["용접불량본수"]) / int(r["생산본수"])
avg_rate = sum(int(r["용접불량본수"]) for r in lots) / sum(int(r["생산본수"]) for r in lots)

# 2. 평상 범위 — 평균 ± 2표준편차 (Google Sheets STDEV와 같은 표본 표준편차)
vib = [float(r["조관기진동(mm/s)"]) for r in lots]
m, sd = statistics.mean(vib), statistics.stdev(vib)
lo, hi = m - 2 * sd, m + 2 * sd
anom = [i for i, v in enumerate(vib) if not lo <= v <= hi]

# 3. 노이즈 vs 추세 — 끝에서부터 거꾸로 "앞 로트보다 높다"가 이어지는 구간의 시작이 추세 시작점
start = len(vib) - 1
while start > 0 and vib[start - 1] < vib[start]:
    start -= 1
trend_anom = [i for i in anom if i >= start]
noise_anom = [i for i in anom if i < start]
trend_lot, trend_date = lots[start]["로트"], lots[start]["일자"]

# 4. 진동·불량률 동반 상승 — 추세 구간 평균 불량률 vs 그 이전
rate_before = statistics.mean(r["불량률"] for r in lots[:start])
rate_trend = statistics.mean(r["불량률"] for r in lots[start:])

pct = lambda x, d=2: f"{x * 100:.{d}f}%"
mfg_lines = [
    "# 제조 AI 판정 (실습용 가상 데이터)", "",
    f"- 전체 평균 불량률: {pct(avg_rate)} (전체 불량 본수 ÷ 전체 생산 본수)",
    f"- 진동 평상 범위: {lo:.2f} ~ {hi:.2f} mm/s (평균 {m:.2f}, 표준편차 {sd:.2f})",
    f"- 이상 후보: {len(anom)}개 — 노이즈 {len(noise_anom)}개, 추세 {len(trend_anom)}개", "",
    "| 로트 | 일자 | 진동(mm/s) | 불량률 | 판정 |", "|---|---|---|---|---|",
]
for i in anom:
    r = lots[i]
    mfg_lines.append(f"| {r['로트']} | {r['일자']} | {vib[i]} | {pct(r['불량률'])} | "
                     f"{'추세적 상승' if i in trend_anom else '노이즈 (한 번 튐)'} |")
mfg_lines += ["",
    f"- 정비 계획 시점: {trend_date} ({trend_lot}) — 이 로트부터 진동이 매 로트 올랐다. "
    f"평상 범위를 넘은 것은 {lots[trend_anom[0]]['일자']}부터라, 범위만 보면 열흘 넘게 늦는다.",
    f"- 같은 구간 평균 불량률: {pct(rate_trend)} (그 이전 {pct(rate_before)}) — 진동과 불량이 함께 올랐다.", "",
    f"**결론:** {lots[noise_anom[0]]['로트']}의 한 번 튐은 지켜보고, {trend_date}부터의 추세를 근거로 "
    "조관기 롤·베어링 점검을 다음 계획 정비에 넣는다."]
Path("out/manufacturing.md").write_text("\n".join(mfg_lines) + "\n", encoding="utf-8")

# ── Block 2 경영 AI ─────────────────────────────────────────────
months = sorted({r["월"] for r in coil_rows})
coil_by_m = {r["월"]: int(r["열연코일가격(원/톤)"]) for r in coil_rows}
c_max, c_min = max(coil_by_m.values()), min(coil_by_m.values())
coil_range = c_max / c_min - 1                                  # 변동 폭 = 최고 ÷ 최저 − 1
latest = [r for r in coil_rows if r["월"] == months[-1]]         # 현재 = 마지막 달


def margin(r, coil_mult=1.0):
    """톤당 판가·원재료비·영업이익 — 판가·가공비는 그대로, 코일가만 바꾼다"""
    price = int(r["판가(원/톤)"])
    raw = int(r["열연코일가격(원/톤)"]) * coil_mult * float(r["코일소요(톤/톤)"])
    op = price - raw - int(r["가공비(원/톤)"])
    return price, raw, op


scen = {}
for mult in (0.9, 1.0, 1.1):
    rev = opsum = 0
    per = {}
    for r in latest:
        price, raw, op = margin(r, mult)
        vol = int(r["판매량(톤)"])
        rev, opsum = rev + price * vol, opsum + op * vol
        per[r["품목"]] = op / price
    scen[mult] = (opsum / rev, per)

drop = {k: scen[1.0][1][k] - scen[1.1][1][k] for k in scen[1.0][1]}
sens = max(drop, key=drop.get)
sens_row = next(r for r in latest if r["품목"] == sens)
_, raw0, _ = margin(sens_row)
need_up = raw0 * 0.1 / int(sens_row["판가(원/톤)"])            # 톤당 영업이익을 지키는 판가 인상률
total_change_pp = (scen[1.1][0] - scen[1.0][0]) * 100

mg_lines = [
    "# 경영 AI — 열연코일 가격과 마진 (실습용 가상 데이터)", "",
    f"- 열연코일 가격: 최저 {c_min:,}원 ~ 최고 {c_max:,}원 / 변동 폭 {coil_range * 100:.1f}% (최고 ÷ 최저 − 1)",
    f"- 기준 월: {months[-1]} · 판가와 가공비는 그대로 두고 코일가만 바꾼다 (가정)", "",
    "| 품목 | 판가(원/톤) | 원재료비(원/톤) | 스프레드(원/톤) | 영업이익률 −10% | 현재 | +10% |",
    "|---|---|---|---|---|---|---|",
]
for r in latest:
    price, raw, _ = margin(r)
    k = r["품목"]
    mg_lines.append(f"| {k} | {price:,} | {raw:,.0f} | {price - raw:,.0f} | {pct(scen[0.9][1][k], 1)} | "
                    f"{pct(scen[1.0][1][k], 1)} | {pct(scen[1.1][1][k], 1)} |")
mg_lines += [
    f"| 전체(판매량 가중) | | | | {pct(scen[0.9][0], 1)} | {pct(scen[1.0][0], 1)} | {pct(scen[1.1][0], 1)} |", "",
    f"- 코일가 +10%일 때 전체 영업이익률 변화: {total_change_pp:.1f}%p",
    f"- 가장 크게 떨어지는 품목: {sens} ({drop[sens] * 100:.1f}%p 하락)",
    f"- {sens}의 톤당 영업이익을 지키려면 판가를 {need_up * 100:.1f}% 올려야 한다", "",
    f"**결론:** 원재료비 비중이 큰 {sens}부터 코일가 연동 판가 조정을 협상하고, "
    "코일가 시나리오를 매달 갱신해 협상 근거로 쓴다."]
Path("out/margin.md").write_text("\n".join(mg_lines) + "\n", encoding="utf-8")

# ── Block 3 도입 로드맵 ──────────────────────────────────────────
for c in cands:
    c["배수"] = float(c["연간기대효과(억원)"]) / float(c["초기투자(억원)"])
eligible = [c for c in cands if c["배수"] >= 1 and c["데이터준비도"] in ("상", "중")]
top = max(eligible, key=lambda c: c["배수"])
top_effect = max(cands, key=lambda c: float(c["연간기대효과(억원)"]))
ranked = sorted(cands, key=lambda c: (c in eligible, c["배수"]), reverse=True)

rm_lines = ["# AI 도입 로드맵 (실습용 가상 데이터)", "",
            "| 순위 | 과제 | 영역 | 연간 기대효과(억원) | 초기 투자(억원) | 배수 | 데이터 준비도 | 조건 충족 |",
            "|---|---|---|---|---|---|---|---|"]
for n, c in enumerate(ranked, 1):
    rm_lines.append(f"| {n} | {c['과제']} | {c['영역']} | {c['연간기대효과(억원)']} | {c['초기투자(억원)']} | "
                    f"{c['배수']:.1f}배 | {c['데이터준비도']} | {'○' if c in eligible else '× (데이터 부족)'} |")
rm_lines += ["",
    f"- 1순위 파일럿: **{top['과제']}** — 배수 {top['배수']:.1f}배, 데이터 준비도 {top['데이터준비도']}",
    f"- 효과 금액만 보면 1순위는 {top_effect['과제']}({top_effect['연간기대효과(억원)']}억원)이지만 "
    f"데이터 준비도가 '{top_effect['데이터준비도']}'라 90일 안에 결과를 보기 어렵다 → 파일럿과 함께 코일가·구매 데이터를 쌓아 다음 해 과제로 둔다."]
Path("out/roadmap.md").write_text("\n".join(rm_lines) + "\n", encoding="utf-8")

# ── 임원 한 장 보고서 index.html ────────────────────────────────
roadmap = [
    ("0~30일 작게 시작", f"조관기 1대에 진동 센서 데이터 수집·평상 범위 설정, 경보 기준 합의"),
    ("30~60일 확산", "추세 경보를 정비 계획에 연결, 같은 라인 다른 조관기로 확대"),
    ("60~90일 측정", "돌발 정지 시간과 용접 불량률을 파일럿 전과 비교해 다음 투자 결정"),
]
kpis = [
    ("1순위 파일럿", top["과제"], f"배수 {top['배수']:.1f}배 · 투자 {top['초기투자(억원)']}억원"),
    ("정비 계획 시점", trend_date, f"평상 범위 이탈보다 {len([i for i in range(start, trend_anom[0])])}로트 먼저"),
    ("코일가 +10% 시 이익률", f"{total_change_pp:.1f}%p", f"{sens} {drop[sens] * 100:.1f}%p 하락"),
    ("평균 불량률", pct(avg_rate), f"추세 구간 {pct(rate_trend)}"),
]
data = {
    "lots": [r["로트"] for r in lots], "vib": vib, "rate": [round(r["불량률"] * 100, 3) for r in lots],
    "lo": round(lo, 3), "hi": round(hi, 3), "trend": start,
    "items": list(scen[1.0][1].keys()),
    "scen": {k: [round(scen[x][1][k] * 100, 2) for x in (0.9, 1.0, 1.1)] for k in scen[1.0][1]},
    "cands": [{"name": c["과제"], "x": {"하": 1, "중": 2, "상": 3}[c["데이터준비도"]], "y": round(c["배수"], 2),
               "eff": float(c["연간기대효과(억원)"]), "top": c is top} for c in cands],
}
kpi_html = "".join(f'<div class="kpi"><div class="kl">{a}</div><div class="kv">{b}</div><div class="ks">{c}</div></div>'
                   for a, b, c in kpis)
rm_html = "".join(f'<li><b>{a}</b><span>{b}</span></li>' for a, b in roadmap)
html = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>철관 AI 도입 보고서</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
:root{{--navy:#14284b;--ink:#1d2433;--muted:#5b6475;--line:#e3e7ee;--accent:#e8772e;--soft:#f5f7fa}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Pretendard Variable",Pretendard,"Malgun Gothic",sans-serif;background:#fff;color:var(--ink);line-height:1.55}}
header{{background:var(--navy);color:#fff;padding:28px 16px}}
.wrap{{max-width:980px;margin:0 auto;padding:0 16px}}
header .wrap{{padding:0}}
.q{{font-size:.85rem;opacity:.8;margin:0 0 6px}}
h1{{font-size:1.45rem;margin:0 0 8px;line-height:1.35}}
.tag{{display:inline-block;background:var(--accent);color:#fff;font-size:.75rem;padding:2px 8px;border-radius:4px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:20px 0}}
.kpi{{border:1px solid var(--line);border-radius:8px;padding:12px 14px;background:var(--soft)}}
.kl{{font-size:.78rem;color:var(--muted)}}.kv{{font-size:1.25rem;font-weight:700;color:var(--navy)}}.ks{{font-size:.8rem;color:var(--muted)}}
h2{{font-size:1.1rem;color:var(--navy);border-left:4px solid var(--accent);padding-left:8px;margin:28px 0 6px}}
.lead{{margin:0 0 10px;font-size:.95rem}}
.box{{position:relative;height:320px}}
.tbl{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font-size:.88rem}}
th,td{{border-bottom:1px solid var(--line);padding:6px 6px;text-align:right}}
td:first-child{{word-break:keep-all}}
th:not(:first-child),td:not(:first-child){{white-space:nowrap}}
@media(max-width:480px){{table{{font-size:.8rem}}}}
th:first-child,td:first-child{{text-align:left}}th{{color:var(--muted);font-weight:600}}
ol.rm{{list-style:none;padding:0;margin:0;display:grid;gap:8px}}
ol.rm li{{border:1px solid var(--line);border-radius:8px;padding:10px 12px}}
ol.rm b{{display:block;color:var(--navy)}}
footer{{color:var(--muted);font-size:.78rem;margin:32px 0 24px;word-break:keep-all}}
</style></head><body>
<header><div class="wrap">
<p class="q">핵심 질문 — 우리 철관 회사는 제조와 경영 중 어디부터 AI를 도입해야, 어떤 성과를 언제 확인할 수 있는가?</p>
<h1>제조부터: {top['과제']}을 90일 파일럿 1순위로 제안합니다</h1>
<span class="tag">실습용 가상 데이터</span>
</div></header>
<main class="wrap">
<div class="kpis">{kpi_html}</div>

<h2>근거 ① 제조 — 조관기 진동과 용접 불량</h2>
<p class="lead">{lots[noise_anom[0]]['로트']}의 {vib[noise_anom[0]]} mm/s는 한 번 튄 노이즈입니다. {trend_date}({trend_lot})부터 진동이 매 로트 오르고, 같은 구간 불량률도 {pct(rate_before)} → {pct(rate_trend)}로 올랐습니다.</p>
<div class="box"><canvas id="c1"></canvas></div>

<h2>근거 ② 경영 — 열연코일 가격과 마진</h2>
<p class="lead">코일가가 10% 오르면 전체 영업이익률이 {total_change_pp:.1f}%p 움직입니다. {sens}이 가장 민감해, 톤당 이익을 지키려면 판가를 {need_up * 100:.1f}% 올려야 합니다.</p>
<div class="box"><canvas id="c2"></canvas></div>

<h2>비교 — AI 후보 과제 6개</h2>
<p class="lead">효과 금액만 보면 {top_effect['과제']}가 1순위지만 데이터 준비도가 '{top_effect['데이터준비도']}'입니다. 배수 1배 이상 · 데이터 준비도 상/중 중에서는 {top['과제']}가 가장 큽니다.</p>
<div class="box"><canvas id="c3"></canvas></div>
<div class="tbl"><table><tr><th>과제</th><th>영역</th><th>기대효과(억)</th><th>투자(억)</th><th>배수</th><th>데이터</th></tr>
{"".join(f"<tr><td>{c['과제']}</td><td>{c['영역']}</td><td>{c['연간기대효과(억원)']}</td><td>{c['초기투자(억원)']}</td><td>{c['배수']:.1f}배</td><td>{c['데이터준비도']}</td></tr>" for c in ranked)}
</table></div>

<h2>90일 로드맵</h2>
<ol class="rm">{rm_html}</ol>

<footer>실습용 가상 데이터 — learn-steelpipe-ai-exec 실습 자료(production_lots.csv · coil_price_margin.csv · ai_candidates.csv). 실제 기업의 생산·원가 수치가 아닙니다. 방법: 평상 범위(평균 ± 2표준편차)·파일럿 배수(연간 기대효과 ÷ 초기 투자)는 kma-auto-genai-3-1 강의 Day5, 보고 구조는 Day3·Day6를 따랐습니다.</footer>
</main>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const D={json.dumps(data, ensure_ascii=False)};
Chart.defaults.font.family='"Pretendard Variable",Pretendard,"Malgun Gothic",sans-serif';
const navy='#14284b',orange='#e8772e',gray='#9aa3b2';
new Chart(c1,{{data:{{labels:D.lots,datasets:[
 {{type:'line',label:'조관기 진동(mm/s)',data:D.vib,borderColor:navy,pointRadius:D.vib.map((v,i)=>(v>D.hi||v<D.lo)?5:2),
   pointBackgroundColor:D.vib.map((v,i)=>(v>D.hi||v<D.lo)?orange:navy),yAxisID:'y',tension:.2}},
 {{type:'line',label:'평상 범위 상한',data:D.vib.map(()=>D.hi),borderColor:orange,borderDash:[6,4],pointRadius:0,yAxisID:'y'}},
 {{type:'line',label:'평상 범위 하한',data:D.vib.map(()=>D.lo),borderColor:gray,borderDash:[6,4],pointRadius:0,yAxisID:'y'}},
 {{type:'bar',label:'용접 불량률(%)',data:D.rate,backgroundColor:D.rate.map((v,i)=>i>=D.trend?'rgba(232,119,46,.35)':'rgba(154,163,178,.35)'),yAxisID:'y2'}}]}},
 options:{{maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},plugins:{{legend:{{position:'bottom',labels:{{boxWidth:12}}}}}},
 scales:{{x:{{ticks:{{maxTicksLimit:8}}}},y:{{title:{{display:true,text:'mm/s'}}}},y2:{{position:'right',grid:{{drawOnChartArea:false}},title:{{display:true,text:'불량률 %'}}}}}}}}}});
new Chart(c2,{{type:'bar',data:{{labels:D.items,datasets:[
 {{label:'코일가 −10%',data:D.items.map(k=>D.scen[k][0]),backgroundColor:gray}},
 {{label:'현재',data:D.items.map(k=>D.scen[k][1]),backgroundColor:navy}},
 {{label:'코일가 +10%',data:D.items.map(k=>D.scen[k][2]),backgroundColor:orange}}]}},
 options:{{maintainAspectRatio:false,plugins:{{legend:{{position:'bottom',labels:{{boxWidth:12}}}}}},scales:{{y:{{title:{{display:true,text:'영업이익률 %'}}}}}}}}}});
new Chart(c3,{{type:'bubble',data:{{datasets:D.cands.map(c=>({{label:c.name,data:[{{x:c.x,y:c.y,r:4+c.eff*1.6}}],
 backgroundColor:c.top?'rgba(232,119,46,.75)':'rgba(20,40,75,.35)',borderColor:c.top?orange:navy}}))}},
 options:{{maintainAspectRatio:false,plugins:{{legend:{{position:'bottom',labels:{{boxWidth:10}}}},
 tooltip:{{callbacks:{{label:t=>t.dataset.label+' · '+t.raw.y+'배'}}}}}},
 scales:{{x:{{min:.5,max:3.5,afterBuildTicks:a=>{{a.ticks=[1,2,3].map(v=>({{value:v}}))}},ticks:{{callback:v=>({{1:'하',2:'중',3:'상'}})[v]}},title:{{display:true,text:'데이터 준비도'}}}},
 y:{{min:0,title:{{display:true,text:'파일럿 배수 (기대효과 ÷ 투자)'}}}}}}}}}});
</script>
</body></html>
"""
Path("index.html").write_text(html, encoding="utf-8")

# ── expected.json ──────────────────────────────────────────────
V = lambda v, d, b: {"value": v, "decimals": d, "block": b}
expected = {"values": {
    "lots_rows": V(len(lots), 0, 0), "coil_rows": V(len(coil_rows), 0, 0), "candidates_rows": V(len(cands), 0, 0),
    "avg_defect_rate": V(round(avg_rate * 100, 2), 2, 1),
    "vib_anomaly_count": V(len(anom), 0, 1), "vib_noise_count": V(len(noise_anom), 0, 1),
    "vib_trend_count": V(len(trend_anom), 0, 1),
    "trend_start_date": {"value": trend_date, "block": 1}, "trend_start_lot": {"value": trend_lot, "block": 1},
    "coil_range_pct": V(round(coil_range * 100, 1), 1, 2),
    "margin_change_pp_up10": V(round(total_change_pp, 1), 1, 2),
    "most_sensitive_product": {"value": sens, "block": 2},
    "required_price_up_pct": V(round(need_up * 100, 1), 1, 2),
    "top_pilot": {"value": top["과제"], "block": 3}, "top_pilot_multiple": V(round(top["배수"], 1), 1, 3),
    "top_by_effect": {"value": top_effect["과제"], "block": 3},
}}
Path("expected.json").write_text(json.dumps(expected, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n".join(mfg_lines[2:5] + mg_lines[-5:-2] + rm_lines[-2:]))
