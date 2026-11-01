// 교재 ch1~3.md → Word(.docx). 실행: node build_docx.js <textbook 폴더> <출력 .docx> [Pretendard-Regular.ttf]
// 글꼴 파일을 주면 문서 안에 넣는다 — Pretendard가 설치되지 않은 PC에서도 같은 서체로 보이게.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  ShadingType, BorderStyle, ImageRun, AlignmentType, PageBreak, Footer, PageNumber, LevelFormat, CharacterSet,
} = require("docx");

const [, , dir, outFile, fontFile] = process.argv;
const FONT = "Pretendard";
const NAVY = "14284B", ORANGE = "E8772E", MUTED = "5B6475", SOFT = "F5F7FA", LINE = "D5DBE5";
const CONTENT_W = 11906 - 2 * 1134; // A4 폭 − 좌우 여백 2cm (DXA)

// **굵게**, *기울임*, `코드` 를 TextRun 으로
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: "Consolas", ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

function table(lines) {
  const rows = lines.filter((l) => !/^\|\s*-/.test(l)).map((l) =>
    l.replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
  const n = rows[0].length;
  // 열 너비: 글자 수 비례, 최소 1500 DXA (날짜가 한 줄에 들어가게)
  const len = Array.from({ length: n }, (_, i) => Math.max(...rows.map((r) => (r[i] || "").length), 2));
  const sum = len.reduce((a, b) => a + b, 0);
  let widths = len.map((v) => Math.max(1500, Math.round((v / sum) * CONTENT_W)));
  const scale = CONTENT_W / widths.reduce((a, b) => a + b, 0);
  widths = widths.map((w) => Math.floor(w * scale));
  widths[n - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: ri === 0,
      children: widths.map((w, ci) => new TableCell({
        width: { size: w, type: WidthType.DXA },
        shading: ri === 0 ? { type: ShadingType.CLEAR, fill: NAVY, color: "auto" } : undefined,
        borders: { top: border, bottom: border, left: border, right: border },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({ children: runs(r[ci] || "", ri === 0 ? { bold: true, color: "FFFFFF", size: 19 } : { size: 19 }) })],
      })),
    })),
  });
}

function image(src) {
  const png = path.join(dir, src.replace(/\.svg$/, ".png"));
  const isWide = src.includes("fig1");
  const w = isWide ? 620 : 540, h = isWide ? Math.round(620 * 560 / 1200) : Math.round(540 * 560 / 900);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(png), transformation: { width: w, height: h } })] });
}

const children = [];
// 표지
children.push(
  new Paragraph({ spacing: { before: 2400 }, children: [new TextRun({ text: "강의 교재", color: ORANGE, bold: true, size: 26 })] }),
  new Paragraph({ spacing: { before: 120, after: 120 }, children: [new TextRun({ text: "철관 제조기업 임원을 위한 제조·경영 AI", bold: true, size: 52, color: NAVY })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "1장 제조 AI · 2장 경영 AI · 3장 도입 로드맵", size: 26, color: MUTED })] }),
  new Paragraph({ shading: { type: ShadingType.CLEAR, fill: SOFT }, border: { left: { style: BorderStyle.SINGLE, size: 24, color: ORANGE, space: 8 } },
    spacing: { after: 240 }, children: [new TextRun({ text: "핵심 질문 — 우리 철관 회사는 제조와 경영 중 어디부터 AI를 도입해야, 어떤 성과를 언제 확인할 수 있는가?", size: 24, bold: true })] }),
  new Paragraph({ spacing: { before: 1200 }, children: [new TextRun({ text: "숫자는 공개 자료에서만 가져왔고, 문장 끝의 [S번호]가 출처다. 출처 목록은 각 장 끝에 있다.", size: 19, color: MUTED })] }),
  new Paragraph({ children: [new TextRun({ text: "강의 실습의 데이터는 실습용 가상 데이터이며 이 교재 본문에는 쓰지 않았다.", size: 19, color: MUTED })] }),
);

for (const ch of ["ch1.md", "ch2.md", "ch3.md"]) {
  const lines = fs.readFileSync(path.join(dir, ch), "utf8").split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (!l.trim() || l.trim() === "---") continue;
    if (l.startsWith("|")) {
      const block = [];
      while (i < lines.length && lines[i].startsWith("|")) block.push(lines[i++]);
      i--;
      children.push(table(block), new Paragraph({ spacing: { after: 120 }, children: [] }));
    } else if (l.startsWith("# ")) {
      children.push(new Paragraph({ children: [new PageBreak()] }),
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(l.slice(2))] }));
    } else if (l.startsWith("## ")) {
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(l.slice(3))] }));
    } else if (l.startsWith("### ")) {
      children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(l.slice(4))] }));
    } else if (l.startsWith("![")) {
      children.push(image(l.match(/\(([^)]+)\)/)[1]));
    } else if (l.startsWith("> ")) {
      children.push(new Paragraph({ shading: { type: ShadingType.CLEAR, fill: SOFT },
        border: { left: { style: BorderStyle.SINGLE, size: 24, color: ORANGE, space: 8 } },
        spacing: { before: 80, after: 160 }, children: runs(l.slice(2)) }));
    } else if (/^- /.test(l)) {
      children.push(new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: runs(l.slice(2)) }));
    } else if (/^\d+\. /.test(l)) {
      const [, num, rest] = l.match(/^(\d+)\. (.*)$/);
      children.push(new Paragraph({ indent: { left: 400, hanging: 400 }, spacing: { after: 80 },
        children: [new TextRun({ text: num + ". ", bold: true, color: NAVY }), ...runs(rest)] }));
    } else if (/^\*[^*].*\*$/.test(l.trim())) {
      children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
        children: runs(l.trim().slice(1, -1), { italics: true, color: MUTED, size: 18 }) }));
    } else {
      children.push(new Paragraph({ spacing: { after: 140 }, children: runs(l) }));
    }
  }
}

const doc = new Document({
  creator: "learn-steelpipe-ai-exec",
  fonts: fontFile ? [{ name: FONT, data: fs.readFileSync(fontFile), characterSet: CharacterSet.HANGUL }] : [],
  title: "철관 제조기업 임원을 위한 제조·경영 AI — 교재",
  styles: {
    default: { document: { run: { font: { ascii: FONT, eastAsia: FONT, hAnsi: FONT, cs: FONT }, size: 21 }, paragraph: { spacing: { line: 320 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, color: NAVY, font: FONT }, paragraph: { spacing: { after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: NAVY, font: FONT },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 1, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ORANGE, space: 4 } } } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, color: NAVY, font: FONT }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(outFile, b); console.log("ok", outFile); });
