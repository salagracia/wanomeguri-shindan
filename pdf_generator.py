"""
PDF生成（8ページ拡張版）
詳細プロファイル・相性診断・運勢サイクルを含む
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, ListFlowable, ListItem, Image, ImageAndFlowables
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

FONT_REGULAR = None
FONT_BOLD = None


def register_japanese_fonts():
    """日本語フォント登録（環境別自動切替）
    優先順位：
    1. ローカル同梱 IPAex Gothic（fonts/ipaexg.ttf）← Render等のLinuxサーバー
    2. Windows標準フォント
    3. Mac標準フォント
    4. Linuxシステムフォント
    5. ReportLab CID内蔵フォント（最終フォールバック）
    """
    global FONT_REGULAR, FONT_BOLD

    # プロジェクトルートからのパス
    project_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. ローカル同梱 IPAex（最優先・どの環境でも動く）
    local_fonts = [
        ('IPAexGothic', os.path.join(project_dir, 'fonts', 'ipaexg.ttf'),
                         os.path.join(project_dir, 'fonts', 'ipaexg.ttf')),
        ('IPAexMincho', os.path.join(project_dir, 'fonts', 'ipaexm.ttf'),
                         os.path.join(project_dir, 'fonts', 'ipaexm.ttf')),
    ]

    # 2. システム標準フォント候補
    system_fonts = [
        # Windows
        ('YuGothic', r'C:\Windows\Fonts\YuGothM.ttc', r'C:\Windows\Fonts\YuGothB.ttc'),
        ('Meiryo', r'C:\Windows\Fonts\meiryo.ttc', r'C:\Windows\Fonts\meiryob.ttc'),
        ('MSGothic', r'C:\Windows\Fonts\msgothic.ttc', r'C:\Windows\Fonts\msgothic.ttc'),
        # Mac
        ('HiraginoSans', '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
                          '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'),
        # Linux (Render/Debian/Ubuntu系)
        ('NotoSansCJK', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                         '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'),
        ('IPAexSys', '/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf',
                      '/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf'),
    ]

    all_candidates = local_fonts + system_fonts

    for name, regular_path, bold_path in all_candidates:
        try:
            if os.path.exists(regular_path):
                # TTC（コレクション）と TTF を区別
                if regular_path.endswith('.ttc'):
                    pdfmetrics.registerFont(TTFont(name, regular_path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont(name, regular_path))
                FONT_REGULAR = name

                if os.path.exists(bold_path) and bold_path != regular_path:
                    try:
                        bold_name = f"{name}-Bold"
                        if bold_path.endswith('.ttc'):
                            pdfmetrics.registerFont(TTFont(bold_name, bold_path, subfontIndex=0))
                        else:
                            pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                        FONT_BOLD = bold_name
                    except Exception:
                        FONT_BOLD = name
                else:
                    FONT_BOLD = name

                print(f"[FONT] Registered: {name} (regular={regular_path})")
                return
        except Exception as e:
            print(f"[FONT] Failed {name}: {e}")
            continue

    # 5. ReportLab CID内蔵フォント（フォールバック・PDF Viewer依存）
    try:
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
        FONT_REGULAR = 'HeiseiKakuGo-W5'
        FONT_BOLD = 'HeiseiKakuGo-W5'
        print(f"[FONT] Registered CID fallback: HeiseiKakuGo-W5")
        return
    except Exception as e:
        print(f"[FONT] CID font fallback failed: {e}")

    raise RuntimeError("日本語フォントが見つかりません（IPAex fontsがリポジトリに含まれているか確認してください）")


def make_styles():
    styles = getSampleStyleSheet()
    return {
        'title': ParagraphStyle('TitleJP', parent=styles['Title'], fontName=FONT_BOLD,
                                 fontSize=24, leading=30, alignment=TA_CENTER,
                                 textColor=colors.HexColor('#1E2A47'), spaceAfter=15),
        'h1': ParagraphStyle('H1JP', parent=styles['Heading1'], fontName=FONT_BOLD,
                              fontSize=16, leading=22, textColor=colors.HexColor('#1E2A47'),
                              spaceBefore=18, spaceAfter=6,
                              borderPadding=4, borderColor=colors.HexColor('#1E2A47'),
                              borderWidth=0, leftIndent=0),
        'h2': ParagraphStyle('H2JP', parent=styles['Heading2'], fontName=FONT_BOLD,
                              fontSize=13, leading=18, textColor=colors.HexColor('#B85C38'),
                              spaceBefore=8, spaceAfter=4),
        'h3': ParagraphStyle('H3JP', parent=styles['Heading3'], fontName=FONT_BOLD,
                              fontSize=11, leading=15, textColor=colors.HexColor('#2C3E50'),
                              spaceBefore=5, spaceAfter=3),
        'body': ParagraphStyle('BodyJP', parent=styles['Normal'], fontName=FONT_REGULAR,
                                fontSize=9.5, leading=15, textColor=colors.black,
                                alignment=TA_LEFT, spaceAfter=4),
        'small': ParagraphStyle('SmallJP', parent=styles['Normal'], fontName=FONT_REGULAR,
                                 fontSize=8, leading=12, textColor=colors.grey, alignment=TA_CENTER),
        'quote': ParagraphStyle('QuoteJP', parent=styles['Normal'], fontName=FONT_REGULAR,
                                 fontSize=10.5, leading=18, textColor=colors.HexColor('#2C3E50'),
                                 leftIndent=15, rightIndent=15, spaceAfter=8,
                                 backColor=colors.HexColor('#ECEFF4')),
        'tip': ParagraphStyle('TipJP', parent=styles['Normal'], fontName=FONT_REGULAR,
                               fontSize=9.5, leading=15, textColor=colors.HexColor('#1E2A47'),
                               leftIndent=15, spaceAfter=3),
    }


def bullet_list(items, styles):
    """ブレットリスト生成"""
    return ListFlowable(
        [ListItem(Paragraph(it, styles['body']), leftIndent=12) for it in items],
        bulletType='bullet', start='•', leftIndent=18, spaceBefore=2, spaceAfter=4
    )


def chapter_illustration(filename: str, width_mm: float = 35) -> Image | None:
    """章用イラストImageオブジェクトを返す（小さく・フロート用）
    width_mm: PDF上の表示幅（デフォルト35mm = 1/4サイズ）
    """
    project_dir = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(project_dir, 'assets', 'illustrations', filename)
    if not os.path.exists(fp):
        return None
    return Image(fp, width=width_mm*mm, height=width_mm*mm)


def chapter_illustration_wide(filename: str, width_mm: float = 45, height_mm: float = 26) -> Image | None:
    """横長イラスト（小さめ・フロート用）"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(project_dir, 'assets', 'illustrations', filename)
    if not os.path.exists(fp):
        return None
    return Image(fp, width=width_mm*mm, height=height_mm*mm)


