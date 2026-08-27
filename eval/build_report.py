"""Build a self-contained HTML report of the synthetic held-out test run:
every case with its input (text/image/audio, embedded as base64 data URIs),
expected vs actual action/type, and an illustrative rule-based simulator.

Usage:
    python eval/build_report.py
Writes eval/synthetic_test_report.html
"""

import base64
import csv
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SYN_DIR = HERE / "synthetic_media"
CASES_CSV = HERE / "synthetic_cases.csv"
PRED_CSV = HERE / "synthetic_predictions.csv"
OUT_HTML = HERE / "synthetic_test_report.html"


def b64_file(path: Path) -> str:
    return base64.standard_b64encode(path.read_bytes()).decode("ascii")


def main():
    cases = {r["message_id"]: r for r in csv.DictReader(open(CASES_CSV, encoding="utf-8", newline=""))}
    preds = {r["message_id"]: r for r in csv.DictReader(open(PRED_CSV, encoding="utf-8", newline=""))}

    cards_data = []
    for mid, c in cases.items():
        p = preds.get(mid, {})
        media_html = ""
        if c["media_type"] == "image":
            img_path = SYN_DIR / "images" / f"{mid}.jpg"
            b64 = b64_file(img_path)
            media_html = f'<img class="media-thumb" src="data:image/jpeg;base64,{b64}" alt="synthetic image for {mid}">'
        elif c["media_type"] == "voice":
            wav_path = SYN_DIR / "audio" / f"{mid}.wav"
            b64 = b64_file(wav_path)
            media_html = f'<audio controls class="media-audio" src="data:audio/wav;base64,{b64}"></audio>'

        cards_data.append({
            "mid": mid,
            "conv": c["conversation_type"],
            "text": c["message_text"],
            "media_type": c["media_type"],
            "media_html": media_html,
            "exp_action": c["expected_action"],
            "exp_type": c["expected_type"],
            "act_action": p.get("action", ""),
            "act_type": p.get("message_type", ""),
            "reason": p.get("reason", ""),
            "confidence": p.get("confidence", ""),
            "action_ok": p.get("action", "") == c["expected_action"],
            "type_ok": p.get("message_type", "") == c["expected_type"],
        })

    n = len(cards_data)
    action_ok = sum(1 for c in cards_data if c["action_ok"])
    type_ok = sum(1 for c in cards_data if c["type_ok"])
    n_text = sum(1 for c in cards_data if not c["media_type"])
    n_img = sum(1 for c in cards_data if c["media_type"] == "image")
    n_voice = sum(1 for c in cards_data if c["media_type"] == "voice")

    def esc(s):
        return html.escape(s or "")

    card_blocks = []
    for c in cards_data:
        a_cls = "ok" if c["action_ok"] else "miss"
        t_cls = "ok" if c["type_ok"] else "miss"
        conf = c["confidence"]
        try:
            conf_pct = f"{float(conf) * 100:.0f}%"
        except ValueError:
            conf_pct = "-"
        input_block = f'<p class="case-text">{esc(c["text"])}</p>' if c["text"] else c["media_html"]
        card_blocks.append(f"""
        <article class="case-card">
          <header class="case-head">
            <span class="mid">{esc(c["mid"])}</span>
            <span class="conv-badge conv-{esc(c["conv"])}">{esc(c["conv"])}</span>
          </header>
          <div class="case-input">{input_block}</div>
          <div class="case-compare">
            <div class="cmp-row">
              <span class="cmp-label">action</span>
              <span class="pill action-{esc(c["exp_action"])}">exp: {esc(c["exp_action"])}</span>
              <span class="arrow">&rarr;</span>
              <span class="pill action-{esc(c["act_action"])} {a_cls}">{esc(c["act_action"])}</span>
              <span class="verdict {a_cls}">{"OK" if c["action_ok"] else "MISS"}</span>
            </div>
            <div class="cmp-row">
              <span class="cmp-label">type</span>
              <span class="pill type-pill">exp: {esc(c["exp_type"])}</span>
              <span class="arrow">&rarr;</span>
              <span class="pill type-pill {t_cls}">{esc(c["act_type"])}</span>
              <span class="verdict {t_cls}">{"OK" if c["type_ok"] else "MISS"}</span>
            </div>
          </div>
          <p class="reason">{esc(c["reason"])}</p>
          <div class="conf-row"><span>confidence</span><div class="conf-bar"><div class="conf-fill" style="width:{conf_pct}"></div></div><span class="conf-num">{conf_pct}</span></div>
        </article>""")

    html_out = TEMPLATE.format(
        n=n, action_ok=action_ok, type_ok=type_ok,
        action_pct=f"{action_ok/n*100:.0f}", type_pct=f"{type_ok/n*100:.0f}",
        n_text=n_text, n_img=n_img, n_voice=n_voice,
        cards="\n".join(card_blocks),
    )
    OUT_HTML.write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size / 1024:.0f} KB)")


