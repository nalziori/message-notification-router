# -*- coding: utf-8 -*-
"""Build the "AI와 함께 에이전트를 만든 이야기" presentation deck as a landscape PDF (Korean).

Companion to docs/presentation_ko.html — same 14-slide narrative, rendered as
one slide per PDF page. Focus: how Claude/Claude Code was actually used during
development (reconstructed collaboration turns + standard-agent-architecture
comparison), not the router project's own feature set.

Usage:
    python docs/build_presentation_pdf.py
Writes docs/presentation_ko.pdf
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, PageBreak, HRFlowable,
)

HERE = Path(__file__).resolve().parent
PAGE_SIZE = landscape((338 * mm, 190 * mm))  # 16:9 widescreen slide

KOREAN_FONT = "MalgunGothic"
KOREAN_FONT_BOLD = "MalgunGothic-Bold"
pdfmetrics.registerFont(TTFont(KOREAN_FONT, r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont(KOREAN_FONT_BOLD, r"C:\Windows\Fonts\malgunbd.ttf"))

ACCENT = colors.HexColor("#1f6f78")
ACCENT_DARK = colors.HexColor("#14464d")
ACCENT_LIGHT = colors.HexColor("#e3f1f2")
AGENT_BG = colors.HexColor("#eef6f6")
HUMAN_BG = colors.HexColor("#f4f5f5")
INK = colors.HexColor("#1a1d24")
MUTED = colors.HexColor("#5b6270")
ROW_ALT = colors.HexColor("#f2f5f6")
BORDER = colors.HexColor("#d8dee0")

ss = getSampleStyleSheet()
STYLES = {
    "Eyebrow": ParagraphStyle("Eyebrow", fontName=KOREAN_FONT_BOLD, fontSize=11,
                               leading=13, textColor=ACCENT, spaceAfter=6),
    "H1": ParagraphStyle("H1", fontName=KOREAN_FONT_BOLD, fontSize=25, leading=30,
                          textColor=ACCENT_DARK, spaceAfter=10),
    "Lead": ParagraphStyle("Lead", fontName=KOREAN_FONT, fontSize=12, leading=17.5,
                            textColor=MUTED, spaceAfter=8),
    "Body": ParagraphStyle("Body", fontName=KOREAN_FONT, fontSize=10.6, leading=15,
                            textColor=INK, spaceAfter=6),
    "Bullet": ParagraphStyle("Bullet", fontName=KOREAN_FONT, fontSize=10.6, leading=15,
                              textColor=INK, spaceAfter=5),
    "CardTitle": ParagraphStyle("CardTitle", fontName=KOREAN_FONT_BOLD, fontSize=11.5,
                                 leading=14, textColor=ACCENT_DARK, spaceAfter=4),
    "CardBody": ParagraphStyle("CardBody", fontName=KOREAN_FONT, fontSize=9.6,
                                leading=13.5, textColor=MUTED),
    "TableHead": ParagraphStyle("TableHead", fontName=KOREAN_FONT_BOLD, fontSize=9.3,
                                 leading=12, textColor=colors.white),
    "TableCell": ParagraphStyle("TableCell", fontName=KOREAN_FONT, fontSize=9,
                                 leading=12.6, textColor=INK),
    "TableCellStrong": ParagraphStyle("TableCellStrong", fontName=KOREAN_FONT_BOLD, fontSize=9,
                                       leading=12.6, textColor=ACCENT_DARK),
    "StatNum": ParagraphStyle("StatNum", fontName=KOREAN_FONT_BOLD, fontSize=18,
                               leading=21, textColor=ACCENT_DARK),
    "StatLabel": ParagraphStyle("StatLabel", fontName=KOREAN_FONT, fontSize=8.3,
                                 leading=11, textColor=MUTED),
    "PageNum": ParagraphStyle("PageNum", fontName=KOREAN_FONT, fontSize=8.5,
                               textColor=MUTED, alignment=2),
    "TagCenter": ParagraphStyle("TagCenter", fontName=KOREAN_FONT_BOLD, fontSize=9.3,
                                 leading=12, textColor=colors.white, alignment=1),
    "StepNum": ParagraphStyle("StepNum", fontName=KOREAN_FONT_BOLD, fontSize=10,
                               textColor=ACCENT_DARK, alignment=1),
    "StepTitle": ParagraphStyle("StepTitle", fontName=KOREAN_FONT_BOLD, fontSize=10.3,
                                 leading=13, textColor=INK, spaceAfter=2),
    "StepBody": ParagraphStyle("StepBody", fontName=KOREAN_FONT, fontSize=9,
                                leading=12.5, textColor=MUTED),
    "WhoHuman": ParagraphStyle("WhoHuman", fontName=KOREAN_FONT_BOLD, fontSize=8.6,
                                textColor=MUTED, alignment=2),
    "WhoAgent": ParagraphStyle("WhoAgent", fontName=KOREAN_FONT_BOLD, fontSize=8.6,
                                textColor=ACCENT_DARK, alignment=2),
    "BubbleBody": ParagraphStyle("BubbleBody", fontName=KOREAN_FONT, fontSize=9.6,
                                  leading=14, textColor=INK),
    "Takeaway": ParagraphStyle("Takeaway", fontName=KOREAN_FONT, fontSize=9.2,
                                leading=13, textColor=MUTED),
    "Notice": ParagraphStyle("Notice", fontName=KOREAN_FONT, fontSize=8.2,
                              leading=11.5, textColor=MUTED),
    "Big": ParagraphStyle("Big", fontName=KOREAN_FONT_BOLD, fontSize=16, leading=22,
                           textColor=INK, spaceAfter=12),
}


def p(text, style="Body"):
    return Paragraph(text, STYLES[style] if isinstance(style, str) else style)


def bullets(items, style="Bullet"):
    return ListFlowable(
        [ListItem(p(t, style), bulletColor=ACCENT, value="bulletchar") for t in items],
        bulletType="bullet", start="\u2022", leftIndent=14, bulletFontSize=8, spaceBefore=2,
    )


def hr(color=BORDER, thickness=0.8):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=10)


def cards(items, col_widths):
    """items: list of (title, body-or-list) -> single-row table of boxed cards.
    body may be a str (paragraph) or a list of str (bullet list)."""
    cell = []
    for title, body in items:
        content = bullets(body, "CardBody") if isinstance(body, list) else p(body, "CardBody")
        inner = Table([[p(title, "CardTitle")], [content]], colWidths=[None])
        inner.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 1), (-1, 1), 0),
        ]))
        cell.append(inner)
    t = Table([cell], colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ROW_ALT),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("LINEAFTER", (0, 0), (-2, 0), 0.7, BORDER),
    ]))
    return t


def stat_row(items, col_widths):
    num_row = [p(n, "StatNum") for n, _ in items]
    lab_row = [p(l, "StatLabel") for _, l in items]
    t = Table([num_row, lab_row], colWidths=col_widths)
    t.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
        ("LINEBELOW", (0, 0), (-1, 1), 0.7, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ]))
    return t


def arch_steps(items):
    """items: list of (num, title, body) -> vertical numbered list."""
    rows = []
    for num, title, body in items:
        badge = Table([[p(num, "StepNum")]], colWidths=[9 * mm], rowHeights=[9 * mm])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), ACCENT_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.7, ACCENT),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        rows.append([badge, [p(title, "StepTitle"), p(body, "StepBody")]])
    t = Table(rows, colWidths=[11 * mm, 260 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def convo(turns):
    """turns: list of (role, text) where role is 'human' or 'agent'."""
    rows = []
    for role, text in turns:
        if role == "human":
            who = p("사람", "WhoHuman")
            bubble_style = TableStyle([("BACKGROUND", (0, 0), (-1, -1), HUMAN_BG),
                                        ("BOX", (0, 0), (-1, -1), 0.6, BORDER)])
        else:
            who = p("Claude", "WhoAgent")
            bubble_style = TableStyle([("BACKGROUND", (0, 0), (-1, -1), AGENT_BG),
                                        ("BOX", (0, 0), (-1, -1), 0.6, ACCENT)])
        bubble = Table([[p(text, "BubbleBody")]], colWidths=[220 * mm])
        bubble.setStyle(TableStyle([
            *bubble_style.getCommands(),
            ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        rows.append([who, bubble])
    t = Table(rows, colWidths=[24 * mm, 230 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def slide_header(eyebrow, title, num, total):
    head = Table([[p(eyebrow, "Eyebrow"), p(f"{num:02d} / {total}", "PageNum")]],
                  colWidths=[280 * mm, 30 * mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return [head, p(title, "H1"), hr()]


TOTAL = 14


def build_slides():
    S = []

    # 1. Title
    s = []
    s.append(Spacer(1, 16 * mm))
    s.append(p("HACKERRANK ORCHESTRATE · 2026년 8월 — AI 활용 개발기", "Eyebrow"))
    s.append(p("AI와 함께 에이전트를 만든 이야기", ParagraphStyle(
        "TitleBig", fontName=KOREAN_FONT_BOLD, fontSize=32, leading=38, textColor=ACCENT_DARK, spaceAfter=14)))
    s.append(p("메시지 알림 라우터가 <b>무엇인지</b>보다, Claude와 <b>어떻게</b> 협업해 그것을 만들었는지에 초점을 맞춘 발표. "
                "표준 AI 에이전트 아키텍처와 실제 우리가 만든 시스템을 비교하고, 8번의 반복에서 사람과 Claude가 실제로 "
                "주고받은 판단의 흐름을 재구성한다.", "Lead"))
    s.append(Spacer(1, 8 * mm))
    tags = Table([[p("8번의 반복", "TagCenter"), p("표준 아키텍처 대응·차이", "TagCenter"), p("협업 흐름 재구성", "TagCenter")]],
                 colWidths=[75 * mm, 95 * mm, 90 * mm])
    tags.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    s.append(tags)
    S.append(s)

    # 2. Framing
    s = slide_header("이 발표가 다루는 것", "프로젝트 결과보다, 협업 과정", 2, TOTAL)
    s.append(cards([
        ("간단히만 다룬다", [
            "메시지 알림 라우터가 정확히 무엇을 하는 시스템인지",
            "파이프라인의 세부 구현(캐싱, 재시도 등)",
            "최종 정확도 수치 — 부록으로만 언급",
        ]),
        ("핵심으로 다룬다", [
            "Claude와 실제로 어떤 판단·대화가 오갔는가",
            "표준 AI 에이전트 아키텍처와 비교했을 때 무엇이 대응되고, 무엇이 다르거나 추가됐는가",
            "8번의 피드백 루프에서 사람과 Claude가 각각 무엇을 맡았는가",
        ]),
    ], [140 * mm, 140 * mm]))
    S.append(s)

    # 3. Project in one slide
    s = slide_header("프로젝트, 한 장으로", "무엇을 만들었나 (압축)", 3, TOTAL)
    s.append(p("WhatsApp 메시지를 수신자별로 notify(즉시)/digest(나중에)/mute(억제)로 개인화 라우팅하는 시스템.", "Lead"))
    flow = Table([[p("로컬 전처리", "CardTitle"), p("→", "Body"), p("컨텍스트 조립", "CardTitle"),
                   p("→", "Body"), p("Claude Sonnet 5", "CardTitle"), p("→", "Body"),
                   p("검증·fallback", "CardTitle"), p("→", "Body"), p("output.csv", "CardTitle")]],
                 colWidths=[52 * mm, 8 * mm, 52 * mm, 8 * mm, 52 * mm, 8 * mm, 52 * mm, 8 * mm, 45 * mm])
    flow.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    s.append(flow)
    s.append(Spacer(1, 10 * mm))
    s.append(p("이 파이프라인 자체보다 — 이걸 <b>어떻게 Claude와 함께 설계했는지</b>가 이 발표의 본론이다.", "Body"))
    S.append(s)

    # 4. Standard agent architecture
    s = slide_header("참고 모델", "표준 AI 에이전트 아키텍처", 4, TOTAL)
    s.append(p("널리 쓰이는 LLM 에이전트 설계를 6개 요소로 정리하면 대략 이렇다 — 이후 슬라이드에서 우리 시스템과 하나씩 대응시킨다.", "Lead"))
    s.append(arch_steps([
        ("1", "지각 (Perception)", "원시 입력(텍스트·이미지·음성 등)을 모델이 다룰 수 있는 형태로 정규화"),
        ("2", "기억 (Memory)", "단기 작업 컨텍스트 + 장기/외부 지식에 대한 검색"),
        ("3", "계획·추론 (Planning / Reasoning)", "목표를 하위 작업으로 분해하고, 사고 과정을 명시화"),
        ("4", "도구 사용·행동 (Tool Use / Action)", "외부 API·DB·코드 실행으로 환경에 직접 개입"),
        ("5", "관찰 → 재계획 (Observe → Replan)", "행동 결과를 보고 다음 스텝을 결정, 목표 달성까지 반복하는 루프"),
        ("6", "출력·자기평가 (Output / Self-eval)", "최종 산출물 생성 + 피드백으로 스스로 개선"),
    ]))
    S.append(s)

    # 5. Mapping table
    s = slide_header("대응표", "표준 요소 ↔ 우리가 만든 시스템", 5, TOTAL)
    header = [p("표준 요소", "TableHead"), p("우리 시스템의 대응", "TableHead"), p("비고", "TableHead")]
    rows = [
        ["1. 지각", "image_pipeline.py / audio_pipeline.py — OCR·설명, 음성 전사", "표준과 거의 동일"],
        ["2. 기억", "db.py(SQLite) + pull_context()의 규칙 기반 검색(발신자>그룹>비즈니스>최신순)",
         "임베딩 대신 설명 가능한 휴리스틱으로 대체 — 데이터 규모가 작아 충분"],
        ["3. 계획·추론", "내부 스키마 필드(sender_trust 등)를 최종 판단 전에 강제로 채움",
         "자유형식 Thought 대신 카테고리형 필드로 구조화"],
        ["4. 도구 사용", "없음 — LLM은 이미 조립된 컨텍스트에 대해 1회 분류만 수행", "가장 큰 차이 — 다음 슬라이드"],
        ["5. 관찰→재계획", "런타임엔 없음(재시도만); 개발 단계에서 사람+Claude가 8회 수행",
         "루프의 위치가 inference-time이 아니라 build-time"],
        ["6. 출력·자기평가", "to_output_row() + code/evaluation/ 자동 채점 하네스", "대응되지만 오프라인 배치 평가"],
    ]
    data = [header] + [[p(r[0], "TableCellStrong"), p(r[1], "TableCell"), p(r[2], "TableCell")] for r in rows]
    t = Table(data, colWidths=[35 * mm, 155 * mm, 90 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    s.append(t)
    S.append(s)

    # 6. Biggest difference
    s = slide_header("가장 큰 차이", "런타임에 자율 도구 호출 루프가 없다", 6, TOTAL)
    s.append(p("표준 에이전트는 실행 중 LLM이 스스로 어떤 도구를 쓸지 고르고, 결과를 보고, 다시 판단하는 다단계 루프(ReAct류)를 "
                "돈다. 우리 라우터는 그렇게 하지 않았다 — 도구 호출(DB 조회, 미디어 분석)을 LLM 호출 <b>이전에</b> 결정론적 "
                "파이프라인이 전부 끝내고, LLM은 이미 조립된 컨텍스트에 대해 딱 한 번, JSON 스키마로 제약된 분류만 한다.", "Lead"))
    s.append(Spacer(1, 6 * mm))
    box = Table([[p("<b>왜 자유도를 뺐는가:</b> 같은 입력엔 같은 종류의 근거로 판단해야 하는 신뢰성, 무엇을 보고 판단했는지 항상 "
                     "재현 가능해야 하는 평가 가능성, 메시지당 여러 번의 도구 호출 대신 파이프라인 1회+LLM 호출 1회로 끝내는 "
                     "비용/지연, 그리고 결정론적 동작을 요구하는 제출 규약 — 이 네 가지 때문에 의도적으로 자유 루프를 "
                     "배제했다.", "Body")]], colWidths=[280 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AGENT_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("TOPPADDING", (0, 0), (-1, -1), 14), ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 18), ("RIGHTPADDING", (0, 0), (-1, -1), 18),
    ]))
    s.append(box)
    S.append(s)

    # 7. Transition — the real loop
    s = slide_header("그런데", "진짜 에이전트 루프는 다른 곳에 있었다", 7, TOTAL)
    s.append(p("표준 아키텍처 5번, <b>관찰 → 재계획 루프</b>가 사라진 게 아니라 — <b>런타임이 아니라 개발 타임</b>으로 "
                "옮겨갔다.", "Big"))
    s.append(p("사람이 결과를 <b>관찰</b>하고 → 무엇을 할지 <b>계획</b>하면 → Claude Code가 원인을 조사하고 <b>실행</b>하고 → "
                "평가 하네스로 <b>검증</b>하고 → 반영하거나 <b>롤백</b>한다. 이 루프를 8번 돌렸다.", "Lead"))
    s.append(Spacer(1, 10 * mm))
    s.append(p("다음 슬라이드들은 CLAUDE.ko.md에 기록된 실제 반복·의사결정 로그를 사람–Claude 대화 형식으로 재구성한 것이며, "
                "원문 채팅 로그 그대로의 캡처는 아니다.", "Notice"))
    S.append(s)

    # 8-12: conversation reconstructions
    convos = [
        ("협업 흐름 · 반복 1", "버그를 스스로 발견하고 고치다", [
            ("human", "\u201croute --limit 3로 먼저 작게 테스트해보자.\u201d"),
            ("agent", "실행 결과 0/3, 그것도 비정상적으로 빨리 끝난 걸 스스로 이상하게 여김 → 로그 확인 → "
                      "<b>ThreadPoolExecutor 워커들이 SQLite 커넥션 하나를 공유</b>하고 있던 게 원인임을 특정 → 워커마다 "
                      "자기 커넥션을 열도록 수정 → 재실행 3/3 성공을 보고."),
        ], "사람은 \u201c작게 먼저 테스트하자\u201d는 방향만 줬고, 원인 조사부터 수정까지는 Claude가 스스로 수행했다."),
        ("협업 흐름 · 반복 3", "채점이 이상하다는 걸 스스로 알아채다", [
            ("human", "\u201c30건 정답 세트 기준으로 채점해줘.\u201d"),
            ("agent", "채점 결과가 <b>0/30</b>으로 나오는 걸 이상하게 여김 → id 체계를 조사해 sample_messages.csv"
                      "(sample_msg_*)와 messages.csv(msg_*)가 서로 다른 네임스페이스임을 발견 → 채점 스크립트를 "
                      "sample_messages.csv 자신의 입력으로 라우터를 직접 돌리는 방식으로 재작성 → 기준선 action 90% · "
                      "type 63% · F1 49%를 보고."),
        ], "겉보기엔 사소한 채점 스크립트 문제였지만, \u201c결과가 이상하다\u201d를 감지하고 끝까지 원인을 추적한 건 Claude였다."),
        ("협업 흐름 · 반복 5", "사람이 방향을 주면, Claude가 근거를 찾는다", [
            ("human", "\u201cmessage_type 정확도(63%)가 낮은데, 이거 개선해줘.\u201d"),
            ("agent", "혼동행렬을 만들어 오답이 어디 몰려있는지 확인 → <b>event / promotion / greeting</b> 카테고리의 "
                      "실제 오답 텍스트를 전부 정독 → 이 데이터셋만의 분류 관습 4가지를 규칙으로 도출·반영 → "
                      "<b>63%→90%</b> 개선을 보고."),
        ], "사람은 \u201c무엇을\u201d 개선할지 지정했고, \u201c어떻게\u201d(원인 진단과 일반화 가능한 규칙 도출)는 Claude의 몫이었다."),
        ("협업 흐름 · 반복 7", "사람이 패턴을 보고, Claude가 구조로 만든다", [
            ("human", "\u201c정답이 digest인데 notify로 틀린 경우가 많고, 틀린 답들의 confidence가 낮아 보여 — 이거 "
                      "활용할 수 없을까?\u201d"),
            ("agent", "실측으로 확인(정답 평균 confidence 0.85 vs 오답 0.70) → 최종 판단 전에 반드시 채워야 하는 "
                      "<b>내부 전용 스키마 필드 5개</b> 설계·구현 + \u201c애매하면 digest 기본값\u201d 규칙 추가 → 이전 "
                      "오답 7건만 먼저 저비용 검증(3건 수정 확인) → 30건 전체로 재확인 → <b>86.67%→93.33%</b>를 보고."),
        ], "사람의 관찰(패턴)을 Claude가 구체적인 스키마 설계로 번역했다."),
        ("협업 흐름 · 반복 8", "실패를 스스로 인정하고 되돌리다", [
            ("human", "\u201ctype_candidates에 각 후보를 뒷받침하는 실제 문구(key_phrase)도 추출하게 해보면 어떨까?\u201d"),
            ("agent", "구현 → 30건으로 검증 → <b>93.33%→86.67%</b>로 퇴보한 것을 스스로 확인 → 개선이 아니라 퇴보라고 "
                      "먼저 보고하고, 반복 7 상태로 즉시 되돌림 → 110건 재분류."),
        ], "그럴듯한 제안도 측정 없이 채택하지 않는다 — Claude가 스스로 반박 근거를 찾아 되돌린 사례."),
    ]
    for i, (eyebrow, title, turns, takeaway) in enumerate(convos):
        s = slide_header(eyebrow, title, 8 + i, TOTAL)
        s.append(convo(turns))
        s.append(Spacer(1, 6 * mm))
        s.append(p(takeaway, "Takeaway"))
        S.append(s)

    # 13. Role split
    s = slide_header("역할 분담", "사람이 한 일 / Claude가 한 일", 13, TOTAL)
    s.append(cards([
        ("사람이 한 일", [
            "결과를 직접 읽고 패턴을 발견 (digest→notify 편향, confidence–정확도 상관관계)",
            "개선 방향과 우선순위 제시 (\u201cmessage_type 정확도부터 고쳐줘\u201d)",
            "제안된 다음 아이디어를 승인 (key_phrase 확장)",
        ]),
        ("Claude가 한 일", [
            "버그·이상 신호를 스스로 감지하고 원인을 끝까지 조사",
            "가설을 구조(스키마·규칙)로 구현하고 측정으로 검증",
            "퇴보를 스스로 확인하고 먼저 보고한 뒤 즉시 롤백",
        ]),
    ], [140 * mm, 140 * mm]))
    S.append(s)

    # 14. Conclusion
    s = slide_header("결론", "이 협업에서 배운 것", 14, TOTAL)
    s.append(p("가장 중요한 산출물은 <i>output.csv</i>가 아니라, \u201c관찰→가설→구현→검증→반영or롤백\u201d을 8번 반복한 "
                "<i>개발 루프 그 자체</i>였다.", "Big"))
    s.append(p("표준 에이전트 아키텍처가 설명하는 자율 루프를, 이 프로젝트는 런타임 대신 <b>Claude Code와의 협업</b>이라는 "
                "형태로 개발 타임에 구현한 셈이다.", "Lead"))
    s.append(Spacer(1, 8 * mm))
    s.append(stat_row([("93.33%", "action 정확도 (부록)"), ("93.33%", "message_type 정확도 (부록)"),
                        ("110/110", "output.csv 행 (부록)")], [90 * mm, 90 * mm, 90 * mm]))
    S.append(s)

    return S


def build_pdf(out_path: Path):
    doc = SimpleDocTemplate(
        str(out_path), pagesize=PAGE_SIZE,
        topMargin=14 * mm, bottomMargin=12 * mm, leftMargin=17 * mm, rightMargin=17 * mm,
        title="AI-와-함께-에이전트를-만든-이야기 - Message Notification Router",
    )
    story = []
    slides = build_slides()
    for i, slide in enumerate(slides):
        story.extend(slide)
        if i < len(slides) - 1:
            story.append(PageBreak())
    doc.build(story)
    print(f"Wrote {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


def main():
    build_pdf(HERE / "presentation_ko.pdf")


if __name__ == "__main__":
    main()