def floating_image_with_text(img: Image, text_flowables: list, side: str = 'left') -> ImageAndFlowables:
    """イラストを左or右に配置、テキストを回り込ませる"""
    return ImageAndFlowables(
        img, text_flowables,
        imageSide=side,
        imageLeftPadding=3*mm,
        imageRightPadding=3*mm,
        imageTopPadding=2*mm,
        imageBottomPadding=2*mm,
    )


def build_prologue(user_data: dict, result: dict, styles) -> list:
    """序章：あなたが頭打ちなのは、能力のせいじゃない（v1.2）

    更新ガイドライン§YCS基準確定版に準拠。
    冒頭でレベル5の痛み（仕事頭打ち／家での無言／放置リスク／誰にも言えない本音）を
    提示し、「お前は無能じゃない、順番を間違えていただけだ」のpunchで着地させる。
    希少性パートは「あなた専用に組み立てた根拠」に再フレーム。
    """
    elements = []
    name = user_data.get('first_name') or user_data.get('name', '').split(' ')[-1]
    birth_place = user_data.get('birth_place', '—')
    birth_time = user_data.get('birth_time', '—')
    ws = result.get('western_astrology', {})
    sun_sign = ws.get('sun', {}).get('name', '—')
    moon_sign = ws.get('moon', {}).get('name', '—')
    asc = ws.get('asc', {}).get('name', '—')
    kaika = result.get('personality', {}).get('jinsei_kaika', {})
    main_type = kaika.get('name', '—')
    main_tag = kaika.get('tagline', '')
    # v1.1: 序章では短縮表現を使い、フルtaglineは第2章で初出させる
    main_tag_intro = kaika.get('tag_short') or main_tag
    second_type = kaika.get('second_name', '—')
    second_tag = kaika.get('second_tagline', '')
    second_tag_intro = kaika.get('tag_short') or second_tag  # placeholder; second's short comes from second profile via narrative_generator
    # 隠れタイプの短縮表現を取得するため、shinrai_otokoから直接引く
    from calculations.shinrai_otoko import TYPE_PROFILES as _TYPE_PROFILES
    _second_profile = _TYPE_PROFILES.get(kaika.get('second_type', ''), {})
    second_tag_intro = _second_profile.get('tag_short', second_tag)

    elements.append(Paragraph("序章　あなたが頭打ちなのは、能力のせいじゃない", styles['h1']))

    # ===== レベル5：本音まで見える深さの痛み提示 =====
    pain_naming = (
        f"{name}さん。<br/><br/>"
        f"このレポートを開いた今、あなたの中にはおそらく、<br/>"
        f"言葉になっていない違和感が一つや二つあるはずです。<br/><br/>"
        f"仕事は、それなりにやってきた。<br/>"
        f"むしろ、人より頑張ってきた自信もある。<br/>"
        f"なのに最近、結果が手応えにならない。<br/>"
        f"大事な場面で、なぜか運が向かない。<br/><br/>"
        f"家のドアを開けると、妻と話す言葉が見つからない夜が増えた。<br/>"
        f"聞こうとしても、聞いてもらえる気配がない。<br/>"
        f"「俺はちゃんとやってるのに」と思う回数が、確実に増えている。"
    )
    elements.append(Paragraph(pain_naming, styles['body']))
    elements.append(Spacer(1, 4*mm))

    risk_naming = (
        "そして、誰にも言えない本音が、心の奥にある。<br/><br/>"
        "<b>このまま放置したら、5年後、10年後、<br/>"
        "気づくと周りに人が一人もいなくなっているんじゃないか</b>——と。<br/><br/>"
        "これね、認めたくない話なんです。<br/>"
        "俺もそうでした。"
    )
    elements.append(Paragraph(risk_naming, styles['body']))
    elements.append(Spacer(1, 4*mm))

    # ===== Punchline：言われたい言葉「お前は無能じゃない」=====
    reframe = (
        "でも、ここではっきり言わせてほしい。<br/><br/>"
        "<b>これは能力の問題じゃない。<br/>"
        "年齢の問題でもない。<br/><br/>"
        "順番を、間違えていただけなんです。</b><br/><br/>"
        f"{name}さんが頭打ちなのは、<br/>"
        "一番近くにいる人に、信頼されていないから。<br/>"
        "土台が、抜けているから。<br/><br/>"
        "「だから努力が足りない」と自分を責めてきたなら、<br/>"
        "今日はそれを一旦置いていい。"
    )
    elements.append(Paragraph(reframe, styles['quote']))
    elements.append(Spacer(1, 4*mm))

    # ===== このレポートが何をするか =====
    purpose = (
        "このレポートは、その「順番」を、<br/>"
        f"{name}さん本人の占術と、{name}さん本人の言葉から、<br/>"
        "<b>一緒に見直すために作りました</b>。<br/><br/>"
        "まずは、あなたという男の設計図がどうなっているかを、見ていきましょう。"
    )
    elements.append(Paragraph(purpose, styles['body']))
    elements.append(Spacer(1, 4*mm))

    # ===== 生まれた瞬間：占術の根拠 =====
    moment = (
        f"{name}さんが生まれたその瞬間。<br/>"
        f"<b>{birth_place}</b>の空の下で、<b>{birth_time}</b>という時刻に一つの命が誕生しました。<br/><br/>"
        f"その時、太陽は<b>{sun_sign}</b>にあり、<br/>"
        f"月は<b>{moon_sign}</b>を巡り、<br/>"
        f"地平線には<b>{asc}</b>が昇っていました。<br/><br/>"
        f"世界では同じ日にも多くの命が生まれていましたが、<br/>"
        f"まったく同じ条件で生まれた男は存在しません。"
    )
    elements.append(Paragraph(moment, styles['body']))
    elements.append(Spacer(1, 4*mm))

    # ===== 希少性の数字証明：「あなた専用に組まれた根拠」として再フレーム =====
    rarity = (
        "なぜここまで個別の話ができるのか。<br/>"
        "理由は、数字を見れば分かります。<br/><br/>"
        "太陽星座は12種類。月星座も12種類。<br/>"
        "数秘ライフパスは9種類。干支の組み合わせは60種類。<br/><br/>"
        "これだけでも、<b>12 × 12 × 9 × 60 ＝ 77,760通り</b>。<br/>"
        "さらに出生時刻と出生地を加味すると、<b>およそ93万通り以上</b>の組み合わせになります。<br/><br/>"
        "地球人口を約80億人とすると、<b>80億 ÷ 93万 ＝ 約8,600人</b>。<br/><br/>"
        f"つまり、{name}さんと同じ組み合わせを持つ男は、<br/>"
        "統計上およそ<b>8,600人に1人</b>程度。<br/><br/>"
        "これは「あなたが特別だ」という話じゃない。<br/>"
        f"<b>このレポートが、{name}さんという1人の男だけのために組み立てられた</b>、<br/>"
        "ということを示すための数字です。<br/><br/>"
        "ここから読んでもらう一行一行は、<br/>"
        "あなたの設計に合わせて書かれたものだと思って読んでください。"
    )
    elements.append(Paragraph(rarity, styles['quote']))
    elements.append(Spacer(1, 4*mm))

    # ===== 3つの層 =====
    layers = (
        f"このレポートでは、{name}さんを<b>「3つの層」</b>から立体的に見ていきます。<br/><br/>"
        "<b>第一の層</b>は、生まれ持った設計を読み解く<b>命術の視点</b>。<br/><br/>"
        "<b>第二の層</b>は、今回の診断で導き出された<br/>"
        f"<b>「{main_type}（{main_tag_intro}）」</b>という信頼される男タイプの視点。<br/>"
        f"さらに、<b>「{second_type}（{second_tag_intro}）」</b>という隠れタイプの視点。<br/><br/>"
        "<b>第三の層</b>は、あなた自身の言葉から見えてくる<b>本音の視点</b>です。<br/><br/>"
        "この3つを重ねた時に初めて、<br/>"
        "あなたの「仕事での強み」と「家庭での裏目」が表裏一体だと、はっきり見えてきます。"
    )
    elements.append(Paragraph(layers, styles['body']))
    elements.append(Spacer(1, 4*mm))

    # ===== メッセージの核：男性版にリブート =====
    core_message = (
        "このレポートでお伝えしたいのは、たった一つです。<br/><br/>"
        "<b>あなたの仕事の強みは、本物です。</b><br/>"
        "ここまで人生を背負ってきた武器は、本物です。<br/><br/>"
        "ただ、その武器の向きが、<br/>"
        "<b>仕事の場と、家庭の場で、噛み合っていない</b>。<br/><br/>"
        "それだけです。<br/><br/>"
        "直すのは、能力じゃない。<br/>"
        "<b>順番だけです。</b>"
    )
    elements.append(Paragraph(core_message, styles['quote']))
    elements.append(Spacer(1, 4*mm))

    # ===== 結びの一文 =====
    closing = (
        f"{name}さん。<br/><br/>"
        "あなたが頭打ちなのは、無能だからじゃない。<br/>"
        "<b>順番を、整え直していなかっただけです。</b><br/><br/>"
        "ここから始まる9章は、その順番を一緒に見直すための地図です。"
    )
    elements.append(Paragraph(closing, styles['quote']))

    return elements