TEMPLATE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>합성 테스트셋 결과 리포트</title>
<style>
:root {{
  --bg: #f5f6f8;
  --surface: #ffffff;
  --ink: #1a1d24;
  --ink-muted: #5b6270;
  --border: #e2e5ea;
  --accent: #1f6f78;
  --accent-soft: #e4f1f2;
  --ok: #2f9e6e;
  --ok-soft: #e3f6ee;
  --miss: #d6455b;
  --miss-soft: #fbe7ea;
  --notify: #e0574b;
  --digest: #c98a2e;
  --mute: #6b7280;
  --notify-soft: #fdece9;
  --digest-soft: #fbf1e1;
  --mute-soft: #eceef0;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #14171c; --surface: #1c2029; --ink: #e8eaed; --ink-muted: #9aa1ae;
    --border: #2c313b; --accent: #4fb3bd; --accent-soft: #1c3538;
    --ok: #55c795; --ok-soft: #16352a; --miss: #f0798a; --miss-soft: #3a1f24;
    --notify: #f0776a; --digest: #e0ab5c; --mute: #9aa1ae;
    --notify-soft: #3a2320; --digest-soft: #362a17; --mute-soft: #24272c;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #14171c; --surface: #1c2029; --ink: #e8eaed; --ink-muted: #9aa1ae;
  --border: #2c313b; --accent: #4fb3bd; --accent-soft: #1c3538;
  --ok: #55c795; --ok-soft: #16352a; --miss: #f0798a; --miss-soft: #3a1f24;
  --notify: #f0776a; --digest: #e0ab5c; --mute: #9aa1ae;
  --notify-soft: #3a2320; --digest-soft: #362a17; --mute-soft: #24272c;
}}
:root[data-theme="light"] {{
  --bg: #f5f6f8; --surface: #ffffff; --ink: #1a1d24; --ink-muted: #5b6270;
  --border: #e2e5ea; --accent: #1f6f78; --accent-soft: #e4f1f2;
  --ok: #2f9e6e; --ok-soft: #e3f6ee; --miss: #d6455b; --miss-soft: #fbe7ea;
  --notify: #e0574b; --digest: #c98a2e; --mute: #6b7280;
  --notify-soft: #fdece9; --digest-soft: #fbf1e1; --mute-soft: #eceef0;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: -apple-system, "Segoe UI", "Malgun Gothic", sans-serif;
  line-height: 1.5;
}}
.wrap {{ max-width: 1160px; margin: 0 auto; padding: 40px 24px 80px; }}
header.top {{ margin-bottom: 32px; }}
header.top .eyebrow {{
  font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; margin: 0 0 8px;
}}
header.top h1 {{
  font-family: Georgia, "Noto Serif KR", serif;
  font-size: 32px; margin: 0 0 10px; text-wrap: balance;
}}
header.top p {{ color: var(--ink-muted); max-width: 70ch; margin: 0; font-size: 15px; }}

.stat-bar {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px; margin: 28px 0 40px;
}}
.stat {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 16px 18px;
}}
.stat .num {{ font-size: 28px; font-weight: 700; font-variant-numeric: tabular-nums; }}
.stat .label {{ font-size: 12px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }}

section h2 {{
  font-family: Georgia, "Noto Serif KR", serif;
  font-size: 20px; margin: 0 0 16px; padding-top: 8px; border-top: 1px solid var(--border);
}}

