"""
45歳からの 信頼される男 診断 Webアプリ（Streamlit）v1.0
24問×4タイプ・占術統合・男性向け
"""
import streamlit as st
from datetime import date, datetime, time
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_diagnosis
from pdf_generator import generate_pdf
from calculations.personality_quiz import NARRATIVE_QUESTIONS
from calculations.shinrai_otoko import QUESTIONS as KAIKA_QUESTIONS
from email_sender import send_pdf_email, send_admin_notification


st.set_page_config(
    page_title="45歳からの 信頼される男 診断",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header { text-align: center; color: #1E2A47; font-size: 2.5em; margin-bottom: 0; }
    .sub-header { text-align: center; color: #B85C38; font-style: italic; margin-bottom: 30px; }
    .stButton>button { background-color: #1E2A47; color: white; border-radius: 6px;
                       padding: 12px 40px; font-size: 1.1em; border: none; width: 100%; }
    .stButton>button:hover { background-color: #2C3E50; }
    div[data-testid="stExpander"] { background-color: #ECEFF4; border-radius: 6px; }
    .stProgress > div > div { background-color: #1E2A47; }
</style>
""", unsafe_allow_html=True)


st.markdown('<h1 class="main-header">🧭 45歳からの 信頼される男 診断</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">人生後半を立て直すための、あなた専用の設計図</p>',
            unsafe_allow_html=True)

st.markdown("""
この**45歳からの 信頼される男 診断**は、東洋・西洋の占術と現代心理学を組み合わせて、
**あなたの仕事での強み**と、**その同じ強みが家庭でどう出ているか**を、立体的に見ていきます。

🧭 **占術**：数秘・西洋占星術・九星気学・四柱推命・動物キャラ・算命学・帝王学・姓名判断
🛡️ **独自診断**：**45歳からの 信頼される男 診断**（24問・4タイプ・メイン+隠れ）
📈 **運勢**：天中殺・3年の立て直しサイクル
✍️ **自由記述**：仕事の没頭体験・信念・妻への本音・空回りの正体（4問）

**所要時間：約10〜13分**　→ **個人設計図PDF**をメールでお届け
""")

st.divider()


# ========== Step 1: 基本情報 ==========
st.subheader("👤 Step 1：基本情報")

col1, col2 = st.columns(2)
with col1:
    last_name = st.text_input("姓（漢字）", placeholder="山田")
with col2:
    first_name = st.text_input("名（漢字）", placeholder="太郎")

name_kana = st.text_input("お名前（カタカナ・スペースなしで入力）",
                          placeholder="ヤマダタロウ",
                          help="姓と名の間にスペースを入れず、続けてご入力ください（例：ヤマダタロウ）")
email = st.text_input("📧 メールアドレス（必須・診断結果のPDFをお送りします）", placeholder="your@email.com")

col3, col4, col5 = st.columns([2, 1, 2])
with col3:
    birth_date_input = st.date_input("生年月日", min_value=date(1900, 1, 1),
                                       max_value=date.today(), value=date(1980, 1, 1))
with col4:
    birth_time_unknown = st.checkbox("時間不明", value=False)
with col5:
    if not birth_time_unknown:
        birth_time_input = st.time_input("出生時間", value=time(12, 0))
    else:
        birth_time_input = time(12, 0)
        st.caption("12:00で計算します")

birth_place = st.text_input("出生地（都道府県＋市町村）",
                              placeholder="例：東京都新宿区 / 大阪府大阪市")


# ========== Step 2: 45歳からの 信頼される男 診断（24問・4択A/B/C/D） ==========
st.divider()
st.subheader("🛡️ Step 2：45歳からの 信頼される男 診断（24問）")
st.caption("「最も近いもの」を1つ選んでください。所要時間 約5分。")
st.info("💡 仕事軸・家庭軸・価値観軸の3面から、**メインタイプ + 隠れタイプ**が判定されます。")

all_answers = {}

with st.expander("質問を開始する（24問・4択）", expanded=True):
    for i, q in enumerate(KAIKA_QUESTIONS, 1):
        st.markdown(f"**Q{i}. {q['question']}**")
        options = q['options']  # {"A": "...", "B": "...", "C": "...", "D": "..."}
        ans = st.radio(
            label=q['question'],
            options=list(options.keys()),
            format_func=lambda x, opts=options: f"{x}: {opts[x]}",
            key=f"qk_{q['id']}",
            label_visibility="collapsed",
            index=None
        )
        all_answers[q['id']] = ans
        st.markdown("")

# プログレス計算（24問）
answered = sum(1 for q in KAIKA_QUESTIONS if all_answers.get(q['id']) is not None)
progress = st.progress(answered / len(KAIKA_QUESTIONS))
st.caption(f"📊 進捗：{answered} / {len(KAIKA_QUESTIONS)} 問")


# ========== Step 3: 自由記述（必須・4問） ==========
st.divider()
st.subheader("✍️ Step 3：自由記述（必須・4問）")
st.caption("あなたの言葉が、診断の深さを決めます。200字以上、書ける範囲で具体的にお願いします。")
st.info("💡 この4問から、あなたの **強みの核・信念・家族への本音・空回りの正体** が浮かび上がります。\n\n"
        "⚠️ **入力後、テキストボックスの外を一度クリックすると文字数が反映されます**（Streamlitの仕様です）。")

narrative_answers = {}
for n in NARRATIVE_QUESTIONS:
    st.markdown(f"**{n['question']}**")
    st.caption(f"💡 ヒント：{n['hint']}")
    ans = st.text_area(
        label=n['question'], key=f"n_{n['id']}",
        label_visibility="collapsed", height=150,
        max_chars=n['max_length'],
        placeholder="（200字以上を目安に、できるだけ具体的に）"
    )
    narrative_answers[n['id']] = ans
    # 文字数カウンタ（入力済みの場合のみ）＋反映タイミングの説明
    char_count = len((ans or '').strip())
    if char_count == 0:
        st.caption("📝 入力後、テキストボックスの外を一度クリックすると、文字数が反映されます")
    elif char_count < 50:
        st.caption(f"📝 現在 **{char_count}字** / 最低50字必要（入力後ボックス外をクリックで反映）")
    elif char_count < 200:
        st.caption(f"📝 現在 **{char_count}字** / 200字を目安にするとさらに深い診断になります")
    else:
        st.caption(f"✅ 現在 **{char_count}字** — 十分な分量です")
    st.markdown("")


# ========== 診断ボタン ==========
st.divider()

narrative_filled = all(len(narrative_answers.get(n['id'], '').strip()) >= 50
                        for n in NARRATIVE_QUESTIONS)

input_valid = bool(last_name and first_name and name_kana and birth_place
                   and email and "@" in email and answered >= 20
                   and narrative_filled)

if not input_valid:
    if not (last_name and first_name and name_kana and birth_place):
        st.warning("⚠️ 基本情報（姓・名・カタカナ氏名・出生地）をすべて入力してください。")
    elif not email or "@" not in email:
        st.warning("⚠️ メールアドレスを入力してください（診断結果のPDFをメールでお送りします）。")
    elif answered < 20:
        st.warning(f"⚠️ 質問にあと {20 - answered} 問は回答してください（最低20問必須・精度向上のため）。")
    elif not narrative_filled:
        st.warning("⚠️ 自由記述4問にそれぞれ50字以上ご記入ください。\n\n"
                   "💡 **入力済みなのにこの警告が出ている場合**：テキストボックスの外を一度クリックしてください。"
                   "Streamlitの仕様で、ボックスからフォーカスが外れて初めて文字数が反映されます。")

if st.button("🛡️ あなたの「信頼される男タイプ」を診断する", disabled=not input_valid):
    with st.spinner("あなたの占術データと性格を計算中... 🔮"):
        user_input = {
            "name": f"{last_name} {first_name}",
            "last_name": last_name,
            "first_name": first_name,
            "name_kana": name_kana,
            "birth_date": birth_date_input.strftime("%Y-%m-%d"),
            "birth_time": birth_time_input.strftime("%H:%M"),
            "birth_place": birth_place,
            "lat": 35.6762, "lon": 139.6503,
            "answers": {k: v for k, v in all_answers.items() if v is not None},
            "narrative": narrative_answers,
        }

        try:
            result = run_diagnosis(user_input)

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                pdf_path = tmp.name
            generate_pdf(user_input, result, pdf_path)

            st.success("✅ 診断完了！レポートPDFをメールでお送りします。")
            st.markdown("---")
            st.markdown("### 🔮 あなたの主要結果")

            mbti = result['personality']['mbti']
            wd = result['personality']['wd']

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**🧠 16パーソナリティ：{mbti['type']}**")
                st.markdown(f"_{mbti.get('label', '')}_")
                st.markdown(f"**💎 ウェルスダイナミクス：{wd['type']}**")
                st.markdown(f"_{wd.get('label', '')}_")
                st.markdown(f"**🦁 太陽星座：{result['western_astrology']['sun']['name']}**")
                st.markdown(f"**🌙 月星座：{result['western_astrology']['moon']['name']}**")
            with col_b:
                st.markdown(f"**🐘 動物キャラ：{result['doubutsu']['name_60']}**")
                st.markdown(f"（12種：{result['doubutsu']['name_12']}）")
                st.markdown(f"**⭐ 算命学・主星：{result['shusei']['name']}**")
                st.markdown(f"**👑 帝王学：{result['teiou']['name']}**")
                tc_periods = result.get('tenchusatsu_years', {})
                next_p = tc_periods.get('next_period')
                if next_p:
                    st.markdown(f"**🌙 次の天中殺：{next_p[0]}年〜{next_p[1]}年**")

            st.markdown("---")
            st.markdown(f"### 📧 PDFレポートを **{email}** にお送りします")
            st.caption("8ページの完全版PDFが添付ファイルで届きます。")

            with st.spinner("メール送信中... 📨"):
                # 管理者通知（サラさんのリストに追加）
                user_input['email_to'] = email
                user_input['narrative'] = narrative_answers
                admin_result = None
                try:
                    admin_result = send_admin_notification(user_input, result, pdf_path)
                except Exception as e:
                    admin_result = {"success": False, "message": f"Exception: {e}"}

                # デバッグ：管理者通知の結果を画面に表示（ユーザー体験に影響しないよう小さく）
                if admin_result and not admin_result.get('success'):
                    st.caption(f"🔧 管理者通知デバッグ: {admin_result.get('message', '不明')}")

                # ユーザーへのメール送信
                email_result = send_pdf_email(email, user_input['name'], pdf_path)
                if email_result['success']:
                    st.success(f"""
✅ **{email} にメールを送信しました！**

📬 メールボックスをご確認ください。

⚠️ **届かない場合**：
- 迷惑メールフォルダもチェックしてください
- 5分待っても届かない場合は、メールアドレスを確認して再度診断してください
                    """)
                    if admin_result and admin_result.get('success'):
                        st.caption(f"📊 管理者通知も送信済み: {admin_result.get('message')}")
                    st.balloons()
                else:
                    st.error(f"❌ メール送信に失敗しました\n\n{email_result['message']}")
                    st.info("メールアドレスを確認して、もう一度診断してください。")

            # 一時ファイルを削除
            try:
                os.unlink(pdf_path)
            except Exception:
                pass

        except Exception as e:
            st.error(f"診断中にエラーが発生しました：{e}")
            st.exception(e)


st.divider()
# ビルドバージョン（デプロイ反映確認用）
BUILD_VERSION = "v1.4 / 2026-06-15"
st.markdown(f"""
<div style='text-align:center; color:#888; font-size:0.85em; margin-top:30px;'>
    45歳からの 信頼される男 診断 v1.4<br>
    YouTube「信頼される男の流儀」公式診断<br>
    『一番近い人に信頼される男が、外でも信頼される』<br>
    <span style='color:#bbb; font-size:0.8em;'>Build: {BUILD_VERSION}</span>
</div>
""", unsafe_allow_html=True)
