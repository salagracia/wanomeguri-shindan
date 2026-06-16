"""
チャート/グラフ生成モジュール
matplotlib を使って、各ユーザーの占術データから動的に図を生成。
PDFに埋め込む PNG 画像を返す。
"""
import os
import io
import tempfile
import matplotlib
matplotlib.use('Agg')  # 非対話モード（サーバー環境用）
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
import numpy as np

# ブランドカラー（男性版：ネイビー＋銅色アクセント）
# 変数名は互換性のため女性版から維持
BRAND_PURPLE = '#1E2A47'  # ディープネイビー（基調）
BRAND_RED = '#B85C38'     # 銅色アクセント
BRAND_LIGHT = '#ECEFF4'   # ライトスレート（背景）
BRAND_PINK = '#D5DBE5'    # スレートハイライト
BRAND_GOLD = '#B0792E'    # ブロンズゴールド

# 日本語フォント設定
def _setup_japanese_font():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_candidates = [
        os.path.join(project_dir, 'fonts', 'ipaexg.ttf'),
        r'C:\Windows\Fonts\YuGothM.ttc',
        r'C:\Windows\Fonts\meiryo.ttc',
        r'C:\Windows\Fonts\msgothic.ttc',
        '/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf',
        '/Library/Fonts/Hiragino Sans GB.ttc',
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                fm.fontManager.addfont(fp)
                font_name = fm.FontProperties(fname=fp).get_name()
                rcParams['font.family'] = font_name
                rcParams['axes.unicode_minus'] = False
                return True
            except Exception:
                continue
    return False

_setup_japanese_font()


def _save_to_temp_png(fig) -> str:
    """matplotlibのFigureをPNGとして一時ファイルに保存し、パスを返す"""
    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    fig.savefig(tmp.name, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    return tmp.name


# ===== 1. 序章：希少性インフォグラフィック =====
def make_rarity_chart() -> str:
    """『8,600人に1人』を視覚化する円グラフ"""
    fig, ax = plt.subplots(figsize=(6, 4))
    sizes = [1, 8599]
    colors = [BRAND_PURPLE, '#EFEFEF']
    wedges, _ = ax.pie(sizes, colors=colors, startangle=90,
                       wedgeprops={'edgecolor': 'white', 'linewidth': 2},
                       counterclock=False)
    # 中央テキスト
    ax.text(0, 0.1, '8,600人に\n1人', ha='center', va='center',
            fontsize=22, fontweight='bold', color=BRAND_PURPLE)
    ax.text(0, -0.3, 'あなたは唯一無二の設計', ha='center', va='center',
            fontsize=10, color='#666')
    # 中央を白く
    centre = plt.Circle((0, 0), 0.55, fc='white', ec='white')
    ax.add_artist(centre)
    ax.set_aspect('equal')
    return _save_to_temp_png(fig)


# ===== 2. 第1章：4タイプ レーダーチャート =====
def make_type_radar(scores: dict) -> str:
    """4タイプ（A/B/C/D）の点数をレーダーチャートで表示
    scores = {'A': 19, 'B': 0, 'C': 0, 'D': 5} のような形式
    """
    labels = ['創造\n(A)', '癒し\n(B)', '導き\n(C)', '美意識\n(D)']
    values = [scores.get('A', 0), scores.get('B', 0),
              scores.get('C', 0), scores.get('D', 0)]
    # 24点満点を100%として正規化
    values = [v / 24 * 100 for v in values]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={'projection': 'polar'})
    ax.fill(angles_plot, values_plot, color=BRAND_PURPLE, alpha=0.3)
    ax.plot(angles_plot, values_plot, color=BRAND_PURPLE, linewidth=2.5)
    # 各タイプの値ラベル
    for ang, v, lab in zip(angles, values, labels):
        ax.text(ang, v + 8, f'{int(v)}%', ha='center', va='center',
                fontsize=11, color=BRAND_RED, fontweight='bold')
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['25%', '50%', '75%', '100%'], color='#999', fontsize=8)
    ax.set_ylim(0, 110)
    ax.grid(color='#CCC', linestyle='--', linewidth=0.5)
    ax.set_title('あなたの4タイプ判定', fontsize=14, color=BRAND_PURPLE,
                 fontweight='bold', pad=20)
    return _save_to_temp_png(fig)