.case-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px; margin-bottom: 48px;
}}
.case-card {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px; display: flex; flex-direction: column; gap: 10px;
}}
.case-head {{ display: flex; justify-content: space-between; align-items: center; }}
.mid {{ font-family: ui-monospace, Consolas, monospace; font-size: 12px; color: var(--ink-muted); }}
.conv-badge {{
  font-size: 11px; padding: 3px 8px; border-radius: 999px; background: var(--accent-soft);
  color: var(--accent); font-weight: 600;
}}
.case-input {{ min-height: 36px; }}
.case-text {{ margin: 0; font-size: 14px; color: var(--ink); }}
.media-thumb {{ width: 100%; max-height: 160px; object-fit: cover; border-radius: 8px; display: block; }}
.media-audio {{ width: 100%; height: 32px; }}
.case-compare {{ display: flex; flex-direction: column; gap: 6px; }}
.cmp-row {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: 12px; }}
.cmp-label {{ color: var(--ink-muted); width: 42px; text-transform: uppercase; font-size: 10px; letter-spacing: 0.04em; }}
.arrow {{ color: var(--ink-muted); }}
.pill {{
  padding: 3px 9px; border-radius: 999px; font-size: 11px; font-weight: 600;
  background: var(--mute-soft); color: var(--mute);
}}
.pill.action-notify {{ background: var(--notify-soft); color: var(--notify); }}
.pill.action-digest {{ background: var(--digest-soft); color: var(--digest); }}
.pill.action-mute {{ background: var(--mute-soft); color: var(--mute); }}
.pill.type-pill {{ background: var(--accent-soft); color: var(--accent); }}
.verdict {{ margin-left: auto; font-weight: 700; font-size: 11px; letter-spacing: 0.03em; }}
.verdict.ok {{ color: var(--ok); }}
.verdict.miss {{ color: var(--miss); }}
.reason {{ font-size: 12.5px; color: var(--ink-muted); margin: 0; }}
.conf-row {{ display: flex; align-items: center; gap: 8px; font-size: 11px; color: var(--ink-muted); }}
.conf-bar {{ flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }}
.conf-fill {{ height: 100%; background: var(--accent); }}
.conf-num {{ font-variant-numeric: tabular-nums; width: 32px; text-align: right; }}

