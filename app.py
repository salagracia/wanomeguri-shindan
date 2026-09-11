"""
わの巡り診断 Webアプリ（Flask）v1.1

構成:
- GET  /              : 診断アプリ本体（static/index.html）を配信
- POST /api/submit    : メールアドレス入力時に呼ばれる。
                        サラさんへ管理者通知（リード記録）のみ送信。
- POST /api/send-pdf  : 結果表示後、ブラウザが生成したPDFを受け取り、
                        お客様へ「診断結果PDF添付メール」を送信。

環境変数（Render に設定済みのものを再利用）:
  RESEND_API_KEY     Resend の APIキー
  FROM_EMAIL         送信元（独自ドメイン認証前は onboarding@resend.dev）
  FROM_NAME          （旧・未使用）Renderに旧チャンネル名が残っているため参照しない。送信者名は REBOOT_FROM_NAME（既定「REBOOT 山岡サラ」）
  ADMIN_EMAIL        管理者メール（デフォルト: monthly@salagracia.com）
  ADMIN_FROM_EMAIL   管理者通知の送信元（未設定なら FROM_EMAIL）

旧「信頼される男の流儀 5タイプ診断」(Streamlit) は git 履歴に保存されています。
"""
import os
from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify, send_from_directory

try:
    import resend
except ImportError:
    resend = None

try:
    from calculations.seimei_handan import seimei_handan, KANJI_KAKUSU, KANA_KAKUSU
except Exception:
    seimei_handan = None
    KANJI_KAKUSU, KANA_KAKUSU = {}, {}

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # PDF添付アップロード用に30MBまで許可

JST = timezone(timedelta(hours=9))

GENDER_LABELS = {
    "male": "男性",
    "female": "女性",
    "unspecified": "回答なし",
}


def _resend_ready():
    api_key = os.environ.get("RESEND_API_KEY", "")
    if resend and api_key:
        resend.api_key = api_key
        return True
    return False


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/health")
def health():
    return "ok"


APP_NAME = "REBOOT現在地診断"
# 送信者名。Render の FROM_NAME は旧チャンネル名（信頼される男の流儀）のまま残っているため参照しない。
SENDER_NAME = os.environ.get("REBOOT_FROM_NAME", "REBOOT 山岡サラ")
PAYMENT_URL = os.environ.get("CONSULT_PAYMENT_URL", "https://square.link/u/B7I7bZ8r")  # 個別相談3,300円（Square）


def _scores_text(scores):
    return "\n".join(f"  {k}: {v}点" for k, v in (scores or {}).items()) or "  （未取得）"


@app.route("/api/submit", methods=["POST"])
def submit():
    """18問回答完了時に呼ばれる。管理者通知（リード記録）のみ。"""
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    primary = (data.get("primary") or "").strip()
    secondary = (data.get("secondary") or "").strip()
    scores = data.get("scores") or {}

    if _resend_ready():
        from_email = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
        admin_from = os.environ.get("ADMIN_FROM_EMAIL", from_email)
        admin_email = os.environ.get("ADMIN_EMAIL", "monthly@salagracia.com")
        now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
        try:
            resend.Emails.send({
                "from": f"{APP_NAME} <{admin_from}>",
                "to": [admin_email],
                "subject": f"【{APP_NAME}】診断完了: {name or '名前未入力'} / {primary}",
                "text": (
                    f"{APP_NAME}で新しい診断が完了しました。\n\n"
                    f"日時　　　　: {now}\n"
                    f"お名前　　　: {name or '未入力'}\n"
                    f"一番のブレーキ: {primary}\n"
                    f"次に向き合うもの: {secondary}\n"
                    f"4タイプスコア:\n{_scores_text(scores)}\n"
                ),
            })
        except Exception:
            pass

    return jsonify({"ok": True})


