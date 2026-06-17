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
✍️ **自由記述**：仕事の没頭体験・信念・妻への本音・空回りの正体（4問・**任意**）

**所要時間：約10〜13分**　→ 結果はその場で表示・**24ページの個人設計図PDFをダウンロード可能**
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


# ========== Step 3: 自由記述（任意・4問） ==========
st.divider()
st.subheader("✍️ Step 3：自由記述（任意・4問／飛ばしてもOK）")
st.caption("書ける範囲で構いません。1〜2問だけでも、書いた分だけレポートが深くなります。")
st.info("💡 この4問は **書くと診断レポートに引用されますが、空欄でも診断は実行できます**。\n\n"
        "時間がない方は、ここを飛ばして下のボタンへどうぞ。")

narrative_answers = {}
for n in NARRATIVE_QUESTIONS:
    st.markdown(f"**{n['question']}**")
    st.caption(f"💡 ヒント：{n['hint']}")
    ans = st.text_area(
        label=n['question'], key=f"n_{n['id']}",
        label_visibility="collapsed", height=120,
        max_chars=n['max_length'],
        placeholder="（任意・書ける範囲で構いません）"
    )
    narrative_answers[n['id']] = ans
    # 文字数カウンタ（柔らかいトーン）
    char_count = len((ans or '').strip())
    if char_count > 0:
        st.caption(f"📝 {char_count}字 — 書いてくれた分だけ、レポートが深くなります")
    st.markdown("")


# ========== 診断ボタン ==========
st.divider()

# v2.0: メアド入力廃止。基本情報＋20問以上で診断OK。結果は画面表示＋PDFダウンロード。
input_valid = bool(last_name and first_name and name_kana and birth_place
                   and answered >= 20)

if not input_valid:
    if not (last_name and first_name and name_kana and birth_place):
        st.warning("⚠️ 基本情報（姓・名・カタカナ氏名・出生地）をすべて入力してください。")
    elif answered < 20:
        st.info(f"あと {20 - answered} 問、答えていただくと診断できます（より正確な判定のため、20問以上を目安にしています）。")

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

            # PDFバイトを読み込む（ダウンロードボタン用）
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()

            # 管理者（サラさん）への通知をバックグラウンドで送信（ユーザー体験に影響しない）
            try:
                send_admin_notification(user_input, result, pdf_path)
            except Exception:
                pass  # 管理者通知エラーは静かに失敗（ユーザーには見せない）

            # 一時ファイルを削除（バイトは既にメモリにある）
            try:
                os.unlink(pdf_path)
            except Exception:
                pass

            # ============ 結果画面 ============
            kaika = result['personality']['jinsei_kaika']

            st.markdown("---")
            st.success("✅ 診断完了です。")
            st.markdown(f"## あなたは **{kaika['type']} {kaika['name']}**")
            st.markdown(f"_{kaika['tagline']}_")
            st.markdown(f"**隠れタイプ：{kaika['second_type']} {kaika['second_name']}**（{kaika['second_tagline']}）")

            st.markdown("---")

            # 仕事の強み
            st.markdown("### ✅ あなたの仕事での強み")
            st.markdown(kaika.get('strength_body', '').replace('\n\n', '\n\n'))

            st.markdown("---")

            # 家庭での裏目
            st.markdown("### ⚠️ その強みは、家庭でこう届いているかも")
            st.markdown(kaika.get('shadow_body', '').replace('\n\n', '\n\n'))

            st.markdown("---")

            # 占術データ要約
            with st.expander("🔮 あなたの占術データ（参考）"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**🦁 太陽星座：** {result['western_astrology']['sun']['name']}")
                    st.markdown(f"**🌙 月星座：** {result['western_astrology']['moon']['name']}")
                    st.markdown(f"**🔢 ライフパス数：** {result['numerology']['life_path']['number']}")
                    st.markdown(f"**⭐ 算命学・主星：** {result['shusei']['name']}")
                with col_b:
                    st.markdown(f"**🐘 動物キャラ：** {result['doubutsu']['name_60']}")
                    st.markdown(f"**👑 帝王学：** {result['teiou']['name']}")
                    st.markdown(f"**🪐 本命星：** {result['kyusei']['honmei']['name']}")
                    tc_periods = result.get('tenchusatsu_years', {})
                    next_p = tc_periods.get('next_period')
                    if next_p:
                        st.markdown(f"**🌙 次の天中殺：** {next_p[0]}〜{next_p[1]}年")

            st.markdown("---")

            # PDFダウンロード
            st.markdown("### 📄 24ページの本格レポートをダウンロード")
            st.markdown(
                "占術データ＋4タイプ判定＋自由記述から、**あなただけの個人設計図**として全章書き出しました。"
                "ゆっくり読み返したい時のために、PDFをダウンロードできます。"
            )

            filename = f"45歳からの信頼される男診断_{user_input['name'].replace(' ', '')}.pdf"
            st.download_button(
                label="📥 PDFレポートをダウンロード",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                type="primary",
            )
            st.caption("※ レポートは保存されません。必要なら今すぐダウンロードしてください。")

            st.markdown("---")

            # 個別相談 CTA
            st.markdown("### あなたの場合の「整え方」を、もう一段深く話したい方へ")
            st.markdown(
                "このレポートで見えた **「強み」と「家庭での裏目」** は、100人いれば100通りの整え方があります。\n\n"
                "あなたの仕事と家庭のリアルに合わせて、**あなた専用の順番**を一緒に組みたい方のために、個別の相談時間を用意しました。\n\n"
                "**▶ 60分・個別相談（3,000円）**\n"
                "- このレポートの読み解きと、あなたの場合の整え方\n"
                "- 仕事の強みを家庭でどう向け直すか\n"
                "- 人生後半の立て直しの順番\n"
                "- その場で出てきた具体的な悩みへの返し\n\n"
                "申し込みは、診断をお届けしているLINEから受け付けています。\n"
                "**「個別相談希望」** とトークに送ってください。日程をご案内します。"
            )

            st.balloons()

        except Exception as e:
            st.error(f"診断中にエラーが発生しました：{e}")
            st.exception(e)


st.divider()
# ビルドバージョン（デプロイ反映確認用）
BUILD_VERSION = "v2.0 / 2026-06-17"
st.markdown(f"""
<div style='text-align:center; color:#888; font-size:0.85em; margin-top:30px;'>
    45歳からの 信頼される男 診断 v2.0<br>
    YouTube「信頼される男の流儀」公式診断<br>
    『一番近い人に信頼される男が、外でも信頼される』<br>
    <span style='color:#bbb; font-size:0.8em;'>Build: {BUILD_VERSION}</span>
</div>
""", unsafe_allow_html=True)
