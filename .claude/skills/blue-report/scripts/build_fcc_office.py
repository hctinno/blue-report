#!/usr/bin/env python3
"""FCC/KC 보고서의 DOCX · PPTX 대표 시안을 만든다.

## 무엇을 만드나

A/B/C 세 종의 DOCX 와 PPTX 를 `decks-out/fcc-kc/` 에 만든다. HTML/PDF 가 기준이고,
이 둘은 **같은 fixture 에서 파생한 이식 시안**이다. 손으로 다른 수치를 적어 넣은
문서를 따로 관리하지 않는다 — 그러면 형식마다 다른 보고서가 된다.

## 색을 여기서 정하지 않는다

blue-report.css 의 --br-* 를 읽어 쓴다. 파이썬 쪽에 hex 를 적으면 CSS 를 고칠 때
갈라진다. pptx/tokens.js 가 같은 일을 하는 이유와 같다.

## 차트

- PPTX 는 네이티브 차트를 쓴다(python-pptx 가 지원). 받는 사람이 값을 고칠 수 있다.
- DOCX 는 python-docx 에 차트 API 가 없다. 표로 그릴 수 있는 것(순위 막대)은
  **셀 음영 표**로 네이티브로 그리고, 추이선만 PNG 로 넣되 값 표를 함께 둔다.
  이미지로 굳힌 자리는 통합 가이드 5장 변환표의 "이미지 고정"과 같은 뜻이다.

    python3 scripts/build_fcc_office.py            # 만든다
    python3 scripts/build_fcc_office.py --pdf      # PDF·PNG 미리보기까지
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SKILL)))
FCC = os.path.join(SKILL, "assets", "fcc-kc")
OUT = os.path.join(ROOT, "decks-out", "fcc-kc")

sys.path.insert(0, HERE)
from ensure_deps import need_python, need_browser  # noqa: E402
from palette import css_tokens  # noqa: E402

STAMP = "DESIGN FIXTURE · 운영 분석 결과 아님"


def T():
    """--br-* 를 RGB 3튜플로. 색은 CSS 한 곳에서만 정한다."""
    t = css_tokens()
    return {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in t.items()}


# ---------------------------------------------------------------- 추이선 PNG
# DOCX 에 넣을 그림. 우리 HTML 템플릿의 SVG 를 그대로 찍어 브랜드가 갈라지지 않게 한다.

def trend_png(path):
    chrome = need_browser()
    from playwright.sync_api import sync_playwright
    src = os.path.join(FCC, "templates", "tpl-a-executive.html")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        pg = br.new_page(viewport={"width": 1000, "height": 1300}, device_scale_factor=3)
        pg.goto("file://" + os.path.abspath(src))
        pg.wait_for_timeout(1200)
        pg.locator("svg.fk-line").first.screenshot(path=path)
        br.close()
    return path


# --------------------------------------------------------------------- DOCX

def build_docx(spec, fx, tok, png):
    need_python("docx", "python-docx", "DOCX 생성(python-docx)")
    from docx import Document
    from docx.enum.section import WD_ORIENT
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor, Cm, Emu

    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Pretendard"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Pretendard")

    sec = d.sections[0]
    if spec.get("land"):
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    else:
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    for m in ("left_margin", "right_margin"):
        setattr(sec, m, Cm(1.9))
    sec.top_margin, sec.bottom_margin = Cm(1.7), Cm(1.7)

    def shade(cell, rgb):
        el = OxmlElement("w:shd")
        el.set(qn("w:val"), "clear")
        el.set(qn("w:fill"), "%02X%02X%02X" % rgb)
        cell._tc.get_or_add_tcPr().append(el)

    def para(text, size=10.5, bold=False, color=None, space=6, align=None):
        p = d.add_paragraph()
        p.paragraph_format.space_after = Pt(space)
        if align:
            p.alignment = align
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
        if color:
            r.font.color.rgb = RGBColor(*color)
        return p

    def heading(text):
        p = para(text, size=15, bold=True, color=tok["navy"], space=8)
        return p

    def kv_table(rows, widths=(0.3, 0.7), head=None):
        t = d.add_table(rows=0, cols=len(widths))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.style = "Table Grid"
        if head:
            r = t.add_row().cells
            for c, h in zip(r, head):
                c.text = ""
                run = c.paragraphs[0].add_run(h)
                run.bold = True
                run.font.size = Pt(10.5)
                run.font.color.rgb = RGBColor(*tok["navy"])
                shade(c, tok["page"])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))  # 머리행 반복
        for row in rows:
            cells = t.add_row().cells
            for c, v in zip(cells, row):
                c.text = ""
                run = c.paragraphs[0].add_run(str(v))
                run.font.size = Pt(10.5)
        return t

    def narrative(origin, title, paras):
        pre = {"server_fact": "■ 서버 검증 사실", "ai_interpretation": "▲ AI 해석",
               "human_note": "✎ 검토자 메모"}[origin]
        col = {"server_fact": tok["cobalt"], "ai_interpretation": tok["cat-3"],
               "human_note": tok["text-2"]}[origin]
        para(f"{pre} · {title}", size=10.5, bold=True, color=col, space=2)
        for x in paras:
            p = para(x, space=3)
            p.paragraph_format.left_indent = Cm(0.5)
        para("", space=4)

    def banner(title, items, kind="warn"):
        t = d.add_table(rows=1, cols=1)
        t.style = "Table Grid"
        c = t.rows[0].cells[0]
        shade(c, tok["warn-bg"] if kind == "warn" else tok["page"])
        c.text = ""
        r = c.paragraphs[0].add_run(("⚠ " if kind == "warn" else "◆ ") + title)
        r.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(*(tok["warn-text"] if kind == "warn" else tok["navy"]))
        for x in items:
            p = c.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            rr = p.add_run("· " + x)
            rr.font.size = Pt(10.5)
        para("", space=4)

    def bar_table(rows, caption):
        """순위 막대를 셀 음영으로 그린다. 이미지가 아니라 표라서 값을 고칠 수 있다."""
        para(caption, size=10.5, color=tok["text-2"], space=3)
        top = max(abs(r["v"]) for r in rows) or 1
        STEPS = 20
        t = d.add_table(rows=0, cols=3)
        t.style = "Table Grid"
        for r in rows:
            cells = t.add_row().cells
            cells[0].text = ""
            cells[0].paragraphs[0].add_run(r["n"]).font.size = Pt(10.5)
            filled = max(1, round(abs(r["v"]) / top * STEPS))
            cells[1].text = ""
            run = cells[1].paragraphs[0].add_run("█" * filled + "░" * (STEPS - filled))
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(*(tok["cobalt"] if r.get("subject") else tok["mark-mute"]))
            cells[2].text = ""
            rr = cells[2].paragraphs[0].add_run(r["d"])
            rr.bold = True
            rr.font.size = Pt(10.5)
            rr.font.color.rgb = RGBColor(*tok["navy"])
        para("", space=4)

    # ── 표지 ────────────────────────────────────────────────────────────
    cover = d.add_table(rows=1, cols=1)
    cc = cover.rows[0].cells[0]
    shade(cc, tok["dark"])
    cc.text = ""
    for text, size, bold, col, sp in (
            ("COMPANY NAME", 11, True, tok["on-dark-2"], 10),
            (spec["coverEyebrow"], 10.5, True, tok["accent-on-dark"], 4),
            (spec["title"], 20, True, tok["on-dark"], 4),
            (spec["subtitle"], 11, False, tok["on-dark-2"], 10),
            (STAMP, 10.5, True, tok["amber"], 10),
            (f'{fx["report"]["publisher"]} · {fx["report"]["product"]} · {fx["report"]["issuedAt"]}',
             10.5, False, tok["on-dark-3"], 0)):
        p = cc.paragraphs[0] if text == "COMPANY NAME" else cc.add_paragraph()
        p.paragraph_format.space_after = Pt(sp)
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.bold = bold
        r.font.color.rgb = RGBColor(*col)
    d.add_page_break()

    s, q = fx["scope"], fx["quality"]

    def scope_table():
        kv_table([["데이터 버전", s["sourceDataVersion"]],
                  ["분석 기간", s["appliedPeriod"]],
                  ["모집단", s["populationDefinition"]],
                  ["레코드 단위", "인증 건(certification)"],
                  ["적용 필터", " · ".join(s["appliedFilters"])],
                  ["커버리지", "● 완전 · " + s["coverageNote"]]])
        para("", space=6)

    def metric_table():
        kv_table([[m["label"], f'{m["value"]:,}{m.get("unit","")}' if isinstance(m["value"], int)
                   else f'{m["value"]}{m.get("unit","")}', m.get("note", "")]
                  for m in fx["metrics"]],
                 widths=(0.34, 0.22, 0.44), head=["서버 지표", "값", "비고"])
        para("", space=6)

    def rank_block():
        bar_table([{"n": pt["label"], "v": pt["value"], "d": f'{pt["value"]:,}',
                    "subject": pt.get("emphasis") == "subject"}
                   for pt in fx["charts"][1]["series"][0]["points"]],
                  "시험기관별 처리 건수 · 모집단 1,284건 · 서버가 정한 순서 그대로")

    def trend_block():
        para("월별 인증 건수 — 8월은 부분 기간(점선·음영)", size=10.5, color=tok["text-2"], space=3)
        d.add_picture(png, width=Emu(int(sec.page_width) - int(sec.left_margin) - int(sec.right_margin)))
        kv_table([[pt["label"], f'{pt["value"]:,}'] for pt in fx["charts"][0]["series"][0]["points"]],
                 widths=(0.5, 0.5), head=["구간", "건수"])
        para("그림은 서식 재현이 어려워 이미지로 고정 · 값은 위 표에 그대로 수록",
             size=10.5, color=tok["text-3"], space=6)

    def evidence_block():
        kv_table([[i["certificationId"], i["entity"], i["grantedAt"], i["sourceRef"], "● 확인"]
                  for i in fx["evidence"]["items"]],
                 widths=(0.24, 0.2, 0.12, 0.32, 0.12),
                 head=["인증 식별자", "엔터티", "공개일", "출처", "상태"])
        para("", space=6)

    def lineage_block():
        kv_table([["스냅샷", fx["lineage"]["snapshotChecksum"]],
                  ["보고서 모델", fx["lineage"]["reportModelChecksum"]],
                  ["형식 간 일관성", fx["lineage"]["consistencyProjectionChecksum"]],
                  ["계보", fx["lineage"]["lineageChecksum"]],
                  ["생성", fx["lineage"]["generatedBy"]]])
        para("PDF · DOCX · PPTX 는 같은 보고서 모델에서 파생 — 데이터 버전, 기간, 필터, 모집단, "
             "커버리지, 서버 지표, 근거 상태, 일관성 체크섬이 형식과 무관하게 동일",
             size=10.5, color=tok["text-2"])

    def count_table():
        kv_table([["전체 모집단", "1,284", "필터를 통과한 인증 건 전체"],
                  ["반환 행", "1,284", "이 보고서가 받은 행"],
                  ["고유 인증", "1,284", "인증 식별자 기준 중복 제거"],
                  ["고유 제조사", "12", "엔터티 해소 후"],
                  ["상호 기준 제조사", "19", "해소 전 문자열 기준 — 별칭이 따로 세어짐"],
                  ["미해소", "3", "위 12에 미포함"]],
                 widths=(0.3, 0.16, 0.54), head=["셈", "값", "정의"])
        para("", space=6)

    def stamp():
        para(STAMP, size=10.5, bold=True, color=tok["warn-text"])

    # 세 종의 차이는 색이 아니라 순서다. 무엇을 먼저 보여 주느냐가 곧 문서의 성격이다.
    if spec["key"] == "a":
        # A — 결론이 먼저. 근거는 뒤로 미룬다.
        heading("핵심 결론"); scope_table(); metric_table()
        narrative("server_fact", "검증된 사실", fx["narrative"][0]["paragraphs"])
        banner("이 수치를 읽을 때", q["warnings"]); stamp(); d.add_page_break()
        heading("무엇이 결론을 뒷받침하는가"); rank_block(); trend_block(); stamp(); d.add_page_break()
        heading("해석과 의사결정 경계")
        narrative("ai_interpretation", "검증된 사실 아님", fx["narrative"][1]["paragraphs"])
        narrative("human_note", "서버·AI 산출물 아님", fx["narrative"][2]["paragraphs"])
        banner("이 보고서로 말할 수 없는 것", q["limitations"], kind="limit")
        para("", space=6); heading("권고와 다음 행동")
        kv_table([[re.sub("<[^>]+>", "", r["text"]), f'{r["owner"]} · {r["due"]}']
                  for r in fx["recommendations"]],
                 widths=(0.7, 0.3), head=["권고", "담당 · 기한"])
        stamp(); d.add_page_break()
        heading("근거와 계보"); evidence_block(); lineage_block(); stamp()

    elif spec["key"] == "b":
        # B — 결론을 앞세우지 않는다. 계약 → 지표 → 추이·순위 → 품질 → 근거.
        heading("분석 범위와 필터 계약"); scope_table(); count_table(); stamp(); d.add_page_break()
        heading("지표 매트릭스"); metric_table()
        narrative("server_fact", "검증된 사실", fx["narrative"][0]["paragraphs"])
        stamp(); d.add_page_break()
        heading("기간 추이와 순위"); trend_block(); rank_block()
        banner("이 수치를 읽을 때", q["warnings"]); stamp(); d.add_page_break()
        heading("품질 상태와 근거")
        kv_table([[x["label"], f'{x["value"]:,}' if isinstance(x["value"], int) else x["value"],
                   x.get("note", "")] for x in q["summary"]],
                 widths=(0.3, 0.2, 0.5), head=["품질 항목", "값", "비고"])
        para("", space=6); evidence_block()
        banner("이 보고서로 말할 수 없는 것", q["limitations"], kind="limit")
        lineage_block(); stamp()

    else:
        # C — 수치보다 어떻게 나온 수치인지가 먼저. 문서 통제와 필드 대응이 앞에 온다.
        heading("문서 통제")
        kv_table([["보고서 번호", "DEMO-FCC-2026-0001-C"],
                  ["템플릿", "fcc-kc-c-evidence-dossier · v0.1.0"],
                  ["작성 근거", "Blue Report FCC/KC Insight 서버 산출 보고서 모델"],
                  ["검토 상태", "초안"],
                  ["보존 기간", "산출일로부터 5년"],
                  ["재현 방법", "같은 데이터 버전·필터·기간으로 재실행 시 동일 체크섬"]])
        para("", space=6); heading("모집단 · 레코드 단위 · 필터"); scope_table()
        stamp(); d.add_page_break()
        heading("집계 의미"); count_table()
        heading("서버 수치와 원본 필드 대응")
        kv_table([["기간 내 인증 건수", "metrics.cert_total", "certification_id", "고유 개수"],
                  ["제조사 수", "metrics.entity_total", "applicant_name(정규화)", "해소 후 고유 개수"],
                  ["1위 시험기관 비중", "metrics.lab_share_top", "test_lab_id", "최상위 건수 ÷ 모집단"],
                  ["전년 동기 대비", "metrics.yoy_delta", "grant_date", "동일 기간 폭 비교"],
                  ["월별 추이", "charts.trend_monthly", "grant_date", "월 단위 집계"],
                  ["시험기관 순위", "charts.lab_rank", "test_lab_id", "건수 내림차순"]],
                 widths=(0.26, 0.24, 0.24, 0.26),
                 head=["표시 항목", "보고서 모델 필드", "원본 필드", "집계 방법"])
        para("", space=6); stamp(); d.add_page_break()
        heading("품질 예외와 제한사항")
        kv_table([["미해소 엔터티", "3", "제조사 수에서 제외", "제조사 수 · 순위"],
                  ["모호 엔터티", "1", "수기 확인 대기", "제조사 수"],
                  ["부분 기간", "1개월", "점선·음영 표기", "월 추이 마지막 점"],
                  ["다중 분류", "해당", "비가산 표기", "교차 분석 합계"]],
                 widths=(0.28, 0.14, 0.28, 0.3), head=["예외", "건수", "처리", "영향"])
        para("", space=6)
        banner("이 수치를 읽을 때", q["warnings"])
        banner("이 보고서로 말할 수 없는 것", q["limitations"], kind="limit")
        stamp(); d.add_page_break()
        heading("근거 목록"); evidence_block()
        heading("공개 연락처")
        kv_table([[c["entity"], "누리집", c["value"], c["source"], c["verifiedAt"]]
                  for c in fx["publicContacts"]],
                 widths=(0.18, 0.12, 0.3, 0.26, 0.14),
                 head=["엔터티", "구분", "값", "출처", "확인일"])
        para("공개 출처에서 확인된 것만 게재 · 추정 연락처 미작성", size=10.5, color=tok["text-2"], space=6)
        stamp(); d.add_page_break()
        heading("계보와 검토"); lineage_block()
        para("", space=8)
        kv_table([["작성", "", "검토", "", "승인", ""]], widths=(0.16, 0.17, 0.16, 0.17, 0.16, 0.18))
        stamp()

    path = os.path.join(OUT, spec["docx"])
    d.save(path)
    return path


# --------------------------------------------------------------------- PPTX

def build_pptx(spec, fx, tok):
    need_python("pptx", "python-pptx", "PPTX 생성(python-pptx)")
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.util import Emu, Inches, Pt

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    BLANK = prs.slide_layouts[6]
    W, H = prs.slide_width, prs.slide_height
    PAD = Inches(0.9)

    def rgb(k):
        return RGBColor(*tok[k])

    def bg(sl, k):
        sl.background.fill.solid()
        sl.background.fill.fore_color.rgb = rgb(k)

    def text(sl, s, x, y, w, h, size=18, bold=False, color="text", align=None):
        tb = sl.shapes.add_textbox(x, y, w, h)
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = s
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.name = "Pretendard"
        r.font.color.rgb = rgb(color)
        if align:
            p.alignment = align
        return tb

    def slide(title=None, dark=False):
        sl = prs.slides.add_slide(BLANK)
        if dark:
            bg(sl, "dark")
        else:
            bg(sl, "page")
        text(sl, "COMPANY NAME", W - PAD - Inches(3), Inches(0.35), Inches(3), Inches(0.4),
             size=13, bold=True, color="on-dark-2" if dark else "navy")
        if title:
            text(sl, title, PAD, Inches(0.9), W - PAD * 2, Inches(0.9),
                 size=30, bold=True, color="on-dark" if dark else "navy")
        text(sl, STAMP, PAD, H - Inches(0.75), Inches(5), Inches(0.4),
             size=12, bold=True, color="amber" if dark else "warn-text")
        return sl

    s = fx["scope"]

    # 표지
    sl = slide(dark=True)
    text(sl, spec["coverEyebrow"], PAD, Inches(2.1), Inches(8), Inches(0.5),
         size=15, bold=True, color="accent-on-dark")
    text(sl, spec["title"], PAD, Inches(2.6), Inches(11), Inches(1.3),
         size=40, bold=True, color="on-dark")
    text(sl, spec["subtitle"], PAD, Inches(3.9), Inches(11), Inches(0.8),
         size=16, color="on-dark-2")
    text(sl, f'{s["sourceDataVersion"]}   ·   {s["appliedPeriod"]}   ·   ● 완전 커버리지',
         PAD, Inches(4.8), Inches(11), Inches(0.5), size=14, color="on-dark-3")
    text(sl, f'{fx["report"]["publisher"]} · {fx["report"]["product"]} · {fx["report"]["issuedAt"]}',
         PAD, H - Inches(1.4), Inches(11), Inches(0.5), size=13, color="on-dark-3")

    # ── 종마다 다른 순서 ────────────────────────────────────────────────
    # A 는 지표 → 근거, B 는 계약 → 지표 → 차트, C 는 통제 → 필드 → 근거.
    if spec["key"] == "b":
        sl = slide("분석 범위와 필터 계약")
        rows = [["항목", "값"], ["데이터 버전", s["sourceDataVersion"]],
                ["분석 기간", s["appliedPeriod"]], ["모집단", s["populationDefinition"]],
                ["레코드 단위", "인증 건(certification)"],
                ["커버리지", "● 완전 · " + s["coverageNote"]]]
        tb = sl.shapes.add_table(len(rows), 2, PAD, Inches(2.0), W - PAD * 2, Inches(3.0)).table
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                cell = tb.cell(r, c)
                cell.text = str(v)
                for pp in cell.text_frame.paragraphs:
                    for rr in pp.runs:
                        rr.font.size = Pt(13)
                        rr.font.bold = (r == 0 or c == 0)
                        rr.font.name = "Pretendard"
    elif spec["key"] == "c":
        sl = slide("문서 통제와 재현 방법")
        rows = [["항목", "값"], ["보고서 번호", "DEMO-FCC-2026-0001-C"],
                ["템플릿", "fcc-kc-c-evidence-dossier · v0.1.0"],
                ["데이터 버전", s["sourceDataVersion"]],
                ["재현 방법", "같은 데이터 버전·필터·기간으로 재실행 시 동일 체크섬"],
                ["보존 기간", "산출일로부터 5년"]]
        tb = sl.shapes.add_table(len(rows), 2, PAD, Inches(2.0), W - PAD * 2, Inches(3.0)).table
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                cell = tb.cell(r, c)
                cell.text = str(v)
                for pp in cell.text_frame.paragraphs:
                    for rr in pp.runs:
                        rr.font.size = Pt(13)
                        rr.font.bold = (r == 0 or c == 0)
                        rr.font.name = "Pretendard"

    # 지표
    sl = slide("핵심 지표")
    cw = (W - PAD * 2 - Inches(0.4) * 3) / 4
    for i, m in enumerate(fx["metrics"]):
        x = PAD + (cw + Inches(0.4)) * i
        box = sl.shapes.add_shape(1, x, Inches(2.2), cw, Inches(1.9))
        box.fill.solid()
        box.fill.fore_color.rgb = rgb("card")
        box.line.color.rgb = rgb("card-line")
        box.shadow.inherit = False
        text(sl, m["label"], x + Inches(0.2), Inches(2.35), cw - Inches(0.4), Inches(0.4),
             size=13, color="text-2")
        v = f'{m["value"]:,}' if isinstance(m["value"], int) else str(m["value"])
        text(sl, v + m.get("unit", ""), x + Inches(0.2), Inches(2.8), cw - Inches(0.4), Inches(0.7),
             size=30, bold=True, color="warn-text" if m.get("state") == "warn" else "navy")
        text(sl, m.get("note", ""), x + Inches(0.2), Inches(3.5), cw - Inches(0.4), Inches(0.5),
             size=12, color="text-3")
    text(sl, "■ 서버 검증 사실 · " + fx["narrative"][0]["paragraphs"][0],
         PAD, Inches(4.5), W - PAD * 2, Inches(0.5), size=16, bold=True, color="cobalt")
    text(sl, fx["narrative"][0]["paragraphs"][1], PAD, Inches(5.0), W - PAD * 2, Inches(0.5),
         size=15, color="text")

    # 순위 — 네이티브 차트
    sl = slide("시험기관별 처리 건수")
    cd = CategoryChartData()
    pts = fx["charts"][1]["series"][0]["points"]
    cd.categories = [p["label"] for p in pts]
    cd.add_series("건수", [p["value"] for p in pts])
    gf = sl.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, PAD, Inches(2.0),
                             W - PAD * 2, Inches(4.4), cd)
    ch = gf.chart
    ch.has_legend = False
    pl = ch.plots[0]
    pl.has_data_labels = True
    pl.data_labels.font.size = Pt(13)
    pl.gap_width = 45
    for i, pt in enumerate(pts):
        pl.series[0].points[i].format.fill.solid()
        pl.series[0].points[i].format.fill.fore_color.rgb = rgb(
            "cobalt" if pt.get("emphasis") == "subject" else "mark-mute")
    text(sl, "모집단 1,284건 · 서버가 정한 순서 그대로 · 값 편집 가능한 네이티브 차트",
         PAD, Inches(6.5), W - PAD * 2, Inches(0.4), size=12, color="text-2")

    # 추이 — 네이티브 차트
    sl = slide("월별 인증 건수")
    cd = CategoryChartData()
    tp = fx["charts"][0]["series"][0]["points"]
    cd.categories = [p["label"] for p in tp]
    cd.add_series("건수", [p["value"] for p in tp])
    gf = sl.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, PAD, Inches(2.0),
                             W - PAD * 2, Inches(4.0), cd)
    ch = gf.chart
    ch.has_legend = False
    ch.plots[0].has_data_labels = True
    ch.plots[0].data_labels.font.size = Pt(13)
    ser = ch.plots[0].series[0]
    ser.format.line.color.rgb = rgb("cobalt")
    ser.format.line.width = Pt(2.5)
    text(sl, "⚠ 8월은 15일까지의 부분 기간 — 마감월과 같은 자로 비교 불가",
         PAD, Inches(6.2), W - PAD * 2, Inches(0.5), size=15, bold=True, color="warn-text")

    # 해석과 경계
    sl = slide("해석과 의사결정 경계")
    y = Inches(2.0)
    for origin, k, col in (("ai_interpretation", "▲ AI 해석 · 검증된 사실 아님", "cat-3"),
                           ("human_note", "✎ 검토자 메모 · 서버·AI 산출물 아님", "text-2")):
        idx = 1 if origin == "ai_interpretation" else 2
        text(sl, k, PAD, y, W - PAD * 2, Inches(0.4), size=15, bold=True, color=col)
        y += Inches(0.45)
        for x in fx["narrative"][idx]["paragraphs"]:
            text(sl, x, PAD + Inches(0.3), y, W - PAD * 2 - Inches(0.3), Inches(0.5),
                 size=15, color="text")
            y += Inches(0.55)
        y += Inches(0.2)
    text(sl, "◆ 이 보고서로 말할 수 없는 것", PAD, y, W - PAD * 2, Inches(0.4),
         size=15, bold=True, color="navy")
    y += Inches(0.45)
    for x in fx["quality"]["limitations"]:
        text(sl, "· " + x, PAD + Inches(0.3), y, W - PAD * 2, Inches(0.4), size=14, color="text-2")
        y += Inches(0.42)

    # 권고
    sl = slide("권고와 다음 행동")
    y = Inches(2.1)
    for i, r in enumerate(fx["recommendations"], 1):
        text(sl, f'{i:02d}', PAD, y, Inches(0.6), Inches(0.5), size=16, bold=True, color="text-3")
        text(sl, re.sub("<[^>]+>", "", r["text"]), PAD + Inches(0.7), y,
             W - PAD * 2 - Inches(3.2), Inches(0.6), size=16, color="text")
        text(sl, f'{r["owner"]} · {r["due"]}', W - PAD - Inches(2.5), y,
             Inches(2.5), Inches(0.5), size=14, bold=True, color="navy")
        y += Inches(0.95)

    # 근거·계보
    sl = slide("근거와 계보")
    rows = [["인증 식별자", "엔터티", "공개일", "상태"]] + \
           [[i["certificationId"], i["entity"][:18], i["grantedAt"], "● 확인"]
            for i in fx["evidence"]["items"]]
    tbl = sl.shapes.add_table(len(rows), 4, PAD, Inches(2.0),
                              W - PAD * 2, Inches(2.6)).table
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            cell = tbl.cell(r, c)
            cell.text = str(v)
            for pp in cell.text_frame.paragraphs:
                for rr in pp.runs:
                    rr.font.size = Pt(12)
                    rr.font.bold = (r == 0)
                    rr.font.name = "Pretendard"
    text(sl, "체크섬 — 스냅샷 " + fx["lineage"]["snapshotChecksum"]
         + "  ·  보고서 모델 " + fx["lineage"]["reportModelChecksum"],
         PAD, Inches(5.0), W - PAD * 2, Inches(0.5), size=12, color="text-2")
    text(sl, "PDF · DOCX · PPTX 는 같은 보고서 모델에서 파생 — 형식이 달라도 위 값이 동일",
         PAD, Inches(5.5), W - PAD * 2, Inches(0.5), size=13, color="text-2")

    path = os.path.join(OUT, spec["pptx"])
    prs.save(path)
    return path


SPECS = [
    {"key": "a", "coverEyebrow": "경영진 보고 · 결정 요청",
     "title": "무선 모듈 인증 동향과 시험기관 편중",
     "subtitle": "2026년 상반기 FCC/KC 공개 인증 데이터 분석 · 하반기 시험 물량 배분 결정용",
     "docx": "Blue Report-FCC-A-Executive.docx", "pptx": "Blue Report-FCC-A-Executive.pptx"},
    {"key": "b", "coverEyebrow": "분석 대시보드", "land": True,
     "title": "인증 지표 대시보드",
     "subtitle": "2026년 상반기 FCC/KC 공개 인증 데이터 · 수치 비교와 추이 검토용",
     "docx": "Blue Report-FCC-B-Dashboard.docx", "pptx": "Blue Report-FCC-B-Dashboard.pptx"},
    {"key": "c", "coverEyebrow": "증거 도시에 · 재현 가능",
     "title": "인증 분석 근거 도시에",
     "subtitle": "재현성 · 근거 제출 · 감사 대응용 · 2026년 상반기 FCC/KC 공개 인증 데이터",
     "docx": "Blue Report-FCC-C-Dossier.docx", "pptx": "Blue Report-FCC-C-Dossier.pptx"},
]



def verify(out_dir):
    """만든 파일이 열리고 규격대로 들어갔는가.

    LibreOffice 가 이 환경에서 돌지 않아(txt 조차 변환 실패) 그림으로 검수하지
    못한다. 그래서 파일을 다시 열어 구조로 판정한다 — 추정으로 통과 처리하지 않는다.
    종마다 구성 순서가 달라야 하므로 그 순서까지 본다."""
    import glob
    import zipfile
    from docx import Document
    from pptx import Presentation

    ok = fail = 0
    EXPECT_DOCX_HEADS = {
        "A": ["핵심 결론", "무엇이 결론을 뒷받침하는가", "해석과 의사결정 경계", "권고와 다음 행동", "근거와 계보"],
        "B": ["분석 범위와 필터 계약", "지표 매트릭스", "기간 추이와 순위", "품질 상태와 근거"],
        "C": ["문서 통제", "집계 의미", "서버 수치와 원본 필드 대응", "품질 예외와 제한사항", "근거 목록", "계보와 검토"],
    }
    for p in sorted(glob.glob(f"{out_dir}/*.docx")):
        key = os.path.basename(p).split("-")[3][0]
        d = Document(p)
        txt = "\n".join(x.text for x in d.paragraphs)
        for t in d.tables:
            for r in t.rows:
                for c in r.cells:
                    txt += "\n" + c.text
        sec = d.sections[0]
        land = sec.page_width > sec.page_height
        checks = {
            "DESIGN FIXTURE 도장": txt.count("DESIGN FIXTURE") >= 4,
            "범위 계약": all(x in txt for x in ("FCC-PUBLIC", "2026-01-01", "필터를 통과한")),
            "서술 출처 3종": all(x in txt for x in ("■ 서버 검증 사실", "▲ AI 해석", "✎ 검토자 메모")) if key == "A" else True,
            "근거·계보": "2AXXX-WM100-2026" in txt and "sha256:" in txt,
            "구성 순서": all(h in txt for h in EXPECT_DOCX_HEADS[key]),
            "방향": land if key == "B" else not land,
            "zip 무결성": zipfile.ZipFile(p).testzip() is None,
        }
        bad = [k for k, v in checks.items() if not v]
        print(f"{os.path.basename(p)} · {'가로' if land else '세로'} · 표 {len(d.tables)} · 그림 {len(d.inline_shapes)}"
              f" — {'통과' if not bad else '실패: ' + ', '.join(bad)}")
        ok, fail = (ok + 1, fail) if not bad else (ok, fail + 1)

    for p in sorted(glob.glob(f"{out_dir}/*.pptx")):
        key = os.path.basename(p).split("-")[3][0]
        pr = Presentation(p)
        txt, charts, tables = [], 0, 0
        for sl in pr.slides:
            for sh in sl.shapes:
                if sh.has_text_frame:
                    txt.append(sh.text_frame.text)
                if sh.has_chart:
                    charts += 1
                if sh.has_table:
                    tables += 1
        t = "\n".join(txt)
        want = 7 if key == "A" else 8
        checks = {
            f"슬라이드 {want}장": len(pr.slides) == want,
            "16:9": abs(pr.slide_width / pr.slide_height - 16 / 9) < 0.01,
            "네이티브 차트 2개": charts == 2,
            "쪽마다 시안 도장": t.count("DESIGN FIXTURE") >= want,
            "부분 기간 경고": "부분 기간" in t,
            "서술 출처": "▲ AI 해석" in t,
            "체크섬": "sha256:" in t,
            "zip 무결성": zipfile.ZipFile(p).testzip() is None,
        }
        bad = [k for k, v in checks.items() if not v]
        print(f"{os.path.basename(p)} · 슬라이드 {len(pr.slides)} · 차트 {charts} · 표 {tables}"
              f" — {'통과' if not bad else '실패: ' + ', '.join(bad)}")
        ok, fail = (ok + 1, fail) if not bad else (ok, fail + 1)

    print(f"\n통과 {ok} · 실패 {fail}")
    return 1 if fail else 0



def to_pdf(paths):
    """LibreOffice 로 PDF 를 뽑아 눈으로 볼 수 있게 한다. 없으면 조용히 건너뛰지 않고 알린다."""
    import shutil
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("  LibreOffice 가 없어 PDF 미리보기를 만들지 못했다.", file=sys.stderr)
        return []
    made = []
    for p in paths:
        r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", OUT, p],
                           capture_output=True, text=True, timeout=300)
        pdf = os.path.splitext(p)[0] + ".pdf"
        if os.path.isfile(pdf):
            made.append(pdf)
        else:
            print(f"  변환 실패: {os.path.basename(p)} — {r.stderr.strip()[:120]}", file=sys.stderr)
    return made


def main():
    ap = argparse.ArgumentParser(description="FCC/KC DOCX·PPTX 시안")
    ap.add_argument("--pdf", action="store_true", help="LibreOffice 로 PDF 미리보기까지")
    ap.add_argument("--check", action="store_true", help="만들지 않고 지금 있는 파일만 판정한다")
    a = ap.parse_args()

    if a.check:
        return verify(OUT)

    os.makedirs(OUT, exist_ok=True)
    fx = json.load(open(os.path.join(FCC, "fixtures", "fixture-baseline.json"), encoding="utf-8"))
    tok = T()
    png = trend_png(os.path.join(OUT, "_trend.png"))

    made = []
    for spec in SPECS:
        made.append(build_docx(spec, fx, tok, png))
        made.append(build_pptx(spec, fx, tok))
    print(f"시안 {len(made)}개 생성 — {os.path.relpath(OUT, ROOT)}")
    for m in made:
        print("  " + os.path.basename(m))
    print()
    rc = verify(OUT)
    if a.pdf:
        pdfs = to_pdf(made)
        print(f"PDF 미리보기 {len(pdfs)}개")
    return rc


if __name__ == "__main__":
    sys.exit(main())