@app.route("/api/consult", methods=["POST"])
def consult():
    """結果ページの「個別相談を申し込む」から呼ばれる。
    ① サラさんへ申込通知（診断結果つき） ② 申込者へ受付メール（自動返信）。"""
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    line_name = (data.get("line_name") or "").strip()
    preferred = (data.get("preferred") or "").strip()
    note = (data.get("note") or "").strip()
    primary = (data.get("primary") or "").strip()
    secondary = (data.get("secondary") or "").strip()
    scores = data.get("scores") or {}

    if not email or "@" not in email:
        return jsonify({"ok": False, "error": "email required"}), 400
    if not _resend_ready():
        return jsonify({"ok": False, "error": "mail not configured"}), 500

    from_email = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
    from_name = SENDER_NAME
    admin_from = os.environ.get("ADMIN_FROM_EMAIL", from_email)
    admin_email = os.environ.get("ADMIN_EMAIL", "monthly@salagracia.com")
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")

    admin_ok = False
    try:
        resend.Emails.send({
            "from": f"{APP_NAME} <{admin_from}>",
            "to": [admin_email],
            "reply_to": email,
            "subject": f"【個別相談 申込】{name or '名前未入力'}さん / {primary}",
            "text": (
                "REBOOT現在地診断から、個別相談（3,300円）の申込がありました。\n"
                "本人にはSquareのお支払いリンクを案内済みです。決済後はSquare側で日程を選んでもらい、Googleカレンダーに自動登録されます。\n"
                "カレンダーに予約が入ったら、この申込内容と診断結果を見て相談の準備をしてください。\n\n"
                f"日時　　　　: {now}\n"
                f"お名前　　　: {name or '未入力'}\n"
                f"メール　　　: {email}\n"
                f"LINE表示名　: {line_name or '未入力'}\n"
                f"困っていること: {note or '未入力'}\n\n"
                f"一番のブレーキ: {primary}\n"
                f"次に向き合うもの: {secondary}\n"
                f"4タイプスコア:\n{_scores_text(scores)}\n"
            ),
        })
        admin_ok = True
    except Exception:
        admin_ok = False

    try:
        resend.Emails.send({
            "from": f"{from_name} <{from_email}>",
            "to": [email],
            "subject": "【REBOOT】個別相談のお申込を受け付けました",
            "text": (
                f"{name or 'あなた'}さん\n\n"
                "REBOOT現在地診断から、個別相談のお申込をいただきありがとうございます。\n\n"
                "まだお支払いがお済みでない場合は、下のリンクからお願いします（3,300円）。\n"
                f"{PAYMENT_URL}\n\n"
                "お支払いが完了すると、そのまま画面で相談の日時を選べます。\n"
                "選んだ日時は自動で予約確定となり、確認メールが届きます。\n\n"
                "【お申込内容】\n"
                f"一番のブレーキ: {primary}\n"
                f"困っていること: {note or '未入力'}\n\n"
                "ここまで来たあなたは、もう「いつか」の人ではありません。\n"
                "当日、お話しできるのを楽しみにしています。\n\n"
                "REBOOT　山岡サラ\n"
            ),
        })
    except Exception:
        pass

    return jsonify({"ok": admin_ok})


@app.route("/api/seimei", methods=["POST"])
def seimei():
    """本名（漢字）入力時のみ呼ばれる。姓名判断（五格・数霊・三才）を返す。"""
    data = request.get_json(force=True, silent=True) or {}
    sei = (data.get("sei") or "").strip()
    mei = (data.get("mei") or "").strip()
    if not (seimei_handan and sei and mei):
        return jsonify({"ok": False})
    try:
        result = seimei_handan(sei, mei)
        # 画数辞書にない文字が含まれる場合は「概算」フラグを立てる（誠実な注記のため）
        unknown = [c for c in (sei + mei)
                   if c.strip() and c not in KANJI_KAKUSU and c not in KANA_KAKUSU]
        return jsonify({"ok": True, "result": result, "approx": bool(unknown)})
    except Exception:
        return jsonify({"ok": False})


@app.route("/api/send-pdf", methods=["POST"])
def send_pdf():
    """結果表示後にブラウザから自動で呼ばれる。診断結果PDFを管理者（サラさん）へ送信。
    メールアドレスは収集していないため、お客様への送信は行わない。"""
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    name = (data.get("name") or "").strip()
    type_name = (data.get("type") or "").strip()
    pdf_b64 = (data.get("pdf_base64") or "").strip()

    if not (_resend_ready() and pdf_b64):
        return jsonify({"ok": False})

    from_email = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
    from_name = SENDER_NAME
    today = datetime.now(JST).strftime("%Y-%m-%d")
    admin_email = os.environ.get("ADMIN_EMAIL", "monthly@salagracia.com")

    params = {
        "from": f"{from_name} <{from_email}>",
        "to": [email] if email else [admin_email],
        "subject": f"【{APP_NAME}】診断結果PDF: {name or '名前未入力'} / {type_name}",
        "text": (
            f"{APP_NAME}が完了しました。\n\n"
            f"お名前　　　: {name or '未入力'}\n"
            f"一番のブレーキ: {type_name}\n\n"
            "詳しい結果はPDFを添付しています。\n"
        ),
        "attachments": [{
            "filename": f"REBOOT現在地診断_{today}.pdf",
            "content": pdf_b64,
        }],
    }
    if email and admin_email and admin_email != email:
        params["bcc"] = [admin_email]

    try:
        resend.Emails.send(params)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