def generate_pdf(user_data: dict, result: dict, output_path: str):
    register_japanese_fonts()
    styles = make_styles()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title=f"45歳からの 信頼される男 診断レポート - {user_data['name']}"
    )

    story = []

    # ============== Page 1: 表紙 ==============
    story.append(Spacer(1, 18*mm))
    story.append(Paragraph("45歳からの 信頼される男 診断レポート", styles['title']))
    story.append(Paragraph("人生後半を立て直すための、あなた専用の設計図", styles['small']))
    story.append(Spacer(1, 20*mm))

    user_info = [
        ['氏名', user_data['name']],
        ['生年月日', user_data['birth_date']],
        ['出生時間', user_data.get('birth_time', '不明')],
        ['出生地', user_data.get('birth_place', '不明')],
        ['診断日', datetime.now().strftime('%Y-%m-%d')],
    ]
    tbl = Table(user_info, colWidths=[40*mm, 100*mm])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR), ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1E2A47')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECEFF4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#1E2A47')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 14*mm))
    story.append(Paragraph(
        "東洋・西洋の占術と現代心理学を統合し、<br/>"
        "あなたという唯一無二の存在を立体的に描き出した、<br/>"
        "<b>あなただけの個人設計図</b>です。",
        styles['body']
    ))
    story.append(PageBreak())

    # ============== 序章：あなたという奇跡 ==============
    for el in build_prologue(user_data, result, styles):
        story.append(el)
    story.append(PageBreak())

    # ============== 第1章：あなたの本質（占術データ一覧） ==============
    story.append(Paragraph("第1章：あなたの本質", styles['h1']))
    story.append(Paragraph(
        "8つの占術が語る、あなたの生まれ持った設計を見ていきましょう。"
        "東洋・西洋の叡智が交わる場所に、あなたの本質が浮かび上がります。",
        styles['body']
    ))
    story.append(Spacer(1, 5*mm))

    n = result['numerology']
    ws = result['western_astrology']
    ky = result['kyusei']
    sp = result['shichuusuimei']

    occult_data = [
        ['占術', 'あなたの結果', '意味'],
        ['数秘・ライフパス', f"{n['life_path']['number']}", n['life_path']['meaning'][:30]],
        ['数秘・誕生数', f"{n['birth_day']['number']}", n['birth_day']['meaning'][:30]],
        ['太陽星座', ws['sun']['name'], ws['sun']['theme']],
        ['月星座', ws['moon']['name'], ws['moon'].get('theme', '感情と本能の核')],
        ['アセンダント', ws['asc']['name'], '外向きの表情'],
        ['本命星（九星）', ky['honmei']['name'], ky['honmei']['meaning'][:30]],
        ['月命星', ky['gekkimei']['name'], ky['gekkimei']['meaning'][:30]],
        ['年柱（四柱）', sp['year']['kanshi'], sp['year']['meaning']],
        ['月柱（四柱）', sp['month']['kanshi'], sp['month']['meaning']],
        ['日柱（四柱）', sp['day']['kanshi'], sp['day']['meaning']],
        ['時柱（四柱）', sp.get('hour', {}).get('kanshi', '-'), sp.get('hour', {}).get('meaning', '-')],
        ['動物キャラ（個性心理学）',
         f"{result['doubutsu'].get('name_60', '')}\n（12種類：{result['doubutsu'].get('name_12', '')}）",
         result['doubutsu']['meaning']],
        ['算命学（主星）', result['shusei']['name'], result['shusei']['meaning'][:30]],
        ['帝王学', result['teiou']['name'], result['teiou']['meaning'][:30]],
        ['信頼される男タイプ（メイン）', result['personality']['jinsei_kaika']['type'], result['personality']['jinsei_kaika'].get('name', '')],
        ['隠れタイプ', result['personality']['jinsei_kaika'].get('second_type', ''), result['personality']['jinsei_kaika'].get('second_name', '')],
    ]

    tbl = Table(occult_data, colWidths=[38*mm, 55*mm, 77*mm])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR), ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E2A47')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ECEFF4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    story.append(tbl)

    # 第1章 本文（narrative_generatorから取得・サラ専用テスト本文／Phase2でAPI生成）
    from calculations.narrative_generator import get_chapter1_narrative
    ch1 = get_chapter1_narrative(user_data, result)
    if ch1:
        story.append(Spacer(1, 6*mm))
        for key in ['intro', 'theme', 'impression', 'conflict', 'shine']:
            story.append(Paragraph(ch1[f'{key}_h2'], styles['h2']))
            story.append(Paragraph(ch1[f'{key}_body'], styles['body']))
            story.append(Spacer(1, 3*mm))
        story.append(Paragraph(
            "<i>このあと続く章では、その資質がどのような才能として現れ、<br/>"
            "どのように人生の追い風へと変わっていくのかを見ていきましょう。</i>",
            styles['quote']
        ))

    # ============== Page 3: 信頼される男タイプ詳細（メイン） ==============
    mbti = result['personality']['mbti']
    story.append(Paragraph(f"第2章：あなたの信頼される男タイプ", styles['h1']))
    kaika_main = result.get('personality', {}).get('jinsei_kaika', {})

    # narrative_generatorから本文取得
    from calculations.narrative_generator import get_chapter2_narrative
    ch2 = get_chapter2_narrative(user_data, result)
    if ch2:
        story.append(Paragraph(f"あなたのタイプ：<b>{mbti['type']} — {mbti.get('label', '')}</b>", styles['h2']))
        for key in ['talent', 'scene', 'past', 'bloom', 'future']:
            story.append(Paragraph(ch2[f'{key}_h2'], styles['h2']))
            story.append(Paragraph(ch2[f'{key}_body'], styles['body']))
            story.append(Spacer(1, 3*mm))
    else:
        # フォールバック（旧テンプレ）
        story.append(Paragraph(f"あなたのタイプ：<b>{mbti['type']} — {mbti.get('label', '')}</b>", styles['h2']))
        story.append(Paragraph(mbti.get('summary', ''), styles['quote']))

        story.append(Paragraph("あなたの強み", styles['h3']))
        story.append(bullet_list(mbti.get('strengths', []), styles))

        story.append(Paragraph("気をつけたい弱点", styles['h3']))
        story.append(bullet_list(mbti.get('weaknesses', []), styles))

        story.append(Paragraph("人間関係の特徴", styles['h3']))
        story.append(Paragraph(mbti.get('relationships', ''), styles['body']))

        story.append(Paragraph("適職・キャリア", styles['h3']))
        story.append(Paragraph(mbti.get('career', ''), styles['body']))

        story.append(Paragraph("あなたが取り組むといいチャレンジ", styles['h3']))
        story.append(Paragraph(mbti.get('challenge', ''), styles['tip']))

    # ============== Page 4: 隠れタイプ（第2位） ==============
    wd = result['personality']['wd']
    story.append(Paragraph(f"第3章：あなたの中に眠る、もう一つの顔", styles['h1']))

    from calculations.narrative_generator import get_chapter3_narrative
    ch3 = get_chapter3_narrative(user_data, result)
    if ch3:
        story.append(Paragraph(f"あなたのタイプ：<b>{wd['type']} — {wd.get('label', '')}</b>", styles['h2']))
        for key in ['awakening', 'scene', 'overlap', 'practice', 'future']:
            story.append(Paragraph(ch3[f'{key}_h2'], styles['h2']))
            story.append(Paragraph(ch3[f'{key}_body'], styles['body']))
            story.append(Spacer(1, 3*mm))
    else:
        # フォールバック（旧テンプレ）
        story.append(Paragraph(f"あなたのタイプ：<b>{wd['type']} — {wd.get('label', '')}</b>", styles['h2']))
        story.append(Paragraph(f"戦略：{wd.get('subtitle', '')}", styles['h3']))
        story.append(Paragraph(wd.get('summary', ''), styles['quote']))

        story.append(Paragraph("あなたの強み", styles['h3']))
        story.append(bullet_list(wd.get('strengths', []), styles))

        story.append(Paragraph("気をつけたい弱点", styles['h3']))
        story.append(bullet_list(wd.get('weaknesses', []), styles))

        story.append(Paragraph("運気を上げる戦略", styles['h3']))
        story.append(Paragraph(wd.get('fortune_strategy', ''), styles['quote']))

    # ============== 第4章：人生の追い風とブレーキ ==============
    story.append(Paragraph("第4章：人生の追い風とブレーキ", styles['h1']))
    # 帆船イラスト＋天秤チャート両方とも削除（サラさん指示・意味が伝わらない）

    from calculations.narrative_generator import get_chapter4_narrative
    ch4 = get_chapter4_narrative(user_data, result)
    if ch4:
        for key in ['tailwind', 'overflow', 'brake', 'ally', 'mantra']:
            story.append(Paragraph(ch4[f'{key}_h2'], styles['h2']))
            # 「あなた専用の呪文」セクションだけ quote スタイルで強調
            body_style = styles['quote'] if key == 'mantra' else styles['body']
            story.append(Paragraph(ch4[f'{key}_body'], body_style))
            story.append(Spacer(1, 3*mm))
    else:
        story.append(Paragraph("あなたの中で働く2つの力——あなたを前に進ませるものと、立ち止まらせるもの", styles['body']))
        story.append(Spacer(1, 3*mm))

        story.append(Paragraph("占術が示すあなたの才能の核", styles['h2']))
        talent_text = (
            f"{ws['sun']['name']}の太陽が示す「{ws['sun']['theme']}」、"
            f"そして「{n['life_path']['meaning'].split('。')[0]}」というライフパスが、"
            f"あなたの才能の中心軸を形作っています。<br/><br/>"
            f"{result['shusei']['name']}（算命学）と{ky['honmei']['name']}（九星気学）の組み合わせは、"
            f"<b>「{result['shusei']['meaning'].split('。')[0]}」</b>という資質を裏付けています。"
            f"動物キャラ「{result['doubutsu'].get('name_60', '')}」の特徴である"
            f"「{result['doubutsu']['meaning'].split('。')[0]}」も加わり、"
            f"独自の輝きを放つ人物像が浮かび上がります。"
        )
        story.append(Paragraph(talent_text, styles['body']))
        story.append(Spacer(1, 4*mm))

        story.append(Paragraph("あなたの使命の方向", styles['h2']))
        mission_text = (
            f"{result['teiou']['name']}（帝王学）のあり方が示す通り、"
            f"あなたの使命は<b>「{result['teiou']['meaning']}」</b>という方向にあります。<br/><br/>"
            f"{mbti['type']}としての「{mbti.get('summary', '').split('。')[0]}」を発揮しながら、"
            f"{wd['type']}（{wd.get('label', '')}）として"
            f"「{wd.get('summary', '').split('。')[0]}」を実践することが、"
            f"最も自然な人生の歩み方です。"
        )
        story.append(Paragraph(mission_text, styles['body']))
        story.append(Spacer(1, 4*mm))

        story.append(Paragraph("あなたが気をつけるべき落とし穴", styles['h2']))
        pitfall_text = (
            f"あなたの最大の強み「{mbti.get('strengths', [''])[0]}」は、"
            f"そのまま最大の弱点「{mbti.get('weaknesses', [''])[0]}」と裏表です。<br/><br/>"
            f"{wd['type']}タイプの典型的な落とし穴である「{wd.get('weaknesses', [''])[0]}」も意識し、"
            f"<b>自分の強みを過信せず、補完してくれる仲間と組む</b>ことが鍵です。"
        )
        story.append(Paragraph(pitfall_text, styles['body']))

    # ============== 第5章：これからの開花シナリオ ==============
    fortune = result.get('fortune', {})
    fortune_3y = result.get('fortune_3years', [])
    tc_periods = result.get('tenchusatsu_years', {})
    tc = tc_periods.get('tenchusatsu', fortune.get('tenchusatsu_info', {}))
    prev_p = tc_periods.get('previous_period')
    next_p = tc_periods.get('next_period')
    current_p = tc_periods.get('current_period')

    story.append(Paragraph("第5章：これからの開花シナリオ", styles['h1']))

    from calculations.narrative_generator import get_chapter5_narrative
    ch5 = get_chapter5_narrative(user_data, result)
    if ch5:
        story.append(Paragraph(ch5['three_years_h2'], styles['h2']))
        story.append(Paragraph(ch5['three_years_body'], styles['body']))
        # 整える→広げる→実らせる の波形グラフを文言の直後に配置（低め）
        try:
            from calculations.chart_generator import make_three_year_wave
            from datetime import datetime as _dt
            cur_year = _dt.now().year
            chart_path = make_three_year_wave([
                (f'{cur_year}年', '整える'),
                (f'{cur_year+1}年', '広げる'),
                (f'{cur_year+2}年', '実らせる'),
            ])
            story.append(Spacer(1, 2*mm))
            story.append(Image(chart_path, width=150*mm, height=40*mm, hAlign='CENTER'))
            story.append(Spacer(1, 3*mm))
        except Exception as e:
            print(f"[CHART] wave error: {e}")
        for key in ['pause', 'actions', 'release', 'letter']:
            story.append(Paragraph(ch5[f'{key}_h2'], styles['h2']))
            # 「1年後のあなたへ」セクションだけquoteスタイルで温度感UP
            body_style = styles['quote'] if key == 'letter' else styles['body']
            story.append(Paragraph(ch5[f'{key}_body'], body_style))
            story.append(Spacer(1, 3*mm))
        # 補足：天中殺の具体的な年（実用情報）
        story.append(Paragraph("補足：あなたの「立ち止まる時期」の具体的な年", styles['h3']))
        period_lines = []
        if prev_p:
            period_lines.append(f"前回：<b>{prev_p[0]}年〜{prev_p[1]}年</b>")
        if current_p:
            period_lines.append(f"現在：<b>{current_p[0]}年〜{current_p[1]}年</b>（今まさにこの時期）")
        if next_p:
            period_lines.append(f"次回：<b>{next_p[0]}年〜{next_p[1]}年</b>（大きな決断はこの前までに）")
        story.append(Paragraph("<br/>".join(period_lines), styles['body']))
    else:
        # フォールバック（旧テンプレ）
        story.append(Paragraph("運勢サイクルを味方に、1年後のあなたを描く", styles['body']))
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("あなたの天中殺", styles['h2']))
        tc_text = (
            f"<b>{tc.get('name', '')}</b>（日柱：{tc.get('day_kanshi', '')}）<br/>"
            f"{tc.get('meaning', '')}"
        )
        story.append(Paragraph(tc_text, styles['quote']))
        story.append(Spacer(1, 3*mm))

        story.append(Paragraph("あなたの天中殺の年（具体的時期）", styles['h3']))

        if prev_p:
            story.append(Paragraph(
                f"<b>前回の天中殺：{prev_p[0]}年〜{prev_p[1]}年</b>　← この2年に大きな変化があったはず",
                styles['body']
            ))
        if current_p:
            story.append(Paragraph(
                f"<b>現在の天中殺：{current_p[0]}年〜{current_p[1]}年</b>　← 今まさに天中殺中！",
                styles['body']
            ))
        if next_p:
            story.append(Paragraph(
                f"<b>★ 次の天中殺：{next_p[0]}年〜{next_p[1]}年</b>　← 大きな決断はこの前までに完了させる",
                styles['tip']
            ))

        all_periods = tc_periods.get('all_periods', [])
        if all_periods:
            all_str = "、".join([f"{s}-{e}" if s != e else f"{s}" for s, e in all_periods[:6]])
            story.append(Paragraph(f"<i>※ 全期間：{all_str}（12年周期で繰り返す）</i>", styles['small']))

        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("これから3年のキーワード（毎年の運勢）", styles['h2']))

        year_data = [['年', '十二支', 'キーワード', '解説', '天中殺']]
        for f in fortune_3y:
            is_tc = "天中殺" if f['is_tenchusatsu_year'] else "—"
            year_data.append([
                f"{f['target_year']}年",
                f"{f['now_shi']}年",
                f['keyword'],
                f['description'],
                is_tc
            ])

        year_tbl = Table(year_data, colWidths=[18*mm, 16*mm, 22*mm, 80*mm, 24*mm])
        year_tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR), ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E2A47')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (2, 1), (2, -1), FONT_BOLD),
            ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor('#B85C38')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(year_tbl)
        story.append(Spacer(1, 4*mm))

        story.append(Paragraph("戦略的ポイント", styles['h3']))
        next_year_str = f"{next_p[0]}年" if next_p else "?"
        strategy_text = (
            f"あなたの次の天中殺は<b>{next_year_str}からの2年間</b>です。<br/>"
            f"<b>それまでに大きな決断・拡大・新規挑戦を完了させる</b>のが運気活用の鉄則。<br/><br/>"
            f"特に<b>12年サイクルの頂点「結実」の年</b>は最大の収穫期です。"
            f"その年までに種を蒔き、準備を整えておくと、人生最大の実りを得られます。"
        )
        story.append(Paragraph(strategy_text, styles['quote']))
        story.append(Spacer(1, 5*mm))

        # 第5章の最後に「1年の行動指針」をサブセクションとして統合
        story.append(Paragraph("これから1年であなたが取るべき3つのアクション", styles['h2']))
        actions = [
            f"<b>1. 才能を開く</b>：{ws['sun']['name']}の輝きを活かした「{ws['sun']['theme'].split('・')[0]}」の場を1つ作る。",
            f"<b>2. 仲間を結ぶ</b>：{result['shusei']['name']}の力を活かして、信頼できる仲間との対話を月1回以上持つ。",
            f"<b>3. 強みを投下する</b>：{wd['type']}としての「{wd.get('strengths', [''])[0]}」を、新しい挑戦に投下する。",
        ]
        for a in actions:
            story.append(Paragraph(a, styles['body']))
            story.append(Spacer(1, 2*mm))

        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("今年避けるべきこと", styles['h2']))
        avoid = [
            f"<b>1. </b>{mbti.get('weaknesses', [''])[0]}に陥らないよう、自分のパターンを観察する。",
            f"<b>2. </b>{wd.get('weaknesses', [''])[0]}は{wd['type']}の典型的な失敗パターン。仲間と補完する。",
            f"<b>3. </b>天中殺の年（{'・'.join(tc.get('branches', []))}年）に大きな決断はしない。",
        ]
        for a in avoid:
            story.append(Paragraph(a, styles['body']))
            story.append(Spacer(1, 2*mm))

    # ============== 第6章：大切な人との相性 ==============
    story.append(Paragraph("第6章：大切な人との相性", styles['h1']))

    from calculations.narrative_generator import get_chapter6_narrative
    ch6 = get_chapter6_narrative(user_data, result)
    if ch6:
        for key in ['seeking', 'enabler', 'draining', 'quality', 'nurture']:
            story.append(Paragraph(ch6[f'{key}_h2'], styles['h2']))
            story.append(Paragraph(ch6[f'{key}_body'], styles['body']))
            story.append(Spacer(1, 3*mm))
    else:
        # フォールバック（旧テンプレ）
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("恋愛・パートナーシップ相性", styles['h2']))
        love_text = (
            f"<b>{mbti['type']}としての相性：</b><br/>{mbti.get('love_match', '')}<br/><br/>"
            f"<b>{wd['type']}としての相性：</b><br/>{wd.get('love_match', '')}"
        )
        story.append(Paragraph(love_text, styles['quote']))
        story.append(Spacer(1, 4*mm))

        story.append(Paragraph("相性まとめ", styles['h2']))
        matching_summary = (
            f"あなたは<b>{mbti['type']}×{wd['type']}</b>の組み合わせ。<br/>"
            f"パートナーには、あなたの<b>「{mbti.get('strengths', [''])[0]}」</b>を理解し、"
            f"あなたが苦手な<b>「{mbti.get('weaknesses', [''])[0]}」</b>を補ってくれる人が最適です。<br/><br/>"
            f"恋愛では深い理解と魂レベルのつながりを大切に。"
        )
        story.append(Paragraph(matching_summary, styles['body']))

    # ============== 第7章：数字に宿る、あなたの人生のテーマ ==============
    from calculations.narrative_generator import get_chapter7_narrative
    ch7 = get_chapter7_narrative(user_data, result)
    lp_deep = result.get('numerology', {}).get('life_path_deep', {})

    if ch7:
        story.append(Paragraph("第7章：数字に宿る、あなたの人生のテーマ", styles['h1']))
        for key in ['intro', 'essence', 'shadow', 'triple', 'mature']:
            story.append(Paragraph(ch7[f'{key}_h2'], styles['h2']))
            story.append(Paragraph(ch7[f'{key}_body'], styles['body']))
            story.append(Spacer(1, 3*mm))

        # 数秘ライフパスの具体解説（計算結果由来の固有情報）
        if lp_deep:
            story.append(Paragraph(f"ライフパス{n['life_path']['number']}の詳細：{lp_deep.get('title', '')}", styles['h3']))
            story.append(Paragraph(lp_deep.get('essence', ''), styles['quote']))
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph("あなたの才能", styles['h3']))
            story.append(Paragraph(lp_deep.get('talent', ''), styles['body']))
            story.append(Paragraph("成長の余白（伸びしろ）", styles['h3']))
            story.append(Paragraph(lp_deep.get('growth', ''), styles['body']))
            story.append(Paragraph("魂の使命", styles['h3']))
            story.append(Paragraph(lp_deep.get('mission', ''), styles['body']))
            story.append(Paragraph("50代以上のあなたへ", styles['h3']))
            story.append(Paragraph(lp_deep.get('for_50s', ''), styles['quote']))
    elif lp_deep:
        story.append(Paragraph(f"第7章：数秘ライフパス {n['life_path']['number']} — あなたの数の物語", styles['h1']))
        story.append(Paragraph(f"<b>{lp_deep.get('title', '')}</b>", styles['h2']))
        story.append(Paragraph(lp_deep.get('essence', ''), styles['quote']))
        story.append(Spacer(1, 3*mm))

        story.append(Paragraph("あなたの才能", styles['h3']))
        story.append(Paragraph(lp_deep.get('talent', ''), styles['body']))

        story.append(Paragraph("成長の余白（伸びしろ）", styles['h3']))
        story.append(Paragraph(lp_deep.get('growth', ''), styles['body']))

        story.append(Paragraph("魂の使命", styles['h3']))
        story.append(Paragraph(lp_deep.get('mission', ''), styles['body']))

        story.append(Paragraph("50代以上のあなたへ", styles['h3']))
        story.append(Paragraph(lp_deep.get('for_50s', ''), styles['quote']))

    # ============== 第8章：名前に宿る、あなたへの祝福 ==============
    from calculations.narrative_generator import get_chapter8_narrative
    ch8 = get_chapter8_narrative(user_data, result)
    seimei = result.get('seimei', {})

    if ch8:
        story.append(Paragraph("第8章：名前に宿る、あなたへの祝福", styles['h1']))
        story.append(Paragraph(ch8['gift_h2'], styles['h2']))
        story.append(Paragraph(ch8['gift_body'], styles['body']))
        story.append(Spacer(1, 3*mm))
        # five セクション本文
        story.append(Paragraph(ch8['five_h2'], styles['h2']))
        story.append(Paragraph(ch8['five_body'], styles['body']))
        story.append(Spacer(1, 2*mm))
        # 五格ピラミッド（運命名併記版）を本文の直後に
        try:
            from calculations.chart_generator import make_seimei_pyramid
            if seimei:
                chart_path = make_seimei_pyramid(seimei.get('gokaku', {}))
                story.append(Image(chart_path, width=150*mm, height=103*mm, hAlign='CENTER'))
                story.append(Spacer(1, 3*mm))
        except Exception as e:
            print(f"[CHART] pyramid error: {e}")

        # 五格テーブル＋具体解説（計算結果は必ず表示する）
        if seimei:
            story.append(Paragraph("あなたの五格（計算結果）", styles['h3']))
            gokaku = seimei.get('gokaku', {})
            gokaku_data = [
                ['格', '画数', '数霊の名', '役割'],
                ['天格', str(gokaku.get('tenkaku', 0)), seimei['tenkaku']['name'], '先祖から受け継ぐ運'],
                ['人格 ★', str(gokaku.get('jinkaku', 0)), seimei['jinkaku']['name'], 'あなたの本質（主運）'],
                ['地格', str(gokaku.get('chikaku', 0)), seimei['chikaku']['name'], '青年期までの基礎'],
                ['外格', str(gokaku.get('gaikaku', 0)), seimei['gaikaku']['name'], '社会での印象'],
                ['総格', str(gokaku.get('soukaku', 0)), seimei['soukaku']['name'], '人生全体の大運'],
            ]
            tbl = Table(gokaku_data, colWidths=[18*mm, 16*mm, 50*mm, 56*mm])
            tbl.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR), ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E2A47')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#D5DBE5')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 4*mm))

        # essence（主運）→ totality（総格）の本文＋具体解説
        story.append(Paragraph(ch8['essence_h2'], styles['h2']))
        story.append(Paragraph(ch8['essence_body'], styles['body']))
        if seimei:
            story.append(Paragraph(f"あなたの主運：{seimei['jinkaku']['name']}（{seimei['jinkaku']['number']}画）", styles['h3']))
            story.append(Paragraph(seimei['jinkaku']['description'], styles['body']))
        story.append(Spacer(1, 3*mm))

        story.append(Paragraph(ch8['totality_h2'], styles['h2']))
        story.append(Paragraph(ch8['totality_body'], styles['body']))
        if seimei:
            story.append(Paragraph(f"人生全体の大運：{seimei['soukaku']['name']}（{seimei['soukaku']['number']}画）", styles['h3']))
            story.append(Paragraph(seimei['soukaku']['description'], styles['body']))
            sansai = seimei.get('sansai', {})
            story.append(Paragraph(f"三才配置：{sansai.get('combo', '')}", styles['h3']))
            story.append(Paragraph(sansai.get('meaning', ''), styles['body']))
        story.append(Spacer(1, 3*mm))

        # calling（締めくくり）
        story.append(Paragraph(ch8['calling_h2'], styles['h2']))
        story.append(Paragraph(ch8['calling_body'], styles['body']))
    elif seimei:
        story.append(Paragraph("第8章：姓名判断 — 名前という、最初の贈り物", styles['h1']))
        story.append(Spacer(1, 3*mm))

        story.append(Paragraph(
            seimei.get('intro', '').replace('\n', '<br/>'),
            styles['quote']
        ))
        story.append(Spacer(1, 4*mm))

        # 五格テーブル
        story.append(Paragraph("あなたの五格", styles['h2']))
        gokaku = seimei.get('gokaku', {})
        gokaku_data = [
            ['格', '画数', '数霊の名', '役割'],
            ['天格', str(gokaku.get('tenkaku', 0)), seimei['tenkaku']['name'], '先祖から受け継ぐ運'],
            ['人格 ★', str(gokaku.get('jinkaku', 0)), seimei['jinkaku']['name'], 'あなたの本質（主運）'],
            ['地格', str(gokaku.get('chikaku', 0)), seimei['chikaku']['name'], '青年期までの基礎'],
            ['外格', str(gokaku.get('gaikaku', 0)), seimei['gaikaku']['name'], '社会での印象'],
            ['総格', str(gokaku.get('soukaku', 0)), seimei['soukaku']['name'], '人生全体の大運'],
        ]
        tbl = Table(gokaku_data, colWidths=[18*mm, 16*mm, 50*mm, 56*mm])
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_REGULAR), ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E2A47')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#D5DBE5')),  # 人格行をハイライト
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 4*mm))

        # 主運（人格）の詳細解説
        story.append(Paragraph(f"あなたの主運：{seimei['jinkaku']['name']}", styles['h3']))
        story.append(Paragraph(seimei['jinkaku']['description'], styles['body']))
        story.append(Spacer(1, 3*mm))

        # 総格（人生全体）
        story.append(Paragraph(f"人生全体の大運：{seimei['soukaku']['name']}", styles['h3']))
        story.append(Paragraph(seimei['soukaku']['description'], styles['body']))
        story.append(Spacer(1, 3*mm))

        # 三才配置
        sansai = seimei.get('sansai', {})
        story.append(Paragraph(f"三才配置：{sansai.get('combo', '')}", styles['h3']))
        story.append(Paragraph(sansai.get('meaning', ''), styles['body']))

    # ============== 第9章：あなたの言葉が映す本質 ==============
    from calculations.narrative_generator import get_chapter9_narrative
    ch9 = get_chapter9_narrative(user_data, result)
    narrative = result.get('narrative', {})
    n1 = (narrative.get('N1') or '').strip()
    n2 = (narrative.get('N2') or '').strip()

    if ch9:
        # サラ専用：深掘り版本文
        story.append(Paragraph("第9章：あなたの言葉が映す本質", styles['h1']))
        for key in ['opening', 'talent', 'value', 'future', 'integration']:
            story.append(Paragraph(ch9[f'{key}_h2'], styles['h2']))
            story.append(Paragraph(ch9[f'{key}_body'], styles['body']))
            story.append(Spacer(1, 3*mm))
        # 第9章末で改ページ → 巻末の手紙＋3000円個別相談CTAを新ページに
        story.append(PageBreak())
    elif n1 or n2:
        # フォールバック（旧テンプレ）：簡易版引用＋コメント
        kaika_main = result.get('personality', {}).get('jinsei_kaika', {})
        story.append(Paragraph("第9章：あなたの言葉が映す本質", styles['h1']))
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph(
            "あなたが書いてくれた言葉から、内側の輝きを読み解きます。<br/>"
            "占術データと心理タイプが「設計図」なら、ここに書かれた言葉は「あなたの魂の声」です。",
            styles['quote']
        ))
        story.append(Spacer(1, 4*mm))

        if n1:
            story.append(Paragraph("あなたの夢中体験", styles['h2']))
            story.append(Paragraph(
                f"<i>「{n1}」</i>",
                styles['body']
            ))
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(
                f"<b>ここに見える「{kaika_main.get('name', 'あなた')}」の才能</b><br/>"
                f"この体験の中で、あなたは時間を忘れて没頭しています。<br/>"
                f"これこそ、あなたが本当の自分でいる瞬間。<br/>"
                f"この時間が増えれば増えるほど、人生の輝きが増します。",
                styles['tip']
            ))
            story.append(Spacer(1, 5*mm))

        if n2:
            story.append(Paragraph("あなたの譲れない信念", styles['h2']))
            story.append(Paragraph(
                f"<i>「{n2}」</i>",
                styles['body']
            ))
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(
                f"<b>ここに見える「価値観のコンパス」</b><br/>"
                f"この信念は、あなたの人生の北極星です。<br/>"
                f"迷った時、選択に悩んだ時、この言葉に立ち返ると、必ず本当の道が見えます。<br/>"
                f"「{kaika_main.get('name', 'あなた')}」のタイプと組み合わせることで、揺るぎない人生軸ができます。",
                styles['tip']
            ))

        story.append(PageBreak())

    # ============== Page 10: 兄貴分からの手紙（→ 3000円個別相談 CTA） ==============
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("あなたへ — 手紙", styles['h1']))
    story.append(Spacer(1, 2*mm))

    # 男性版手紙：兄貴分の語り口で、3000円個別相談へ着地させる
    # 仕様書「男性版診断_構成仕様書.md」§3 巻末手紙 に準拠
    kaika_main = result.get('personality', {}).get('jinsei_kaika', {})
    main_name = kaika_main.get('name', 'あなた')
    main_tag_short = kaika_main.get('tag_short') or kaika_main.get('tagline', '')
    first_name = user_data.get('first_name', '') or user_data.get('name', '').split(' ')[-1] or 'あなた'

    story.append(Paragraph(
        f"{first_name}さん。ここまで読んでくれてありがとう。",
        styles['body']
    ))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "正直に言うと、この診断レポートは、<br/>"
        "<b>気持ちのいい話だけを書いた優しいレポートじゃない</b>はずです。",
        styles['body']
    ))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "仕事での強みを認める章があった一方で、<br/>"
        "<b>その同じ強みが、家ではこう出ている</b>と返した章もあった。",
        styles['body']
    ))
    story.append(Spacer(1, 3*mm))

    letter_paragraphs = [
        f"これね、書きながら俺も耳が痛かったんです。<br/>"
        f"なぜなら、{main_name}の男に共通する空回りは、<br/>"
        f"<b>俺自身も通ってきた道</b>だから。",
        "",
        "「もっと頑張れば、仕事も家庭もうまくいくはず」——<br/>"
        "そう思って走ってきた男ほど、ある日ふと気づくんですよ。<br/>"
        "<b>頑張る方向を、少しズレた場所に向けていた</b>ってことに。",
        "",
        f"{first_name}さんの中にある<b>「{main_tag_short}」</b>。<br/>"
        "これは間違いなく、武器です。<br/>"
        "ここまで人生を背負って歩いてこられたのは、これがあったからです。",
        "",
        "ただ、その武器の<b>向きを、家では少しだけ変えていい</b>。<br/>"
        "そうすれば、人生後半の景色は、本当にガラッと変わります。",
        "",
        "<b>もう遅い、なんてことはないです。</b><br/>"
        "順番を、整え直すだけでいい。",
        "",
        "一番近い人に信頼される男が、外でも信頼される。<br/>"
        "<b>これは精神論じゃなく、構造の話</b>です。",
    ]
    for p in letter_paragraphs:
        if p:
            story.append(Paragraph(p, styles['body']))
        else:
            story.append(Spacer(1, 2*mm))

    story.append(Spacer(1, 5*mm))

    # ========== 3000円個別相談 CTA ==========
    story.append(Paragraph(
        f"{first_name}さんの場合の「整え方」を、もう一段深く話したい",
        styles['h2']
    ))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        f"このレポートで見えた「{main_name}としての強み」と「家庭での裏目」は、<br/>"
        "100人いれば100通りの整え方があります。<br/>"
        "あなたの仕事と家庭のリアルに合わせて、<b>あなた専用の順番</b>を一緒に組みたい——<br/>"
        "そう感じた方のために、個別の相談時間を用意しました。",
        styles['body']
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "<b>▶ 60分・個別相談（3,000円）</b><br/>"
        "・このレポートの読み解きと、あなたの場合の整え方<br/>"
        "・仕事の強みを家庭でどう向け直すか<br/>"
        "・人生後半の立て直しの順番<br/>"
        "・その場で出てきた具体的な悩みへの返し",
        styles['quote']
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "申し込みは、診断をお届けしているLINEから受け付けています。<br/>"
        "<b>「個別相談希望」</b>とトークに送ってください。日程をご案内します。",
        styles['body']
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "もう遅い、ではありません。<br/>"
        "<b>順番を整え直せばいい</b>。それだけです。",
        styles['quote']
    ))

    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        f"45歳からの 信頼される男 診断 v1.3 ／ YouTube「信頼される男の流儀」公式診断<br/>"
        f"発行日：{datetime.now().strftime('%Y年%m月%d日')}",
        styles['small']
    ))

    doc.build(story)
    print(f"PDF saved: {output_path}")
