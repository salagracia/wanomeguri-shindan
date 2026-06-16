"""
メール送信機能（Resend API版・HTTPS経由なのでRender制限を回避）
環境変数：
  RESEND_API_KEY    Resend ダッシュボードで発行したAPIキー
  FROM_EMAIL        送信元（独自ドメイン認証前は onboarding@resend.dev）
  FROM_NAME         サラグラシアアカデミー
"""
import os
import base64
from datetime import datetime


def send_admin_notification(user_data: dict, result: dict, pdf_path: str) -> dict:
    """管理者（サラさん）への診断完了通知＋データベース記録用メール
    monthly@salagracia.com に「リスト追加」メールを送信
    Gmail で検索可能なリストとして蓄積する
    """
    import resend
    api_key = os.environ.get('RESEND_API_KEY', '')
    # 管理者通知は確実に届けるため、検証済みドメインの from を優先
    from_email = os.environ.get('ADMIN_FROM_EMAIL', os.environ.get('FROM_EMAIL', 'onboarding@resend.dev'))
    admin_email = os.environ.get('ADMIN_EMAIL', 'monthly@salagracia.com')

    if not api_key:
        return {"success": False, "message": "RESEND_API_KEY未設定"}

    resend.api_key = api_key

    kaika = result.get('jinsei_kaika') or result.get('personality', {}).get('jinsei_kaika', {})
    ws = result.get('western_astrology', {})
    doubutsu = result.get('doubutsu', {})
    shusei = result.get('shusei', {})
    seimei = result.get('seimei', {})
    teiou = result.get('teiou', {})
    sp = result.get('shichuusuimei', {})
    n = result.get('numerology', {})

    user_name = user_data.get('name', '不明')
    user_email = user_data.get('email_to', user_data.get('email', '不明'))
    birth = user_data.get('birth_date', '不明')

    subject = f"【人生開花リスト追加】{user_name}さん｜{kaika.get('name', '?')}×{kaika.get('second_name', '?')}"

    html_body = f"""
<!DOCTYPE html>
<html><body style="font-family: sans-serif; max-width: 600px;">

<h2 style="color: #8B4789;">📊 新規診断レコード</h2>

<table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
  <tr style="background: #F4ECF7;"><td><b>氏名</b></td><td>{user_name}</td></tr>
  <tr><td><b>メール</b></td><td>{user_email}</td></tr>
  <tr style="background: #F4ECF7;"><td><b>生年月日</b></td><td>{birth}</td></tr>
  <tr><td><b>出生地</b></td><td>{user_data.get('birth_place', '不明')}</td></tr>
  <tr style="background: #F4ECF7;"><td><b>診断日</b></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M')}</td></tr>
</table>

<h3 style="color: #8B4789;">🌸 人生開花タイプ</h3>
<ul>
  <li><b>メイン：{kaika.get('name', '?')}</b>（{kaika.get('tagline', '')}）— {kaika.get('score', 0)}/24点</li>
  <li><b>隠れ才能：{kaika.get('second_name', '?')}</b>（{kaika.get('second_tagline', '')}）— {kaika.get('second_score', 0)}/24点</li>
</ul>

<h3 style="color: #8B4789;">🔮 占術データ</h3>
<table border="1" cellpadding="6" style="border-collapse: collapse; font-size: 0.9em;">
  <tr><td>太陽星座</td><td>{ws.get('sun', {}).get('name', '')}</td></tr>
  <tr><td>月星座</td><td>{ws.get('moon', {}).get('name', '')}</td></tr>
  <tr><td>本命星</td><td>{result.get('kyusei', {}).get('honmei', {}).get('name', '')}</td></tr>
  <tr><td>日柱</td><td>{sp.get('day', {}).get('kanshi', '')}</td></tr>
  <tr><td>動物キャラ</td><td>{doubutsu.get('name_60', '')}（{doubutsu.get('name_12', '')}）</td></tr>
  <tr><td>算命学主星</td><td>{shusei.get('name', '')}</td></tr>
  <tr><td>帝王学</td><td>{teiou.get('name', '')}</td></tr>
  <tr><td>姓名判断（主運）</td><td>{seimei.get('jinkaku', {}).get('name', '')}</td></tr>
  <tr><td>ライフパス</td><td>{n.get('life_path', {}).get('number', '')}</td></tr>
</table>

<h3 style="color: #8B4789;">📝 自由記述</h3>
<p style="background: #f9f9f9; padding: 10px;"><b>夢中体験：</b><br>{user_data.get('narrative', {}).get('N1', '記入なし')}</p>
<p style="background: #f9f9f9; padding: 10px;"><b>譲れない信念：</b><br>{user_data.get('narrative', {}).get('N2', '記入なし')}</p>

<hr>
<p style="color: #888; font-size: 0.85em;">
このメールは管理者向け自動送信です。<br>
Gmail で「人生開花リスト」「{kaika.get('name', '')}」などで検索すると関連レコードが取り出せます。
</p>

</body></html>
"""

    try:
        # PDF添付
        with open(pdf_path, 'rb') as f:
            pdf_b64 = base64.b64encode(f.read()).decode()

        params = {
            "from": f"サラグラシアアカデミー <{from_email}>",
            "to": [admin_email],
            "subject": subject,
            "html": html_body,
            "attachments": [{
                "filename": f"診断_{user_name}.pdf",
                "content": pdf_b64,
            }],
        }
        email_obj = resend.Emails.send(params)
        return {"success": True, "message": f"管理者通知送信完了: {email_obj.get('id', '?')}"}
    except Exception as e:
        return {"success": False, "message": f"管理者通知エラー: {e}"}


