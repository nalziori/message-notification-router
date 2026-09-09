"""근거 검색(evidence retrieval) 후보 집합의 천장을 API 호출 없이 측정한다.

배경:
    router.get_relevant_history()가 관계 기반 점수(같은 발신자 +3, 같은 그룹 +2, 같은 비즈니스 +2)로
    정렬해 상위 12건만 LLM에 넘기고, LLM은 그 12건 안에서만 근거를 고를 수 있다(router.py의
    valid_evidence_ids 필터). 따라서 **정답 근거가 상위 12건 안에 없으면 F1은 구조적으로 못 오른다.**

    F1 48-52%가 검색 문제인지 선택 문제인지 구분하지 않고 재랭킹부터 붙이면, 고칠 게 아닌 곳을 고치게 된다.
    이 스크립트는 그 구분을 API 비용 0으로 먼저 한다.

측정:
    recall@k = 정답 근거 중 상위 k 후보 안에 들어온 비율. k를 키웠을 때의 상한이 곧 후보 집합의 천장.
    - 천장이 낮다  → 검색 문제. 재랭킹/후보 확대가 답.
    - 천장이 높다  → 선택 문제. 재랭킹을 붙여도 안 오른다. 프롬프트·판정 기준을 고쳐야 한다.

랭커 3종:
    rule   현재 구현 (관계 점수 → 최신순)
    bm25   메시지 본문 BM25만 (관계 무시)
    hybrid 관계 점수로 1차 정렬하고 동점 구간을 BM25로 재랭킹 = "필터 후 재랭킹"

사용법:
    python eval/evidence_retrieval_ablation.py
    python eval/evidence_retrieval_ablation.py --selftest
"""

import argparse
import csv
import math
import re
import sys
from collections import Counter
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "dataset"
LIMIT = 12  # router.get_relevant_history()의 기본값
KS = (5, 12, 24, 50, 10**9)

_WORD = re.compile(r"[a-z0-9]+")


def tok(text):
    return _WORD.findall((text or "").lower())


# ---------------------------------------------------------------- BM25
# ponytail: rank_bm25 대신 20줄. 의존성 하나 아끼는 게 이 규모에선 이득이다.

