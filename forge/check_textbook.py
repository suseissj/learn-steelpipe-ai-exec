"""교재 검수 — ① 출처 번호 없는 숫자 ② facts.csv와 다른 숫자 ③ 미확보 관련 문장 후보를 찾는다.

실행: python3 -I forge/check_textbook.py <패키지 폴더>
- 문장(표는 행) 단위로 본다. '이 장의 출처' 절과 제목·그림 파일 경로는 제외한다.
- 구성 숫자(장·단계 번호, 목록 번호, 90일 로드맵 구간, 배수 1배 기준, ± 2표준편차)는 사실 숫자가 아니므로 따로 표시만 한다.
"""
import csv, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
pkg = Path(sys.argv[1])
facts = list(csv.DictReader(open(pkg / "forge/research/facts.csv", encoding="utf-8-sig")))
norm = lambda t: re.sub(r"[\s,]", "", t)
fact_text = norm(" ".join(r["값(원문)"] + " " + r["기준시점"] for r in facts))

STRUCT = re.compile(r"^(0|30|60|30일|60일|90일|1배|1년|2표준편차|[1-9]장|Day[0-9]|Block[0-9])$")
NUM = re.compile(r"\d[\d,.]*(?:\s?(?:만\s?[\d,]*원|억원|만달러|원|%p|%|톤|t|곳|건|개사|개|년|월|일|배|분기|주))?")

rows = []
for ch in ("ch1.md", "ch2.md", "ch3.md"):
    text = (pkg / "textbook" / ch).read_text(encoding="utf-8").split("## 이 장의 출처")[0]
    for ln, line in enumerate(text.splitlines(), 1):
        if line.startswith("#") or line.startswith("![") or not re.search(r"\d", line):
            continue
        units = [line] if line.startswith("|") else re.split(r"(?<=\.)\s+|(?<=\.\*)\s+|(?<=\.\))\s+", line)
        for u in units:
            body = re.sub(r"\[S\d+\]|S\d+|F\d+|^\s*\d+\.\s|^\d+\.$|[①-⑤]|Day\d|Block\s?\d|[1-9]장|그림 \d\.?|「[^」]*」|\d{4}\.\d{2}\.\d{2}", " ", u)
            body = re.sub(r"\d{4}-\d{2}-\d{2}", " ", body)
            for m in NUM.finditer(body):
                tok = m.group().strip()
                core = re.match(r"[\d,.]+", tok).group().rstrip(".,")
                if not core:
                    continue
                if STRUCT.match(norm(tok)) or tok in ("1", "2", "3", "4", "5"):
                    kind = "구성 숫자"
                else:
                    kind = None
                has_src = bool(re.search(r"\[S\d+\]", u)) or "출처:" in u
                in_facts = norm(core) in fact_text
                rows.append((ch, ln, tok, kind, has_src, in_facts, u.strip()[:70]))

print("| 장 | 줄 | 숫자 | ① 출처 번호 | ② facts.csv | 문장 |")
print("|---|---|---|---|---|---|")
for ch, ln, tok, kind, has_src, in_facts, u in rows:
    if kind:
        continue
    if has_src and in_facts:
        continue
    print(f"| {ch} | {ln} | {tok} | {'있음' if has_src else '**없음**'} | {'일치' if in_facts else '**없음**'} | {u} |")
print()
print(f"사실 숫자 {sum(1 for r in rows if not r[3])}개 · 구성 숫자 {sum(1 for r in rows if r[3])}개 검사")

print("\n③ 미확보 관련 문장 후보")
keys = r"미확보|확인하지 못|찾지 못|없다|아직|공개 성과|교차 확인"
for ch in ("ch1.md", "ch2.md", "ch3.md"):
    text = (pkg / "textbook" / ch).read_text(encoding="utf-8").split("## 이 장의 출처")[0]
    for ln, line in enumerate(text.splitlines(), 1):
        for u in re.split(r"(?<=\.)\s+", line):
            if re.search(keys, u):
                print(f"- {ch}:{ln} {u.strip()[:110]}")