def send_pdf_email(to_email: str, user_name: str, pdf_path: str) -> dict:
    """PDF添付メールを Resend API 経由で送信"""
    api_key = os.environ.get('RESEND_API_KEY', '')
    from_email = os.environ.get('FROM_EMAIL', 'onboarding@resend.dev')
    from_name = os.environ.get('FROM_NAME', 'サラグラシアアカデミー')

    if not api_key:
        return {
            "success": False,
            "message": "メール送信の設定が不完全です（API Key未登録）"
        }

    try:
        import resend
    except ImportError:
        return {
            "success": False,
            "message": "Resendパッケージが見つかりません"
        }

    resend.api_key = api_key

    # PDF をbase64エンコード
    try:
        with open(pdf_path, 'rb') as f:
            pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return {"success": False, "message": f"PDF読み込みエラー: {e}"}

    # メール本文
    html_body = f"""
<div style="font-family: 'Hiragino Sans', 'Yu Gothic', sans-serif; max-width: 600px; margin: auto;">
  <h2 style="color: #8B4789;">🌹 人生開花タイプ診断レポートが完成しました</h2>
  <p>{user_name} さん</p>
  <p>この度は人生開花タイプ診断を受けてくださり、本当にありがとうございます。</p>
  <p>あなたの「<strong>人生再起動のための個人設計図</strong>」が完成しました。</p>
  <p>📎 添付ファイルからPDFをご確認ください。</p>

  <hr style="border: 1px solid #F4ECF7;">

  <p><strong>このレポートには：</strong></p>
  <ul>
    <li>東洋・西洋の占術8種類の結果（数秘・西洋占星術・九星気学・四柱推命・動物キャラ・算命学・帝王学・姓名判断）</li>
    <li><strong>サラグラシア独自・人生開花タイプ診断</strong>（あなたのメインタイプ）</li>
    <li><strong>あなたの中に眠る「隠れ才能タイプ」</strong>（意識すると開花する内側の才能）</li>
    <li>あなたの言葉が映す本質（自由記述から読み解く深層）</li>
    <li>大切な人との相性・天中殺・3年間の運勢サイクル</li>
    <li>山岡サラからの手紙</li>
  </ul>
  <p>…が、11ページにわたって描かれています。</p>

  <hr style="border: 1px solid #F4ECF7;">

  <p style="color: #8B4789; font-weight: bold; font-size: 1.1em;">
    『人生は、何度でも再起動できる』
  </p>
  <p>あなたの再起動の旅を、応援しています🌹</p>

  <p>
    山岡サラ（サラグラシアアカデミー）<br>
    🎬 YouTubeチャンネル「脳をだまして若返る」<br>
    <a href="https://www.youtube.com/@agelessJP" style="color: #8B4789;">https://www.youtube.com/@agelessJP</a><br>
    <span style="color: #888; font-size: 0.9em;">（登録者12,500人・50代女性のための若返り×ライフスタイル動画）</span>
  </p>

  <hr style="border: 1px solid #ccc;">
  <p style="color: #888; font-size: 0.85em;">
    ※ このメールは自動送信です<br>
    ※ 人生開花タイプ診断：<a href="https://dna-shindan-sara.onrender.com">https://dna-shindan-sara.onrender.com</a>
  </p>
</div>
"""

    text_body = f"""{user_name} さん

この度は人生開花タイプ診断を受けてくださり、本当にありがとうございます。

あなたの「人生再起動のための個人設計図」が完成しました。
📎 添付ファイルからPDFをご確認ください。

────────────────

このレポートには：
・東洋・西洋の占術8種類の結果
  （数秘・西洋占星術・九星気学・四柱推命・動物キャラ・算命学・帝王学・姓名判断）
・サラグラシア独自「人生開花タイプ診断」（あなたのメインタイプ）
・あなたの中に眠る「隠れ才能タイプ」
・あなたの言葉が映す本質（自由記述から読み解く深層）
・大切な人との相性・天中殺・3年間の運勢サイクル
・山岡サラからの手紙

…が、11ページにわたって描かれています。

────────────────

『人生は、何度でも再起動できる』

あなたの再起動の旅を、応援しています🌹

山岡サラ
サラグラシアアカデミー

🎬 YouTubeチャンネル「脳をだまして若返る」
https://www.youtube.com/@agelessJP
（登録者12,500人・50代女性のための若返り×ライフスタイル動画）
"""

    try:
        params = {
            "from": f"{from_name} <{from_email}>",
            "to": [to_email],
            "subject": "【人生開花タイプ診断】あなたのレポートが完成しました 🌹",
            "html": html_body,
            "text": text_body,
            "attachments": [
                {
                    "filename": f"人生開花タイプ診断_{user_name}.pdf",
                    "content": pdf_b64,
                }
            ]
        }
        result = resend.Emails.send(params)
        return {
            "success": True,
            "message": f"{to_email} にメールを送信しました",
            "id": result.get('id', '')
        }
    except Exception as e:
        return {"success": False, "message": f"メール送信失敗: {e}"}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("使い方: python email_sender.py <to_email> <pdf_path>")
        sys.exit(1)
    result = send_pdf_email(sys.argv[1], "テストユーザー", sys.argv[2])
    print(result)
