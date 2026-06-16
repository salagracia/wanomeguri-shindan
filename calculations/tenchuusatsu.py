"""
天中殺・年運（算命学）
日干支から天中殺を判定、現在年と本人の干支から運勢サイクルを判定
"""
from datetime import date
from lunar_python import Solar


TENCHUSATSU_GROUPS = [
    (0, 9, "戌亥天中殺", ["戌", "亥"]),
    (10, 19, "申酉天中殺", ["申", "酉"]),
    (20, 29, "午未天中殺", ["午", "未"]),
    (30, 39, "辰巳天中殺", ["辰", "巳"]),
    (40, 49, "寅卯天中殺", ["寅", "卯"]),
    (50, 59, "子丑天中殺", ["子", "丑"]),
]


TENCHUSATSU_MEANINGS = {
    "戌亥天中殺": "精神性・天運の天中殺。物質より精神的価値を求める時期。霊性が高まる。",
    "申酉天中殺": "家庭の天中殺。家族・住居・身近な関係に変化が起きやすい時期。",
    "午未天中殺": "中年期の天中殺。社会的役割の見直しが必要な時期。",
    "辰巳天中殺": "青春期の天中殺。学びと模索の時期。型を破る変革のとき。",
    "寅卯天中殺": "初年期の天中殺。新しい始まりに向けた準備期。",
    "子丑天中殺": "晩年期の天中殺。人生の総まとめと次世代への伝授の時期。",
}


SHI_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _get_kanshi_index(kan: str, shi: str) -> int:
    kan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    kan_idx = kan_list.index(kan)
    shi_idx = SHI_LIST.index(shi)
    for i in range(60):
        if i % 10 == kan_idx and i % 12 == shi_idx:
            return i
    return 0


def get_tenchusatsu(year: int, month: int, day: int) -> dict:
    """日干支から天中殺を判定"""
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    day_kan = lunar.getDayGan()
    day_shi = lunar.getDayZhi()
    idx = _get_kanshi_index(day_kan, day_shi)
    for start, end, name, branches in TENCHUSATSU_GROUPS:
        if start <= idx <= end:
            return {
                "name": name,
                "branches": branches,
                "meaning": TENCHUSATSU_MEANINGS[name],
                "day_kanshi": f"{day_kan}{day_shi}",
            }
    return {"name": "不明", "branches": [], "meaning": "", "day_kanshi": f"{day_kan}{day_shi}"}


def get_tenchusatsu_years(birth_year: int, birth_month: int, birth_day: int,
                          from_year: int = None, to_year: int = None) -> dict:
    """天中殺に該当する年（過去・現在・未来）を算出"""
    tc = get_tenchusatsu(birth_year, birth_month, birth_day)
    branches = tc["branches"]

    if from_year is None:
        from_year = max(birth_year, date.today().year - 30)
    if to_year is None:
        to_year = date.today().year + 30

    tenchusatsu_years = []
    for y in range(from_year, to_year + 1):
        solar = Solar.fromYmd(y, 6, 1)
        y_shi = solar.getLunar().getYearZhi()
        if y_shi in branches:
            tenchusatsu_years.append((y, y_shi))

    # 連続する2年をペアにする
    periods = []
    i = 0
    while i < len(tenchusatsu_years):
        if i + 1 < len(tenchusatsu_years) and tenchusatsu_years[i+1][0] == tenchusatsu_years[i][0] + 1:
            periods.append((tenchusatsu_years[i][0], tenchusatsu_years[i+1][0]))
            i += 2
        else:
            periods.append((tenchusatsu_years[i][0], tenchusatsu_years[i][0]))
            i += 1

    today_year = date.today().year
    next_period = None
    previous_period = None
    current_period = None
    for start, end in periods:
        if today_year < start:
            if next_period is None:
                next_period = (start, end)
        elif start <= today_year <= end:
            current_period = (start, end)
        else:
            previous_period = (start, end)

    return {
        "tenchusatsu": tc,
        "all_periods": periods,
        "previous_period": previous_period,
        "current_period": current_period,
        "next_period": next_period,
    }


CYCLE_KEYWORDS = [
    ("再生", "新しいサイクルの始まり。リセットと種まきの年。"),
    ("芽吹き", "可能性が芽を出す年。小さな一歩を大切に。"),
    ("成長", "勢いよく伸びる年。挑戦のとき。"),
    ("成熟", "実力が認められる年。社会的な評価。"),
    ("結実", "頂点の年。最大の収穫期。"),
    ("分岐", "選択の年。方向性を見直すとき。"),
    ("内省", "立ち止まり考える年。内側に問いを向ける。"),
    ("再構築", "立て直しの年。価値観の整理。"),
    ("収穫", "今までの蓄積が形になる年。"),
    ("整理", "手放しの年。古いものを次世代へ。"),
    ("休息", "回復の年。エネルギー充電。"),
    ("胎動", "次のサイクルへの準備期。静かに整える年。"),
]


def get_year_fortune(birth_year: int, birth_month: int, birth_day: int,
                     target_year: int = None) -> dict:
    """指定年の運勢サイクルを判定（単年）"""
    if target_year is None:
        target_year = date.today().year

    solar_birth = Solar.fromYmd(birth_year, birth_month, birth_day)
    birth_shi = solar_birth.getLunar().getYearZhi()

    solar_now = Solar.fromYmd(target_year, 6, 1)
    now_shi = solar_now.getLunar().getYearZhi()

    birth_idx = SHI_LIST.index(birth_shi)
    now_idx = SHI_LIST.index(now_shi)
    diff = (now_idx - birth_idx) % 12

    keyword, desc = CYCLE_KEYWORDS[diff]

    tenchusatsu = get_tenchusatsu(birth_year, birth_month, birth_day)
    branches = tenchusatsu["branches"]
    is_tenchusatsu_year = now_shi in branches

    return {
        "target_year": target_year,
        "now_shi": now_shi,
        "birth_shi": birth_shi,
        "cycle_position": diff,
        "keyword": keyword,
        "description": desc,
        "is_tenchusatsu_year": is_tenchusatsu_year,
        "tenchusatsu_info": tenchusatsu
    }


def get_multi_year_fortune(birth_year: int, birth_month: int, birth_day: int,
                            from_year: int, to_year: int) -> list:
    """複数年の運勢を返す"""
    return [get_year_fortune(birth_year, birth_month, birth_day, y)
            for y in range(from_year, to_year + 1)]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== 天中殺 ===")
    print(get_tenchusatsu(1963, 7, 31))
    print("\n=== 天中殺の年（過去〜未来） ===")
    tc_years = get_tenchusatsu_years(1963, 7, 31)
    print(f"  全期間: {tc_years['all_periods']}")
    print(f"  前回: {tc_years['previous_period']}")
    print(f"  現在: {tc_years['current_period']}")
    print(f"  次回: {tc_years['next_period']}")
    print("\n=== 2025-2028年の運勢 ===")
    for y in range(2025, 2029):
        f = get_year_fortune(1963, 7, 31, y)
        print(f"  {y}年: 「{f['keyword']}」({f['now_shi']}年) — {f['description']}")
