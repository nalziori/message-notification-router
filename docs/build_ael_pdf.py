# -*- coding: utf-8 -*-
"""Build the Agent Execution Ledger (AEL) design doc as a PDF.

Usage:
    python docs/build_ael_pdf.py
Writes docs/AEL_ko.pdf

Mirrors the style helpers in build_report_pdf.py so this doc matches the
rest of docs/ visually (same fonts, colors, table styling).
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable,
)

HERE = Path(__file__).resolve().parent

KOREAN_FONT = "MalgunGothic"
KOREAN_FONT_BOLD = "MalgunGothic-Bold"
pdfmetrics.registerFont(TTFont(KOREAN_FONT, r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont(KOREAN_FONT_BOLD, r"C:\Windows\Fonts\malgunbd.ttf"))

ACCENT = colors.HexColor("#1f6f78")
ACCENT_DARK = colors.HexColor("#14464d")
INK = colors.HexColor("#1a1d24")
MUTED = colors.HexColor("#5b6270")
ROW_ALT = colors.HexColor("#f2f5f6")
BORDER = colors.HexColor("#d8dee0")


def make_styles():
    ss = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle("TitleX", parent=ss["Title"], fontName=KOREAN_FONT_BOLD,
                                 fontSize=22, leading=27, textColor=ACCENT_DARK, spaceAfter=4),
        "Subtitle": ParagraphStyle("SubtitleX", parent=ss["Normal"], fontName=KOREAN_FONT,
                                    fontSize=11, leading=15, textColor=MUTED, spaceAfter=18),
        "H1": ParagraphStyle("H1X", parent=ss["Heading1"], fontName=KOREAN_FONT_BOLD,
                              fontSize=15, leading=19, textColor=ACCENT_DARK, spaceBefore=18, spaceAfter=8),
        "H2": ParagraphStyle("H2X", parent=ss["Heading2"], fontName=KOREAN_FONT_BOLD,
                              fontSize=12, leading=15, textColor=INK, spaceBefore=12, spaceAfter=5),
        "Body": ParagraphStyle("BodyX", parent=ss["Normal"], fontName=KOREAN_FONT,
                                fontSize=9.5, leading=14, textColor=INK, spaceAfter=6),
        "Bullet": ParagraphStyle("BulletX", parent=ss["Normal"], fontName=KOREAN_FONT,
                                  fontSize=9.5, leading=14, textColor=INK, spaceAfter=3),
        "Caption": ParagraphStyle("CaptionX", parent=ss["Normal"], fontName=KOREAN_FONT,
                                   fontSize=8, leading=11, textColor=MUTED, spaceBefore=2, spaceAfter=10,
                                   alignment=1),
        "TableHead": ParagraphStyle("TableHeadX", parent=ss["Normal"], fontName=KOREAN_FONT_BOLD,
                                     fontSize=8.6, leading=11, textColor=colors.white),
        "TableCell": ParagraphStyle("TableCellX", parent=ss["Normal"], fontName=KOREAN_FONT,
                                     fontSize=8.4, leading=11.5, textColor=INK),
        "Mono": ParagraphStyle("MonoX", parent=ss["Normal"], fontName="Courier",
                                fontSize=7.6, leading=10.5, textColor=INK, spaceAfter=6,
                                backColor=colors.HexColor("#f5f7f7"), borderPadding=6),
    }


def p(text, style):
    return Paragraph(text, style)


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(t, style), bulletColor=ACCENT, value="bulletchar") for t in items],
        bulletType="bullet", start="\u2022", leftIndent=14, bulletFontSize=8,
    )


def hr():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceBefore=6, spaceAfter=6)


def rich_table(header, rows, styles, col_widths=None):
    data = [[Paragraph(h, styles["TableHead"]) for h in header]]
    for r in rows:
        data.append([Paragraph(str(c), styles["TableCell"]) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def mono(text, styles):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), styles["Mono"])


def content():
    S = []
    add = S.append

    add(("title", "Agent Execution Ledger (AEL) 설계 문서"))
    add(("subtitle", "Message Notification Router 프로젝트 — 에이전트 의사결정을 감사 가능하게 "
                      "기록하는 Single Source of Truth (SSOT) 구조."))

    add(("h1", "1. AEL이란 무엇인가"))
    add(("body", "AEL(Agent Execution Ledger)은 단순한 실행 로그가 아니라, 에이전트가 하나의 작업을 "
                 "처리하는 전 과정 — <b>계획(Planning) → 실행(Execution) → 근거(Evidence) → "
                 "검증(Verification) → 반성(Reflection) → 상태(State)</b> — 를 하나의 append-only "
                 "기록으로 남기는 문서/데이터 구조다. 목적은 두 가지다."))
    add(("bullets", [
        "<b>설명 가능성:</b> \u201c왜 이 메시지를 notify로 분류했는가\u201d를 사후에 정확히 역추적할 수 있다.",
        "<b>환각 방지:</b> \u201c에이전트가 했다고 주장하는 것\u201d과 \u201c실제로 검증을 통과한 것\u201d을 "
        "구조적으로 분리한다 — Verification 없이는 State가 갱신되지 않는다.",
    ]))

    add(("h1", "2. 6단계 파이프라인"))
    add(("table", (
        ["단계", "질문", "이 프로젝트에서의 의미"],
        [
            ["Planning", "무엇을 하려는가?", "이 메시지를 notify/digest/mute 중 무엇으로 분류할지 결정하기 "
             "위해 pull_context()가 어떤 컨텍스트(user/group/business/media/history)를 모을지 계획."],
            ["Execution", "실제로 뭘 했는가?", "classify_message()가 JSON 스키마로 제약된 Claude 호출을 "
             "실행 — 모델, 토큰 사용량, 성공/실패 상태를 기록."],
            ["Evidence", "그 결정의 근거는?", "evidence_message_ids로 인용된 과거 메시지, 첨부 이미지/음성 "
             "분석 결과 — 실제로 사용된 근거만 기록."],
            ["Verification", "근거가 결정을 충족하는가?", "action이 허용된 값인지, evidence_message_ids가 "
             "실제 존재하는 message_id인지, confidence가 얼마인지 자동 검증."],
            ["Reflection", "왜 이렇게 됐고, 다음은?", "router.py가 이미 계산하는 내부 판단 필드 "
             "(sender_trust, urgency_signal, risk_signal, repetition_signal) 그대로 재사용 — 실패 시 "
             "next_action=flag_for_retry로 표시."],
            ["State", "지금 무엇을 알고 있는가?", "Planning~Reflection 원본 기록은 그대로 두고, 최종 "
             "action/message_type/confidence/evidence를 압축한 체크포인트 — output.csv 한 행과 1:1 대응."],
        ]
    )))

    add(("h1", "3. 왜 이 구조가 SSOT인가"))
    add(("bullets", [
        "<b>Append-only:</b> 어떤 레코드도 수정하지 않는다. 재처리(retry-failed)는 새 State 레코드를 "
        "추가할 뿐, 이전 기록을 지우지 않는다.",
        "<b>FK 체인으로 역추적:</b> State → Reflection → Verification → Evidence → Execution → Planning "
        "순으로 message_id 하나의 전체 이력을 재구성할 수 있다.",
        "<b>기존 파이프라인과 손실 없이 통합:</b> router.py의 classify_message()가 이미 만들어내는 "
        "reason/confidence/evidence_message_ids/internal 필드를 그대로 기록하므로, 프롬프트나 라우팅 "
        "로직을 바꾸지 않고 감사 계층만 추가한다.",
        "<b>data/processed.db와 분리:</b> db.py는 매 실행마다 processed.db를 dataset/*.csv로부터 "
        "새로 만든다(원본 데이터의 읽기 전용 캐시). AEL은 별도의 data/ael.db에 저장되어 그 재빌드에 "
        "영향받지 않는다 — 에이전트가 실제로 한 일의 기록이지, 입력 데이터의 사본이 아니기 때문이다.",
    ]))

    add(("h1", "4. 구현: ael_schema.sql + ael_client.py"))
    add(("body", "<font name=\"Courier\">code/ael_schema.sql</font>은 6단계에 대응하는 6개 테이블"
                 "(ael_planning, ael_execution, ael_evidence, ael_verification, ael_reflection, "
                 "ael_state)을 정의한다. 모든 테이블은 message_id로 색인되어 있어 특정 메시지의 전체 "
                 "판단 과정을 바로 조회할 수 있다."))
    add(("body", "<font name=\"Courier\">code/ael_client.py</font>는 이 스키마에 대한 얇은 파이썬 "
                 "래퍼다 — router.classify_message()가 반환하는 record 딕셔너리와 pull_context()가 "
                 "반환하는 ctx 딕셔너리를 받아 record_cycle() 한 번 호출로 6단계를 모두 기록한다:"))
    add(("mono", "from ael_client import init_db, record_cycle\n\n"
                 "init_db()  # 최초 1회: data/ael.db 생성\n\n"
                 "# router.process_message() 안에서, classify_message() 호출 직후\n"
                 "ctx = pull_context(conn, message_row)\n"
                 "record = classify_message(message_row, conn, client)\n"
                 "record_cycle(message_row, ctx, record)"))
    add(("body", "조회는 get_cycle(message_id)로 Planning부터 State까지 한 번에 재구성할 수 있다 — "
                 "낮은 confidence로 분류된 메시지를 나중에 검토할 때, 어떤 근거와 내부 신호로 그 결정에 "
                 "도달했는지 바로 확인 가능하다."))

    add(("h1", "5. 다음 단계 (선택)"))
    add(("bullets", [
        "router.py의 process_message() 안에 record_cycle() 호출을 실제로 연결.",
        "cmd_cache_status에 AEL 기반 통계(예: next_action=flag_for_retry 건수, 평균 confidence) 추가.",
        "심사 발표 자료에서 특정 message_id 하나를 골라 get_cycle()로 전체 추론 과정을 시연 — "
        "\u201cblack box가 아니다\u201d를 코드로 증명하는 가장 직접적인 방법.",
    ]))

    return S


def build_pdf(out_path: Path):
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        topMargin=20 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
        title="Agent Execution Ledger (AEL) Design Doc",
    )
    story = []
    for kind, payload in content():
        if kind == "title":
            story.append(p(payload, styles["Title"]))
        elif kind == "subtitle":
            story.append(p(payload, styles["Subtitle"]))
            story.append(hr())
        elif kind == "h1":
            story.append(p(payload, styles["H1"]))
            story.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT, spaceAfter=6))
        elif kind == "body":
            story.append(p(payload, styles["Body"]))
        elif kind == "bullets":
            story.append(bullets(payload, styles["Bullet"]))
        elif kind == "mono":
            story.append(mono(payload, styles))
        elif kind == "table":
            header, rows = payload
            story.append(rich_table(header, rows, styles, col_widths=[24 * mm, 40 * mm, 106 * mm]))
            story.append(Spacer(1, 8))
    doc.build(story)
    print(f"Wrote {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


def main():
    build_pdf(HERE / "AEL_ko.pdf")


if __name__ == "__main__":
    main()
