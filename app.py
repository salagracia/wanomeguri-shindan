"""
45歳からの 信頼される男 タイプ診断 Webアプリ（Streamlit）v5.0
マルチステップ・フォーム化（女性版と同じ構造）

設計：
- Step 1: 基本情報（名前・生年月日・出生時間・出生地）
- Step 2: 20問×Likert（1問ずつ表示・戻る/次へボタン）
- Step 3: 自由記述（任意・4問）
- Step 4: メールアドレス入力（最後・サンクコスト効果でUP）
- Step 5: 診断実行＋結果表示＋PDFダウンロード（メアドミスの保険付き）
"""
import streamlit as st
from datetime import date, datetime, time
import os
import sys
import tempfile
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_diagnosis
from pdf_generator import generate_pdf
from calculations.personality_quiz import NARRATIVE_QUESTIONS
from calculations.shinrai_otoko import QUESTIONS as KAIKA_QUESTIONS, LIKERT_OPTIONS
from email_sender import send_pdf_email, send_admin_notification


st.set_page_config(
    page_title="45歳からの 信頼される男 タイプ診断",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header { text-align: center; color: #1E2A47; font-size: 2.0em; margin-bottom: 0; }
    .sub-header { text-align: center; color: #B85C38; font-style: italic; margin-bottom: 30px; font-size: 0.95em; }
    .stButton>button { background-color: #1E2A47; color: white; border-radius: 6px;
                       padding: 12px 40px; font-size: 1.05em; border: none; width: 100%;
                       font-weight: bold; }
    .stButton>button:hover { background-color: #2C3E50; }
    .stButton>button:disabled { background-color: #ccc; color: #888; }
    div[data-testid="stExpander"] { background-color: #ECEFF4; border-radius: 6px; }
    .stProgress > div > div { background-color: #1E2A47; }
    .question-card {
        background: #F5F7FA;
        border-left: 4px solid #1E2A47;
        padding: 20px 24px;
        border-radius: 8px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)


# ========== セッション状態の初期化 ==========
def init_session_state():
    defaults = {
        'step': 1,                  # 1=基本情報, 2=20問, 3=自由記述, 4=メアド, 5=診断実行
        'question_index': 0,        # 何問目を表示中か（0〜19）
        'shuffled_questions': None, # ランダム化した質問リスト
        'answers': {},              # Likertスコア {q_id: 1-5}
        'narrative_answers': {},    # 自由記述4問の回答
        'last_name': '',
        'first_name': '',
        'name_kana': '',
        'is_real_name': False,
        'birth_date': date(1975, 1, 1),
        'birth_time': time(12, 0),
        'birth_time_unknown': False,
        'birth_place': '',
        'email': '',
        'diagnosis_completed': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # 質問順序をセッションごとに1度だけランダム化
    if st.session_state.shuffled_questions is None:
        questions_copy = list(KAIKA_QUESTIONS)
        random.shuffle(questions_copy)
        st.session_state.shuffled_questions = questions_copy


init_session_state()


# ========== 共通ヘッダー ==========
def render_header():
    st.markdown('<h1 class="main-header">🛡️ 45歳からの<br>信頼される男 タイプ診断</h1>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">仕事で頭打ちを感じている男性のための、行動パターン分析</p>',
                unsafe_allow_html=True)


# ========== Step 1: 基本情報 ==========
def render_step_1():
    render_header()

    st.markdown("""
仕事で結果を出してきたのに、なぜか家ではうまく噛み合わない瞬間がある。

それは、能力でも年齢でもなく、
**「強みの使い場所」が少しズレているだけ**かもしれません。

このアプリでは、**生年月日・名前・20問の質問回答**をもとに、
あなたの **「信頼タイプ」** を読み解きます。

**所要時間：約5〜8分**　→ 結果はその場で表示・PDFレポートはメールでお届け
""")

    st.divider()
    st.subheader("👤 まずは、あなたについて")

    st.info(
        "💡 **ニックネームでも診断できます。**\n\n"
        "本名（漢字）でご記入いただくと、お名前の構造も加味した **詳細レポート** になります。"
    )

    name_mode = st.radio(
        "名前の入力方法",
        options=["ニックネームで入力（簡易版レポート）", "本名で入力（詳細版レポート）"],
        index=1 if st.session_state.is_real_name else 0,
        horizontal=False,
        key="radio_name_mode",
    )
    is_real_name = name_mode.startswith("本名")

    col1, col2 = st.columns(2)
    with col1:
        last_name = st.text_input(
            "姓（または、ニックネームの前半）",
            value=st.session_state.last_name,
            placeholder="山田" if is_real_name else "タロ"
        )
    with col2:
        first_name = st.text_input(
            "名（または、ニックネームの後半）",
            value=st.session_state.first_name,
            placeholder="太郎" if is_real_name else "ちゃん"
        )

    name_kana = st.text_input(
        "お名前（カタカナ・スペースなしで入力）",
        value=st.session_state.name_kana,
        placeholder="ヤマダタロウ" if is_real_name else "タロチャン",
        help="姓と名の間にスペースを入れず、続けてご入力ください"
    )

    birth_date_input = st.date_input(
        "生年月日",
        value=st.session_state.birth_date,
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )

    st.markdown("")
    st.markdown("---")
    st.markdown("##### 📊 ここから先は任意項目です")
    st.caption("分かれば、より精密な分析が追加されます。空欄のままでも診断可能です。")

    birth_time_input = st.time_input(
        "出生時間（任意）",
        value=st.session_state.birth_time,
        help="分からない場合は下のチェックボックスにチェックを入れてください"
    )
    birth_time_unknown = st.checkbox(
        "出生時間は分からない（12:00で計算します）",
        value=st.session_state.birth_time_unknown
    )
    if birth_time_unknown:
        birth_time_input = time(12, 0)

    birth_place = st.text_input(
        "出生地（任意・都道府県＋市町村）",
        value=st.session_state.birth_place,
        placeholder="例：東京都新宿区"
    )

    st.markdown("")

    step1_valid = bool(last_name.strip() and first_name.strip() and name_kana.strip())

    if not step1_valid:
        st.caption("⚠️ 姓・名・カタカナ氏名は必須です")

    if st.button("次へ →", disabled=not step1_valid, key="btn_step1_next"):
        st.session_state.last_name = last_name.strip()
        st.session_state.first_name = first_name.strip()
        st.session_state.name_kana = name_kana.strip()
        st.session_state.is_real_name = is_real_name
        st.session_state.birth_date = birth_date_input
        st.session_state.birth_time = birth_time_input
        st.session_state.birth_time_unknown = birth_time_unknown
        st.session_state.birth_place = birth_place.strip()
        st.session_state.step = 2
        st.session_state.question_index = 0
        st.rerun()


# ========== Step 2: 20問×Likert（1問ずつ） ==========
def render_step_2():
    render_header()

    shuffled = st.session_state.shuffled_questions
    q_idx = st.session_state.question_index
    total = len(shuffled)
    q = shuffled[q_idx]

    # 進捗バー
    progress_val = (q_idx + 1) / total
    st.progress(progress_val)
    st.caption(f"📊 質問 **{q_idx + 1}** / {total}")

    st.markdown("##### 🛡️ 行動パターンの設問")
    st.caption("当てはまる度合いを5段階でお選びください。深く考えず、最初の直感でOKです。")

    st.markdown(
        f'<div class="question-card"><h4>Q{q_idx + 1}. {q["question"]}</h4></div>',
        unsafe_allow_html=True
    )

    # Likert選択肢
    likert_values = [opt["value"] for opt in LIKERT_OPTIONS]
    likert_label_map = {opt["value"]: opt["label"] for opt in LIKERT_OPTIONS}

    current_ans = st.session_state.answers.get(q['id'])
    default_index = (current_ans - 1) if (current_ans in likert_values) else None

    ans = st.radio(
        label="当てはまる度合い",
        options=likert_values,
        format_func=lambda x: f"{x}：{likert_label_map[x]}",
        key=f"radio_q_{q['id']}",
        index=default_index,
        label_visibility="collapsed",
    )

    st.markdown("")

    # ナビゲーション
    col_back, col_next = st.columns(2)
    with col_back:
        if q_idx > 0:
            if st.button("← 戻る", key=f"btn_back_{q_idx}"):
                if ans is not None:
                    st.session_state.answers[q['id']] = ans
                st.session_state.question_index -= 1
                st.rerun()
        else:
            if st.button("← 基本情報に戻る", key="btn_back_to_step1"):
                if ans is not None:
                    st.session_state.answers[q['id']] = ans
                st.session_state.step = 1
                st.rerun()
    with col_next:
        if q_idx < total - 1:
            if st.button("次へ →", disabled=(ans is None), key=f"btn_next_{q_idx}"):
                st.session_state.answers[q['id']] = ans
                st.session_state.question_index += 1
                st.rerun()
        else:
            if st.button("質問完了 →", disabled=(ans is None), key="btn_to_step3"):
                st.session_state.answers[q['id']] = ans
                st.session_state.step = 3
                st.rerun()


# ========== Step 3: 自由記述（任意・4問） ==========
def render_step_3():
    render_header()

    st.progress(1.0)
    st.caption("📊 質問は完了しました")

    st.subheader("✍️ もう少しだけ、あなたの言葉を聞かせてください")

    st.markdown("""
ここからは **任意** です。
空欄のままでも診断は完成します。

ただ——

回答データだけだと、診断は「**あなたタイプの一般的な傾向**」で止まってしまいます。

ここに **あなた自身の言葉** が加わると、診断は
「**あなただけの個人レポート**」に変わります。

書ける範囲で大丈夫です。
**書いていただくほど、診断は深く、あなただけのものになります。**
""")

    st.caption("⚠️ 入力後、テキストボックスの外を一度クリックすると文字数が反映されます（Streamlitの仕様）")

    st.markdown("")

    total_chars = 0
    for n in NARRATIVE_QUESTIONS:
        st.markdown(f"**{n['question']}** _（任意）_")
        st.caption(f"💡 ヒント：{n['hint']}")
        current_val = st.session_state.narrative_answers.get(n['id'], '')
        ans = st.text_area(
            label=n['question'],
            value=current_val,
            key=f"n_{n['id']}",
            label_visibility="collapsed",
            height=120,
            max_chars=n['max_length'],
            placeholder="（任意・書ける範囲で構いません）"
        )
        st.session_state.narrative_answers[n['id']] = ans
        char_count = len((ans or '').strip())
        total_chars += char_count
        if char_count > 0:
            st.caption(f"📝 {char_count}字 — 書いてくれた分だけ、レポートが深くなります")
        st.markdown("")

    if total_chars == 0:
        st.info(
            "💡 **時間がない方は空欄のままで大丈夫**です。「次へ」を押せばメールアドレス入力に進みます。\n\n"
            "ここを少しでも書いていただけると、診断結果のあなたへのメッセージが、ぐっと立体的になります。"
        )

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("← 質問に戻る", key="btn_back_to_q"):
            st.session_state.question_index = len(st.session_state.shuffled_questions) - 1
            st.session_state.step = 2
            st.rerun()
    with col_next:
        if st.button("次へ →", key="btn_to_step4"):
            st.session_state.step = 4
            st.rerun()


# ========== Step 4: メールアドレス入力（最後） ==========
def render_step_4():
    render_header()

    st.progress(1.0)

    st.markdown("""
### 🎉 お疲れさまでした！

あなただけの「**45歳からの 信頼される男 タイプ診断レポート**」が、もうすぐ完成します。

診断結果は約24ページのPDFで、
あなたのメールアドレスにお届けします。
""")

    st.markdown("")

    email = st.text_input(
        "📧 PDFをお届けするメールアドレス",
        value=st.session_state.email,
        placeholder="your@email.com",
        key="input_email"
    )
    st.session_state.email = email

    email_valid = bool(email and "@" in email and "." in email)
    if email and not email_valid:
        st.caption("⚠️ メールアドレスの形式が正しくないようです")

    st.caption("📌 入力されたアドレスは診断レポート送付以外には使用しません。")

    st.markdown("")

    col_back, col_submit = st.columns(2)
    with col_back:
        if st.button("← 戻る", key="btn_back_to_narrative"):
            st.session_state.step = 3
            st.rerun()
    with col_submit:
        if st.button("🛡️ 診断結果を受け取る", disabled=not email_valid, key="btn_diagnose"):
            st.session_state.step = 5
            st.rerun()


# ========== Step 5: 診断実行＋結果表示 ==========
def render_step_5():
    render_header()

    if st.session_state.diagnosis_completed:
        st.success("✅ 診断は完了しています。メールをご確認ください。")
        if st.button("🔄 もう一度診断する", key="btn_restart"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        return

    user_input = {
        "name": f"{st.session_state.last_name} {st.session_state.first_name}",
        "last_name": st.session_state.last_name,
        "first_name": st.session_state.first_name,
        "name_kana": st.session_state.name_kana,
        "is_real_name": st.session_state.is_real_name,
        "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d"),
        "birth_time": st.session_state.birth_time.strftime("%H:%M"),
        "birth_place": st.session_state.birth_place or "東京都",
        "lat": 35.6762, "lon": 139.6503,
        "answers": {k: v for k, v in st.session_state.answers.items() if v is not None},
        "narrative": st.session_state.narrative_answers,
    }

    with st.spinner("回答パターンとプロファイルを分析中..."):
        try:
            result = run_diagnosis(user_input)

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                pdf_path = tmp.name
            generate_pdf(user_input, result, pdf_path)

            with open(pdf_path, 'rb') as _f:
                pdf_bytes = _f.read()

            st.success("✅ 診断完了！レポートPDFをメールでお送りします。")
            st.markdown("---")

            # メインタイプ
            kaika = result.get('personality', {}).get('jinsei_kaika', {})
            if kaika.get('name'):
                st.markdown(f"### 🛡️ あなたのメインタイプ")
                st.markdown(
                    f"#### **{kaika['type']} — {kaika['name']}**"
                )
                if kaika.get('tagline'):
                    st.markdown(f"_{kaika['tagline']}_")
                if kaika.get('second_name'):
                    st.caption(
                        f"🔍 隠れタイプ：**{kaika['second_type']} — {kaika['second_name']}**"
                    )
                st.markdown("---")

                # 強みと家庭での裏目（要約）
                if kaika.get('strength_body'):
                    st.markdown("#### ✅ あなたの仕事での強み")
                    st.markdown(kaika['strength_body'][:300] + "...")
                    st.markdown("")

                if kaika.get('shadow_body'):
                    st.markdown("#### ⚠️ その強みが家庭で届いている形")
                    st.markdown(kaika['shadow_body'][:300] + "...")
                    st.markdown("")

                st.info("📄 詳しい分析・章別解説・整え方の一手は、メールでお届けするPDFレポートに収録しています。")
                st.markdown("---")

            with st.spinner("メール送信中... 📨"):
                user_input['email_to'] = st.session_state.email
                user_input['narrative'] = st.session_state.narrative_answers
                admin_result = None
                try:
                    admin_result = send_admin_notification(user_input, result, pdf_path)
                except Exception as e:
                    admin_result = {"success": False, "message": f"Exception: {e}"}

                if admin_result and not admin_result.get('success'):
                    st.caption(f"🔧 管理者通知デバッグ: {admin_result.get('message', '不明')}")

                email_result = send_pdf_email(
                    st.session_state.email,
                    user_input['name'],
                    pdf_path
                )
                if email_result['success']:
                    st.success(
                        f"📧 **PDFレポートを {st.session_state.email} にお送りしました。**\n\n"
                        f"📬 メールボックスをご確認ください。\n\n"
                        f"⚠️ 届かない場合は迷惑メールフォルダもチェックしてください。"
                    )
                    if admin_result and admin_result.get('success'):
                        st.caption(f"📊 管理者通知も送信済み: {admin_result.get('message')}")
                    st.balloons()
                    st.session_state.diagnosis_completed = True
                else:
                    st.error(f"❌ メール送信に失敗しました\n\n{email_result['message']}")
                    st.info("メールアドレスをご確認ください。下のボタンからPDFを直接ダウンロードもできます。")

            # ========== PDFダウンロードボタン（メアド入力ミスへの保険） ==========
            st.markdown("---")
            st.markdown("### 📥 念のため、この画面からも受け取れます")
            st.caption(
                "メールアドレスを間違えて入力された場合や、メールがすぐに届かない場合のために、"
                "こちらからもPDFレポートをダウンロードできます。"
            )

            safe_name = (user_input['name'] or 'あなた').replace(' ', '_').replace('　', '_')
            st.download_button(
                label="📄 診断レポートPDFをこの画面からダウンロード",
                data=pdf_bytes,
                file_name=f"45歳からの信頼される男診断_{safe_name}.pdf",
                mime="application/pdf",
                key="dl_pdf_btn",
            )

            if not email_result['success']:
                st.markdown("")
                if st.button("← メールアドレスを修正してもう一度送信する", key="btn_retry_email"):
                    st.session_state.step = 4
                    st.rerun()

            try:
                os.unlink(pdf_path)
            except Exception:
                pass

        except Exception as e:
            st.error(f"診断中にエラーが発生しました：{e}")
            st.exception(e)
            if st.button("← 最初に戻る"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()


# ========== ステップディスパッチャ ==========
step = st.session_state.step

if step == 1:
    render_step_1()
elif step == 2:
    render_step_2()
elif step == 3:
    render_step_3()
elif step == 4:
    render_step_4()
elif step == 5:
    render_step_5()


# ========== フッター ==========
st.divider()
BUILD_VERSION = "v5.0 / 2026-06-23 multi-step-form"
st.markdown(f"""
<div style='text-align:center; color:#888; font-size:0.85em; margin-top:30px;'>
    45歳からの 信頼される男 タイプ診断 v5.0<br>
    YouTube「信頼される男の流儀」公式診断<br>
    『一番近い人に信頼される男が、外でも信頼される』<br>
    <span style='color:#bbb; font-size:0.8em;'>Build: {BUILD_VERSION}</span>
</div>
""", unsafe_allow_html=True)
