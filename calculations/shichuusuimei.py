"""
四柱推命（lunar-python版・正確）
年柱・月柱・日柱・時柱の干支を算出
"""
from lunar_python import Solar


JIKKAN_NAME_KUN = {
    "甲": ("きのえ", "陽木", "大樹・先駆・剛直"),
    "乙": ("きのと", "陰木", "草花・しなやか・芸術的"),
    "丙": ("ひのえ", "陽火", "太陽・明朗・情熱"),
    "丁": ("ひのと", "陰火", "灯火・繊細・内省"),
    "戊": ("つちのえ", "陽土", "山・包容・堅実"),
    "己": ("つちのと", "陰土", "田園・母性・育成"),
    "庚": ("かのえ", "陽金", "鉄・決断・改革"),
    "辛": ("かのと", "陰金", "宝石・美・繊細"),
    "壬": ("みずのえ", "陽水", "大海・流動・包容"),
    "癸": ("みずのと", "陰水", "雨露・知性・潤い"),
}

JUNISHI_NAME = {
    "子": "ね（ネズミ）",
    "丑": "うし",
    "寅": "とら",
    "卯": "う（うさぎ）",
    "辰": "たつ",
    "巳": "み（へび）",
    "午": "うま",
    "未": "ひつじ",
    "申": "さる",
    "酉": "とり",
    "戌": "いぬ",
    "亥": "い（いのしし）",
}


def _build_pillar(kanshi: str) -> dict:
    """干支文字列から詳細情報"""
    kan = kanshi[0]
    shi = kanshi[1]
    kan_info = JIKKAN_NAME_KUN.get(kan, ("", "", ""))
    return {
        "kanshi": kanshi,
        "kan": kan,
        "shi": shi,
        "yomi": f"{kan_info[0]}・{JUNISHI_NAME.get(shi, '')}",
        "gogyou": kan_info[1],
        "meaning": kan_info[2]
    }


def year_pillar(year: int, month: int = 1, day: int = 1) -> dict:
    """年柱（立春切り替え考慮あり）"""
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    return _build_pillar(lunar.getYearInGanZhi())


def month_pillar(year: int, month: int, day: int) -> dict:
    """月柱（節入り切り替え考慮あり）"""
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    return _build_pillar(lunar.getMonthInGanZhi())


def day_pillar(year: int, month: int, day: int) -> dict:
    """日柱（万年暦ベース・正確）"""
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    return _build_pillar(lunar.getDayInGanZhi())


def hour_pillar(year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> dict:
    """時柱（日干 × 出生時刻）"""
    solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
    lunar = solar.getLunar()
    return _build_pillar(lunar.getTimeInGanZhi())


def get_eto(year: int) -> str:
    """干支（十二支ベース・年）"""
    solar = Solar.fromYmd(year, 6, 1)  # 立春後で確実な6月
    return solar.getLunar().getYearZhi()


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"年柱: {year_pillar(1963, 7, 31)}")
    print(f"月柱: {month_pillar(1963, 7, 31)}")
    print(f"日柱: {day_pillar(1963, 7, 31)}")
    print(f"時柱(06:00): {hour_pillar(1963, 7, 31, 6, 0)}")
    print(f"干支(年): {get_eto(1963)}")
