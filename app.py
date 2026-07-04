"""
わの巡り診断 Webアプリ（Flask）v1.0

構成:
- GET  /            : 診断アプリ本体（static/index.html）を配信
- POST /api/submit  : メールアドレス入力時に呼ばれる。
                      サラさんへ管理者通知（リード記録）＋お客様へ確認メールを送信。
                      メール送信に失敗しても必ず ok を返し、結果表示を止めない。

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

app = Flask(__name__, static_folder="static")

JST = timezone(timedelta(hours=9))

GENDER_LABELS = {
    "male": "男性",
    "female": "女性",
    "unspecified": "回答なし",
}


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/health")
def health():
    return "ok"


@app.route("/api/submit", methods=["POST"])
def submit():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip()
    gender = GENDER_LABELS.get(data.get("gender"), "回答なし")
    birthday = (data.get("birthday") or "").strip()
    birthtime = (data.get("birthtime") or "").strip()
    birthplace = (data.get("birthplace") or "").strip()
    type_name = (data.get("type") or "").strip()

    api_key = os.environ.get("RESEND_API_KEY", "")
    if resend and api_key and email:
        resend.api_key = api_key
        from_email = os.environ.get("FROM_EMAIL", "onboarding@resend.dev")
        from_name = os.environ.get("FROM_NAME", "わの巡り診断")
        admin_from = os.environ.get("ADMIN_FROM_EMAIL", from_email)
        admin_email = os.environ.get("ADMIN_EMAIL", "monthly@salagracia.com")
        now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")

        # 1) 管理者通知（サラさんのリード記録）
        try:
            resend.Emails.send({
                "from": f"わの巡り診断 <{admin_from}>",
                "to": [admin_email],
                "subject": f"【わの巡り診断】新しい診断: {type_name} ({email})",
                "text": (
                    "わの巡り診断で新しい診断が完了しました。\n\n"
                    f"日時　　　: {now}\n"
                    f"メール　　: {email}\n"
                    f"性別　　　: {gender}\n"
                    f"生年月日　: {birthday}\n"
                    f"出生時刻　: {birthtime or '未入力'}\n"
                    f"出生地　　: {birthplace or '未入力'}\n"
                    f"診断タイプ: {type_name}\n"
                ),
            })
        except Exception:
            pass

        # 2) お客様への確認メール
        try:
            resend.Emails.send({
                "from": f"{from_name} <{from_email}>",
                "to": [email],
                "subject": f"【わの巡り診断】あなたのタイプは「{type_name}」です",
                "text": (
                    "わの巡り診断をご利用いただき、ありがとうございます。\n\n"
                    f"あなたの診断タイプは——「{type_name}」でした。\n\n"
                    "詳しい結果は、診断画面にすべて表示されています。\n"
                    "画面下の「結果をPDFで保存」ボタンから、\n"
                    "いつでも読み返せる形で保存いただけます。\n\n"
                    "あなたの巡りが、今日から動き出しますように。\n\n"
                    "わの巡り診断\n"
                ),
            })
        except Exception:
            pass

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