.sim-panel {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  padding: 28px; display: grid; grid-template-columns: 1fr 1fr; gap: 28px;
}}
.sim-panel .disclaimer {{
  grid-column: 1 / -1; font-size: 12.5px; color: var(--ink-muted);
  background: var(--accent-soft); border-radius: 8px; padding: 10px 14px; margin: 0 0 4px;
}}
.sim-field {{ margin-bottom: 14px; }}
.sim-field label {{ display: block; font-size: 12px; color: var(--ink-muted); margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.03em; }}
.sim-field textarea, .sim-field select, .sim-field input[type=number] {{
  width: 100%; border: 1px solid var(--border); border-radius: 8px; padding: 9px 11px;
  font-size: 14px; background: var(--bg); color: var(--ink); font-family: inherit;
}}
.sim-field textarea {{ min-height: 72px; resize: vertical; }}
.sim-toggles {{ display: flex; flex-wrap: wrap; gap: 10px 18px; margin-bottom: 18px; }}
.sim-toggle {{ display: flex; align-items: center; gap: 6px; font-size: 13px; }}
.sim-run {{
  background: var(--accent); color: white; border: none; border-radius: 8px;
  padding: 11px 20px; font-size: 14px; font-weight: 600; cursor: pointer;
}}
.sim-run:hover {{ opacity: 0.92; }}
.sim-result {{
  border: 1px dashed var(--border); border-radius: 10px; padding: 18px;
  display: flex; flex-direction: column; gap: 12px; min-height: 100%;
}}
.sim-result .placeholder {{ color: var(--ink-muted); font-size: 13px; margin: auto; }}
.sim-result .out-row {{ display: flex; gap: 8px; align-items: center; }}
.sim-result .out-reason {{ font-size: 13px; color: var(--ink-muted); }}
.sim-result .trace {{ font-size: 12px; color: var(--ink-muted); font-family: ui-monospace, monospace; white-space: pre-wrap; }}
footer {{ margin-top: 40px; font-size: 12px; color: var(--ink-muted); }}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <p class="eyebrow">Message Notification Router &middot; Held-out Evaluation</p>
    <h1>합성 테스트셋 결과 리포트</h1>
    <p>공식 sample_messages.csv 30건과는 완전히 별개로 생성한 새 테스트 케이스 {n}건(텍스트 {n_text} / 이미지 {n_img} / 음성 {n_voice})을 실제 라우터에 통과시킨 결과입니다.
    프롬프트 튜닝에 쓰인 적 없는 데이터라, 개선이 특정 샘플에 과적합된 게 아니라 실제로 일반화되는지 확인하는 용도입니다.</p>
  </header>

  <div class="stat-bar">
    <div class="stat"><div class="num">{n}</div><div class="label">테스트 케이스</div></div>
    <div class="stat"><div class="num">{action_pct}%</div><div class="label">action 정확도 ({action_ok}/{n})</div></div>
    <div class="stat"><div class="num">{type_pct}%</div><div class="label">message_type 정확도 ({type_ok}/{n})</div></div>
    <div class="stat"><div class="num">{n_img}+{n_voice}</div><div class="label">이미지+음성 케이스</div></div>
  </div>

  <section>
    <h2>케이스별 결과</h2>
    <div class="case-grid">
      {cards}
    </div>
  </section>

  <section>
    <h2>직접 시뮬레이션해보기</h2>
    <div class="sim-panel">
      <p class="disclaimer">이 시뮬레이터는 실제 Claude API를 호출하지 않습니다. router.py 시스템 프롬프트에 반영된 판단 규칙(옵트인 vs 반복, event vs business_update, greeting vs forward 등)을 자바스크립트로 단순 재현한 것으로, 실제 모델의 추론과 다를 수 있습니다. 정확한 결과는 위 케이스들처럼 실제 API를 호출한 값입니다.</p>
      <div class="sim-inputs">
        <div class="sim-field">
          <label for="sim-text">메시지 내용</label>
          <textarea id="sim-text" placeholder="예: URGENT - your account will be suspended, reply with your OTP now">Hi, quick reminder that your appointment is scheduled for tomorrow at 4pm. Please confirm.</textarea>
        </div>
        <div class="sim-field">
          <label for="sim-conv">대화 유형</label>
          <select id="sim-conv">
            <option value="personal">personal</option>
            <option value="group">group</option>
            <option value="business" selected>business</option>
          </select>
        </div>
        <div class="sim-field">
          <label for="sim-fwd">forwarded_count</label>
          <input type="number" id="sim-fwd" value="0" min="0">
        </div>
        <div class="sim-toggles">
          <label class="sim-toggle"><input type="checkbox" id="sim-verified" checked> 발신자/비즈니스 인증됨</label>
          <label class="sim-toggle"><input type="checkbox" id="sim-optin"> 프로모션 옵트인함</label>
          <label class="sim-toggle"><input type="checkbox" id="sim-muted"> 그룹 음소거 상태</label>
          <label class="sim-toggle"><input type="checkbox" id="sim-firsttime"> 처음 보는 발신자</label>
          <label class="sim-toggle"><input type="checkbox" id="sim-reported"> 과거 유사 메시지 신고/무시 이력</label>
        </div>
        <button class="sim-run" onclick="runSim()">시뮬레이션 실행</button>
      </div>
      <div class="sim-result" id="sim-result">
        <p class="placeholder">왼쪽에 메시지와 조건을 입력하고 실행 버튼을 눌러보세요.</p>
      </div>
    </div>
  </section>

  <footer>hackerrank-orchestrate-august26 &middot; eval/synthetic_test_report.html &middot; 규칙 기반 시뮬레이터는 참고용이며 실제 채점 기준이 아닙니다.</footer>
</div>

