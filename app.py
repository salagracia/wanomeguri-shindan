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
  FROM_NAME          送信者名（未設定なら「わの巡り診断」）
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


@app.route("/api/submit", methods=["POST"])
def submit():
    """30問回答完了時に呼ばれる。管理者通知（リード記録）のみ。メール未収集でも通知する。"""
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    name = (data.get("name") or "").strip()
    gender = GENDER_LABELS.get(data.get("gender"), "回答なし")
    birthday = (data.get("birthday") or "").strip()
    industry = (data.get("industry") or "").strip()
    revenue = (data.get("revenue") or "").strip()
    employees = (data.get("employees") or "").strip()
    worry = (data.get("worry") or "").strip()
    primary = (data.get("primary") or "").strip()
    secondary = (data.get("secondary") or "").strip()
    scores = data.get("scores") or {}

    if _resend_ready():
        from_email = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
        admin_from = os.environ.get("ADMIN_FROM_EMAIL", from_email)
        admin_email = os.environ.get("ADMIN_EMAIL", "monthly@salagracia.com")
        now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
        scores_text = "\n".join(f"  {k}: {v}点" for k, v in scores.items()) if scores else "  （未取得）"
        try:
            resend.Emails.send({
                "from": f"業績アップ診断 <{admin_from}>",
                "to": [admin_email],
                "subject": f"【業績アップ診断】新しい診断完了: {name or '名前未入力'} / 第一ボトルネック:{primary}",
                "text": (
                    "業績アップ診断で新しい診断が完了しました。\n\n"
                    f"日時　　　　: {now}\n"
                    f"お名前　　　: {name or '未入力'}\n"
                    f"メール　　　: {email or '未収集'}\n"
                    f"性別　　　　: {gender}\n"
                    f"生年月日　　: {birthday or '未入力'}\n"
                    f"業種　　　　: {industry or '未入力'}\n"
                    f"年商帯　　　: {revenue or '未入力'}\n"
                    f"従業員数　　: {employees or '未入力'}\n"
                    f"困っていること: {worry or '未入力'}\n"
                    f"第一ボトルネック: {primary}\n"
                    f"第二ボトルネック: {secondary}\n"
                    f"6領域スコア:\n{scores_text}\n"
                ),
            })
        except Exception:
            pass

    return jsonify({"ok": True})


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
    """結果表示後にブラウザから呼ばれる。診断結果PDFを添付してお客様へ送信。"""
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    name = (data.get("name") or "").strip()
    type_name = (data.get("type") or "").strip()
    pdf_b64 = (data.get("pdf_base64") or "").strip()

    if not (_resend_ready() and email):
        return jsonify({"ok": False})

    from_email = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
    from_name = os.environ.get("FROM_NAME", "わの巡り診断")
    today = datetime.now(JST).strftime("%Y-%m-%d")

    line_url = "https://lin.ee/VaRyFWg"
    greeting = f"{name}さん\n\n" if name else ""
    if pdf_b64:
        body = (
            f"{greeting}"
            "わの巡り診断をご利用いただき、ありがとうございます。\n\n"
            f"あなたの診断タイプは——「{type_name}」でした。\n\n"
            "詳しい診断結果を、このメールにPDFで添付しています。\n"
            "いつでも、何度でも、読み返してください。\n\n"
            "経営者・リーダーの巡りは、一人では整いません。\n"
            "あなたの巡りを本当に整える具体的な道筋は、LINEでお届けしています。\n"
            f"{line_url}\n\n"
            "あなたの巡りが、今日から動き出しますように。\n\n"
            "わの巡り診断\n"
        )
    else:
        body = (
            f"{greeting}"
            "わの巡り診断をご利用いただき、ありがとうございます。\n\n"
            f"あなたの診断タイプは——「{type_name}」でした。\n\n"
            "詳しい結果は、診断画面にすべて表示されています。\n\n"
            "経営者・リーダーの巡りは、一人では整いません。\n"
            "あなたの巡りを本当に整える具体的な道筋は、LINEでお届けしています。\n"
            f"{line_url}\n\n"
            "あなたの巡りが、今日から動き出しますように。\n\n"
            "わの巡り診断\n"
        )

    params = {
        "from": f"{from_name} <{from_email}>",
        "to": [email],
        "subject": f"【わの巡り診断】あなたの診断結果「{type_name}」をお届けします",
        "text": body,
    }
    # 管理者（サラさん）にも同じメール＋PDF添付をBCCで届ける（結果の控え）
    admin_email = os.environ.get("ADMIN_EMAIL", "monthly@salagracia.com")
    if admin_email and admin_email != email:
        params["bcc"] = [admin_email]
    if pdf_b64:
        params["attachments"] = [{
            "filename": f"wa-meguri-shindan_{today}.pdf",
            "content": pdf_b64,
        }]

    try:
        resend.Emails.send(params)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
