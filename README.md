# 철관 제조기업 임원을 위한 제조·경영 AI — learn-steelpipe-ai-exec

철관(강관) 제조기업 임원이 90분 동안 제조 AI(용접 불량·조관기 진동)와 경영 AI(열연코일 가격·마진)를 가상 데이터로 직접 돌려 보고, AI 도입 1순위 파일럿을 고른 임원 한 장 보고서를 공개하는 강의다. 수업은 Claude Code 스킬 `/learn-steelpipe-ai-exec`가 진행한다 (Skills as Curriculum). 이 강의는 suseissj가 course-forge로 직접 만들었다.

> **핵심 질문** — 우리 철관 회사는 제조와 경영 중 어디부터 AI를 도입해야, 어떤 성과를 언제 확인할 수 있는가?

- **결과 대시보드(임원 한 장 보고서)**: https://suseissj.github.io/learn-steelpipe-ai-exec/
- 처음이면 [GUIDE.md](GUIDE.md)부터. 기본 환경은 Claude 데스크톱 앱(Code 탭). VS Code는 GUIDE 부록 B
- 교재 3장: [textbook/Robot_Value_Chain_Textbook.pdf](textbook/Robot_Value_Chain_Textbook.pdf) · 강의 덱 19장: [deck/SteelPipe_AI_Lecture_Deck.pdf](deck/SteelPipe_AI_Lecture_Deck.pdf)

## 설치 — 한 줄

Claude Code 입력칸에 붙여 넣는다.

```
npx skills add suseissj/learn-steelpipe-ai-exec --agent claude-code --global --yes 를 실행해 줘
```

새 세션에서 `/learn-steelpipe-ai-exec`를 입력하면 수업이 시작된다. zip을 받았다면 GUIDE.md 2단계대로 설치한다.

## 블록

| Block | 주제 | 끝나면 생기는 것 |
|---|---|---|
| 0 | 준비 (10분) | 작업 폴더와 실습 데이터 3종, env_check.txt |
| 1 | 제조 AI — 용접 불량·조관기 진동 (20분) | 불량률·진동 차트 |
| 2 | 경영 AI — 열연코일 가격과 마진 (20분) | 코일가 시나리오별 마진 표 |
| 3 | 도입 로드맵 — 1순위 파일럿 (25분) | 임원 한 장 보고서 (index.html) |
| 4 | 공개 (10분) | 보고서 웹 주소 |
| 5 | 공유 (5분) | README와 세 줄 공유 메시지 |

## 결과물 세 가지

| 결과물 | 위치 | 내용 |
|---|---|---|
| 강의 스킬 | `.claude/skills/learn-steelpipe-ai-exec/` | 블록 6개 · 판단형 퀴즈 5문항 · 실습 데이터 · 정답 스크립트 |
| 교재 3장 | `textbook/` | 1장 제조 AI · 2장 경영 AI · 3장 도입 로드맵 (Word·PDF·Markdown, 그림 2장) |
| 강의 덱 | `deck/` | 19장, 본문 20pt (PowerPoint·PDF) |

## 수업 방식

| 구분 | 내용 |
|---|---|
| 목표 — AI Native | 분석은 AI에게 맡기고, 사람은 질문을 정하고 결과로 결정한다 |
| 방법 — Skills as Curriculum | 스킬이 블록마다 설명 → 실습 → STOP → 확인·퀴즈를 진행한다 |
| 형식 — 자율학습 | 강사 없이 자기 속도로, 퀴즈로 스스로 점검한다 |

## 원본 강의와 데이터 출처

| 자료 | 출처 | 구분 |
|---|---|---|
| 방법 — 평상 범위(평균 ± 2σ), 노이즈 vs 추세, 파일럿 배수 | [keerhee/kma-auto-genai-3-1](https://github.com/keerhee/kma-auto-genai-3-1) Day5 예지보전 · `data/_강사용_정답메모.md` | 원본 강의 |
| 재무 지표·임원 보고 구조·90일 로드맵 | 같은 저장소 Day3 경쟁사 재무 · Day6 최종 프로젝트 | 원본 강의 |
| 실습 데이터 3종 | `assets/lab/` — 이 강의 제작 시 생성 (`forge/make_lab_data.py`) | **실습용 가상 데이터** |
| 교재·덱의 숫자 | 공개 보도·증권사 보고서·정부 조사 20건 — `forge/research/sources.md`, 숫자 원문은 `forge/research/facts.csv` | 공개 자료 (문장 끝 [S번호]) |

실습 데이터는 실제 기업의 생산·원가·투자 수치가 아니다. 회사 자료로 바꿔 쓸 때는 공개 저장소에 올리지 않는다.

## 개정 이력

| 날짜 | 바뀐 점 |
|---|---|
| 2026-11-01 | 첫 판 — 강의 스킬 6블록, 교재 3장, 강의 덱 19장 |

## 만든 방법

- `/course-forge`로 만들었다. 제작 기록(brief·커리큘럼·자료 조사·검수 결과)은 `forge/`에 있다.
- 강의 덱은 report-navy-deck 스킬로 만들었다. 서체는 Pretendard(설치되지 않은 PC에서는 대체 글꼴로 보인다). Word 교재에는 Pretendard 글꼴 파일(SIL Open Font License)이 들어 있다.
- 출처: 원본 강의 저장소 https://github.com/keerhee/kma-auto-genai-3-1