<script>
function runSim() {{
  const text = document.getElementById('sim-text').value || '';
  const lower = text.toLowerCase();
  const conv = document.getElementById('sim-conv').value;
  const fwd = parseInt(document.getElementById('sim-fwd').value || '0', 10);
  const verified = document.getElementById('sim-verified').checked;
  const optin = document.getElementById('sim-optin').checked;
  const muted = document.getElementById('sim-muted').checked;
  const firsttime = document.getElementById('sim-firsttime').checked;
  const reported = document.getElementById('sim-reported').checked;

  const trace = [];
  const has = (words) => words.some(w => lower.includes(w));

  const scamWords = ['otp', 'suspend', 'verify your', 'card number', 'password', 'urgent action required', 'click the link', 'prize', 'congratulations'];
  const urgentWords = ['urgent', 'emergency', 'right now', 'asap', 'immediately', 'escalat'];
  const scheduleWords = ['appointment', 'scheduled', 'pickup', 'deadline', 'due', 'form', 'consent', 'timing'];
  const promoWords = ['% off', 'sale', 'discount', 'offer', 'selling', 'pickup near', 'code save', 'deal'];
  const greetingWords = ['good morning', 'good night', 'blessed', 'peaceful day', 'stay positive'];

  let type = 'personal';
  let action = 'digest';
  let confidence = 0.6;

  if (has(scamWords) && !verified) {{
    type = 'scam'; action = 'mute'; confidence = 0.9;
    trace.push('scam 키워드 감지 + 미인증 발신자 → scam/mute');
  }} else if (has(promoWords)) {{
    type = 'promotion';
    if (optin) {{ action = 'digest'; confidence = 0.75; trace.push('프로모션 키워드 + 옵트인함 → promotion/digest (반복이어도 mute 아님)'); }}
    else if (reported || (fwd > 5)) {{ action = 'mute'; confidence = 0.7; trace.push('프로모션 키워드 + 비옵트인 + 무시/신고 이력 → promotion/mute'); }}
    else {{ action = 'digest'; confidence = 0.55; trace.push('프로모션 키워드, 옵트인 정보 없음 → 기본 digest'); }}
  }} else if (has(greetingWords)) {{
    type = 'greeting'; action = muted ? 'mute' : 'digest'; confidence = 0.65;
    trace.push('인사/덕담 문구 감지 → greeting (forward 언급 있어도 내용이 인사면 greeting 우선)');
  }} else if (fwd > 3 && !has(greetingWords)) {{
    type = has(scamWords) ? 'scam' : 'forward';
    action = reported ? 'mute' : 'digest'; confidence = 0.6;
    trace.push('forwarded_count > 3, 인사 아님 → forward (개인 네트워크 체인 전달)');
  }} else if (has(scheduleWords)) {{
    type = 'event'; action = 'notify'; confidence = 0.7;
    trace.push('일정/마감 관련 키워드 → event (발신자가 business여도 event 우선)');
  }} else if (has(urgentWords)) {{
    type = 'urgent'; action = 'notify'; confidence = 0.75;
    trace.push('긴급성 키워드 감지 → urgent/notify');
  }} else if (conv === 'business') {{
    type = 'business_update'; action = verified ? 'digest' : 'mute'; confidence = 0.6;
    trace.push('일정/프로모션/긴급 신호 없는 business 메시지 → business_update, 미인증이면 mute 쪽으로');
  }} else if (firsttime) {{
    type = 'unknown'; action = 'digest'; confidence = 0.45;
    trace.push('첫 대화 상대 + 신뢰 신호 부족 → unknown/digest');
  }} else {{
    type = 'personal'; action = 'digest'; confidence = 0.55;
    trace.push('특별한 신호 없는 개인 메시지 → personal/digest 기본값');
  }}

  const el = document.getElementById('sim-result');
  el.innerHTML =
    '<div class="out-row"><span class="pill action-' + action + '">action: ' + action + '</span>' +
    '<span class="pill type-pill">type: ' + type + '</span></div>' +
    '<div class="conf-row"><span>confidence</span><div class="conf-bar"><div class="conf-fill" style="width:' + Math.round(confidence*100) + '%"></div></div>' +
    '<span class="conf-num">' + Math.round(confidence*100) + '%</span></div>' +
    '<p class="out-reason">규칙 기반 근거: ' + trace.join(' / ') + '</p>' +
    '<p class="trace">(참고용 단순화 로직 -- 실제 router.py는 사용자 이력·그룹/비즈니스 관계·미디어 분석까지 종합 판단합니다)</p>';
}}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