# ===== 3. 第5章：3年運勢の波形グラフ =====
def make_three_year_wave(year_keywords: list) -> str:
    """3年間の運勢キーワードを波形で表示
    year_keywords = [('2026', '整える'), ('2027', '広げる'), ('2028', '実らせる')]
    """
    if not year_keywords:
        year_keywords = [('今年', '整える'), ('来年', '広げる'), ('再来年', '実らせる')]

    fig, ax = plt.subplots(figsize=(8, 2.2))
    x = np.linspace(0, 2 * np.pi, 200)
    y = 0.5 + 0.4 * np.sin(x - np.pi / 2)

    ax.plot(x, y, color=BRAND_PURPLE, linewidth=3)
    ax.fill_between(x, y, 0, color=BRAND_PURPLE, alpha=0.15)

    # 3つのマイルストーン
    for i, (year, kw) in enumerate(year_keywords[:3]):
        xpos = i * np.pi
        ypos = 0.5 + 0.4 * np.sin(xpos - np.pi / 2)
        ax.scatter(xpos, ypos, s=200, color=BRAND_RED, zorder=5,
                   edgecolor='white', linewidth=2.5)
        ax.text(xpos, ypos + 0.15, year, ha='center', fontsize=11,
                color='#333', fontweight='bold')
        ax.text(xpos, ypos - 0.18, kw, ha='center', fontsize=13,
                color=BRAND_PURPLE, fontweight='bold')

    ax.set_ylim(-0.05, 1.1)
    ax.set_xlim(-0.5, 2 * np.pi + 0.5)
    ax.axis('off')
    ax.set_title('これからの3年間、人生の波', fontsize=13,
                 color=BRAND_PURPLE, fontweight='bold', pad=10)
    return _save_to_temp_png(fig)


# ===== 4. 第8章：五格ピラミッド =====
def _get_surei_name(num: int) -> str:
    """SUREI_81から運命の名前だけ取得（chart_generatorで内製・依存最小化）"""
    try:
        from calculations.seimei_handan import SUREI_81
        item = SUREI_81.get(num)
        if item:
            return item[0]  # ('名前', '説明') の0番目
    except Exception:
        pass
    return ''


def make_seimei_pyramid(gokaku: dict) -> str:
    """姓名判断の五格を視覚的に表示（運命の名前を併記）
    gokaku = {'tenkaku': 11, 'jinkaku': 11, 'chikaku': 5, 'gaikaku': 5, 'soukaku': 16}
    """
    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor('white')

    # 五格データ（運命の名前を併記）
    items = [
        ('天格', '先祖から受け継ぐ運', gokaku.get('tenkaku', 0), 0.5, 0.88, BRAND_PURPLE),
        ('人格', 'あなたの本質 ★', gokaku.get('jinkaku', 0), 0.5, 0.55, BRAND_RED),
        ('地格', '幼少期の基礎', gokaku.get('chikaku', 0), 0.5, 0.22, BRAND_PURPLE),
        ('外格', '社会での印象', gokaku.get('gaikaku', 0), 0.12, 0.55, BRAND_GOLD),
        ('総格', '人生全体', gokaku.get('soukaku', 0), 0.88, 0.55, BRAND_GOLD),
    ]

    # 接続線（中央軸＋左右）
    ax.plot([0.5, 0.5, 0.5], [0.88, 0.55, 0.22], color='#CCC',
            linestyle='--', zorder=1, linewidth=1.2)
    ax.plot([0.12, 0.5, 0.88], [0.55, 0.55, 0.55], color='#CCC',
            linestyle='--', zorder=1, linewidth=1.2)

    for label, role, num, x, y, color in items:
        # 円
        circle = plt.Circle((x, y), 0.085, color=color, alpha=0.9, zorder=3)
        ax.add_patch(circle)
        # 数字
        ax.text(x, y, str(num), ha='center', va='center',
                fontsize=18, fontweight='bold', color='white', zorder=4)
        # 五格名（上）
        ax.text(x, y + 0.115, label, ha='center', va='center',
                fontsize=11, color='#333', fontweight='bold')
        # 役割（円のすぐ下）
        ax.text(x, y - 0.115, role, ha='center', va='center',
                fontsize=8, color='#666')
        # 運命の名前（一番下・縁取りボックス）
        surei_name = _get_surei_name(num)
        if surei_name:
            ax.text(x, y - 0.185, surei_name, ha='center', va='center',
                    fontsize=8.5, color=color, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=color, linewidth=1))

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('あなたの五格 — 名前に宿る5つの運', fontsize=13,
                 color=BRAND_PURPLE, fontweight='bold', pad=10)
    return _save_to_temp_png(fig)