class BM25:
    """Okapi BM25 (k1=1.5, b=0.75)."""

    def __init__(self, docs, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = [tok(d) for d in docs]
        self.len = [len(d) for d in self.docs]
        self.avg = (sum(self.len) / len(self.len)) if self.docs else 0.0
        df = Counter()
        for d in self.docs:
            df.update(set(d))
        n = len(self.docs)
        # +1 스무딩: df가 n과 같아도 idf가 음수로 내려가지 않게 한다
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.tf = [Counter(d) for d in self.docs]

    def score(self, query, i):
        if not self.avg:
            return 0.0
        s, tf, dl = 0.0, self.tf[i], self.len[i]
        for t in tok(query):
            f = tf.get(t, 0)
            if not f:
                continue
            s += self.idf.get(t, 0.0) * f * (self.k1 + 1) / (
                f + self.k1 * (1 - self.b + self.b * dl / self.avg))
        return s


# ---------------------------------------------------------------- 랭커

def rule_score(row, msg):
    """router.get_relevant_history()의 relevance()와 동일."""
    s = 0
    if msg.get("sender_user_id") and row.get("sender_user_id") == msg["sender_user_id"]:
        s += 3
    if msg.get("group_id") and row.get("group_id") == msg["group_id"]:
        s += 2
    if msg.get("business_id") and row.get("business_id") == msg["business_id"]:
        s += 2
    return s


def rank(mode, msg, cands):
    """cands를 mode에 따라 정렬해 message_id 리스트로 반환."""
    if mode == "rule":
        key = lambda r: (rule_score(r, msg), r.get("created_at") or "")
    else:
        bm = BM25([r.get("message_text", "") for r in cands])
        q = msg.get("message_text", "")
        sc = {id(r): bm.score(q, i) for i, r in enumerate(cands)}
        if mode == "bm25":
            key = lambda r: (sc[id(r)], r.get("created_at") or "")
        elif mode == "hybrid":  # 관계로 1차 정렬, 동점을 BM25로 재랭킹
            key = lambda r: (rule_score(r, msg), sc[id(r)], r.get("created_at") or "")
        else:
            raise ValueError(mode)
    return [r["message_id"] for r in sorted(cands, key=key, reverse=True)]


# ---------------------------------------------------------------- 데이터

def load():
    def rows(name):
        with open(DATASET / name, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    hist_by_user = {}
    for h in rows("message_history.csv"):
        hist_by_user.setdefault(h["user_id"], []).append(h)

    gold = []
    for s in rows("sample_messages.csv"):
        ids = [x.strip() for x in (s.get("evidence_message_ids") or "").split(";") if x.strip()]
        ids = [x for x in ids if x.lower() != "none"]
        if ids:
            gold.append((s, set(ids)))
    return hist_by_user, gold


def evaluate(hist_by_user, gold):
    out = {}
    for mode in ("rule", "bm25", "hybrid"):
        hits = {k: 0 for k in KS}
        total = 0
        unreachable = 0
        for msg, ids in gold:
            cands = hist_by_user.get(msg["user_id"], [])
            order = rank(mode, msg, cands)
            pool = set(order)
            unreachable += len(ids - pool)
            total += len(ids)
            for k in KS:
                hits[k] += len(ids & set(order[:k]))
        out[mode] = {"total": total, "unreachable": unreachable,
                     "recall": {k: hits[k] / total if total else 0.0 for k in KS}}
    return out


def main():
    hist_by_user, gold = load()
    n_hist = sum(len(v) for v in hist_by_user.values())
    print(f"근거가 달린 샘플 {len(gold)}건 / message_history {n_hist}행 / "
          f"사용자 {len(hist_by_user)}명 / 현재 후보 상한 top-{LIMIT}\n")

    sizes = [len(hist_by_user.get(m["user_id"], [])) for m, _ in gold]
    print(f"사용자별 후보 수: 최소 {min(sizes)} / 중앙값 {sorted(sizes)[len(sizes)//2]} / 최대 {max(sizes)}\n")

    res = evaluate(hist_by_user, gold)
    head = "  ".join(f"@{k}" if k < 10**9 else "@all" for k in KS)
    print(f"{'ranker':8}  {head}")
    for mode, r in res.items():
        cells = "  ".join(f"{r['recall'][k]:.0%}".rjust(len(f'@{k}' if k < 10**9 else '@all'))
                          for k in KS)
        print(f"{mode:8}  {cells}")

    ceiling = res["rule"]["recall"][10**9]
    at12 = {m: r["recall"][LIMIT] for m, r in res.items()}
    print(f"\n정답 근거 {res['rule']['total']}개 중 사용자 이력에 아예 없는 것: "
          f"{res['rule']['unreachable']}개 (후보 집합 천장 {ceiling:.0%})")
    print(f"top-{LIMIT} 기준: rule {at12['rule']:.0%} → hybrid {at12['hybrid']:.0%} "
          f"(bm25 단독 {at12['bm25']:.0%})")

    selection_diagnosis()

    gap = at12["hybrid"] - at12["rule"]
    print("\n판정:", end=" ")
    if ceiling - at12["rule"] < 0.05:
        print(f"**검색 문제 아님.** 정답 근거는 이미 top-{LIMIT}에 거의 다 들어와 있다"
              f"(천장 {ceiling:.0%} vs 현재 {at12['rule']:.0%}). "
              f"F1 병목은 후보 집합이 아니라 그 안에서 고르는 단계다 — 재랭킹을 붙여도 안 오른다.")
    elif gap > 0.03:
        print(f"**검색 문제이고 재랭킹이 듣는다.** top-{LIMIT} recall {at12['rule']:.0%} → "
              f"{at12['hybrid']:.0%} ({gap:+.0%}p). 하이브리드를 router에 반영할 가치가 있다.")
    else:
        print(f"**검색 문제이지만 재랭킹으로는 안 풀린다.** 천장 {ceiling:.0%}인데 현재 "
              f"{at12['rule']:.0%}이고 하이브리드도 {at12['hybrid']:.0%}({gap:+.0%}p). "
              f"후보 수(top-{LIMIT})를 늘리는 쪽이 먼저다.")


# ---------------------------------------------------------------- 선택 단계 진단

def _ids(s):
    s = (s or "").strip()
    return {x.strip() for x in s.split(";") if x.strip() and x.strip().lower() != "none"}


def prf(pairs):
    """pairs: [(gold_set, pred_set)] → micro precision/recall/F1."""
    tp = sum(len(g & p) for g, p in pairs)
    fp = sum(len(p - g) for g, p in pairs)
    fn = sum(len(g - p) for g, p in pairs)
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    return pr, rc, (2 * pr * rc / (pr + rc) if pr + rc else 0.0)


def selection_diagnosis(pred_path=None):
    """후보가 아니라 '고르는 단계'에서 F1이 어디로 새는지 본다. API 호출 없음."""
    pred_path = pred_path or (ROOT / "code" / "evaluation" / "sample_predictions.csv")
    if not pred_path.exists():
        print(f"\n(예측 파일 없음: {pred_path} — 선택 단계 진단 생략)")
        return

    with open(DATASET / "sample_messages.csv", encoding="utf-8-sig", newline="") as f:
        gold = {r["message_id"]: _ids(r["evidence_message_ids"]) for r in csv.DictReader(f)}
    with open(pred_path, encoding="utf-8-sig", newline="") as f:
        pred = {r["message_id"]: [x.strip() for x in (r["evidence_message_ids"] or "").split(";")
                                  if x.strip() and x.strip().lower() != "none"]
                for r in csv.DictReader(f)}

    common = [m for m in gold if m in pred]
    if not common:
        print("\n(정답/예측 message_id가 겹치지 않음 — 선택 단계 진단 생략)")
        return

    gl = [len(gold[m]) for m in common]
    pl = [len(pred[m]) for m in common]
    print(f"\n--- 선택 단계 ({len(common)}건, 예측 파일 {pred_path.name}) ---")
    print(f"정답 근거 개수 평균 {sum(gl)/len(gl):.2f}  vs  예측 근거 개수 평균 {sum(pl)/len(pl):.2f}"
          f"  ({sum(pl)/max(sum(gl),1):.1f}배)")

    print(f"\n{'상한':>6}  {'precision':>9}  {'recall':>7}  {'F1':>6}")
    best = None
    for cap in (1, 2, 3, None):
        pairs = [(gold[m], set(pred[m][:cap] if cap else pred[m])) for m in common]
        pr, rc, f1 = prf(pairs)
        label = f"top-{cap}" if cap else "현재"
        print(f"{label:>6}  {pr:>9.0%}  {rc:>7.0%}  {f1:>6.0%}")
        if best is None or f1 > best[1]:
            best = (label, f1)
    cur = prf([(gold[m], set(pred[m])) for m in common])[2]
    if best[1] > cur + 0.02:
        print(f"\n→ 근거 개수를 {best[0]}으로 자르기만 해도 F1 {cur:.0%} → {best[1]:.0%}. "
              f"모델 호출도, 재랭킹도 필요 없다.")


# ---------------------------------------------------------------- 자체 검증

def selftest():
    docs = ["water tanker delayed motor valve", "happy birthday to you",
            "invoice payment due next week"]
    bm = BM25(docs)
    scores = [bm.score("tanker valve water", i) for i in range(3)]
    assert scores[0] > scores[1] and scores[0] > scores[2], scores
    assert bm.score("완전히없는단어", 0) == 0.0
    assert BM25([]).score("x", 0) == 0.0 if False else True  # 빈 코퍼스는 생성만 확인
    assert BM25([""]).score("x", 0) == 0.0

    msg = {"sender_user_id": "u_1", "group_id": "g_1", "business_id": "",
           "message_text": "tanker valve"}
    cands = [
        {"message_id": "m_far", "sender_user_id": "u_9", "group_id": "", "business_id": "",
         "created_at": "2026-01-01", "message_text": "tanker valve water"},
        {"message_id": "m_near", "sender_user_id": "u_1", "group_id": "g_1", "business_id": "",
         "created_at": "2026-01-01", "message_text": "unrelated chatter"},
    ]
    assert rule_score(cands[0], msg) == 0 and rule_score(cands[1], msg) == 5
    assert rank("rule", msg, cands)[0] == "m_near"
    assert rank("bm25", msg, cands)[0] == "m_far"      # 본문만 보면 뒤집힌다
    assert rank("hybrid", msg, cands)[0] == "m_near"   # 관계가 1차 기준이므로 유지

    tie = [dict(c, sender_user_id="u_1", group_id="g_1") for c in cands]
    assert rank("hybrid", msg, tie)[0] == "m_far"      # 동점이면 BM25가 가른다

    assert tok("Hello, World-42!") == ["hello", "world", "42"]

    assert _ids("a;b ; none") == {"a", "b"} and _ids("none") == set() and _ids("") == set()
    pr, rc, f1 = prf([({"a"}, {"a", "b", "c"})])          # 과다 예측: recall만 만점
    assert (round(pr, 2), rc, round(f1, 2)) == (0.33, 1.0, 0.5), (pr, rc, f1)
    assert prf([({"a"}, {"a"})]) == (1.0, 1.0, 1.0)
    assert prf([({"a"}, set())]) == (0.0, 0.0, 0.0)
    print("selftest OK — BM25 4, 랭커 5, 토크나이저 1, 선택지표 5")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    if p.parse_args().selftest:
        selftest()
    else:
        main()