# ===== 5. 第7章：3つの数字の重なり =====
def make_three_numbers_venn(life_path: int, birth_day: int, destiny: int) -> str:
    """ライフパス × 誕生数 × 運命数 の3円ベン図"""
    fig, ax = plt.subplots(figsize=(6, 5))

    # 3つの円
    c1 = plt.Circle((0.3, 0.6), 0.25, color=BRAND_PURPLE, alpha=0.4)
    c2 = plt.Circle((0.5, 0.3), 0.25, color=BRAND_RED, alpha=0.4)
    c3 = plt.Circle((0.7, 0.6), 0.25, color=BRAND_GOLD, alpha=0.4)
    ax.add_patch(c1)
    ax.add_patch(c2)
    ax.add_patch(c3)

    # 数字ラベル
    ax.text(0.20, 0.78, f'ライフパス\n{life_path}', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#333')
    ax.text(0.50, 0.10, f'誕生数\n{birth_day}', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#333')
    ax.text(0.80, 0.78, f'運命数\n{destiny}', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#333')

    # 中心
    ax.text(0.50, 0.50, 'あなた', ha='center', va='center',
            fontsize=15, fontweight='bold', color=BRAND_PURPLE)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('あなたを形作る 3つの数', fontsize=13,
                 color=BRAND_PURPLE, fontweight='bold')
    return _save_to_temp_png(fig)


# ===== 6. 第4章：追い風とブレーキの天秤 =====
def make_balance_chart() -> str:
    """強み（追い風）と弱み（ブレーキ）の天秤イメージ"""
    fig, ax = plt.subplots(figsize=(7, 3.5))

    # 支点
    ax.plot([0.5, 0.5], [0.1, 0.5], color='#666', linewidth=3)
    # バー
    ax.plot([0.15, 0.85], [0.5, 0.5], color='#666', linewidth=3)
    # 左の皿（追い風）
    ax.scatter(0.15, 0.48, s=2000, color=BRAND_PURPLE, alpha=0.7,
               edgecolor='white', linewidth=2)
    ax.text(0.15, 0.48, '追い風', ha='center', va='center',
            fontsize=12, color='white', fontweight='bold')
    ax.text(0.15, 0.70, '才能・強み', ha='center', fontsize=10, color='#333')
    # 右の皿（ブレーキ）
    ax.scatter(0.85, 0.48, s=2000, color=BRAND_RED, alpha=0.7,
               edgecolor='white', linewidth=2)
    ax.text(0.85, 0.48, 'ブレーキ', ha='center', va='center',
            fontsize=12, color='white', fontweight='bold')
    ax.text(0.85, 0.70, '反転した強み', ha='center', fontsize=10, color='#333')

    # 中央メッセージ
    ax.text(0.5, 0.05, '同じエネルギーから生まれる、二つの力',
            ha='center', fontsize=11, color=BRAND_PURPLE, fontweight='bold')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.85)
    ax.set_aspect('equal')
    ax.axis('off')
    return _save_to_temp_png(fig)
