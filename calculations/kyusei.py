"""
九星気学
本命星・月命星を算出
"""


# 九星の名称と性質
KYUSEI = {
    1: ("一白水星", "水", "深い思索・順応・柔軟。流れに乗りながら本質を掴む。"),
    2: ("二黒土星", "土", "母性・育成・堅実。じっくりと土台を作り上げる力。"),
    3: ("三碧木星", "木", "発展・若さ・行動力。新しい物事を切り拓く先駆者。"),
    4: ("四緑木星", "木", "信用・調和・整え。風のように人と人を繋ぐ調停者。"),
    5: ("五黄土星", "土", "中心・帝王・支配。強烈な存在感と統率の力。"),
    6: ("六白金星", "金", "完成・権威・尊厳。リーダーシップと天の理を体現する。"),
    7: ("七赤金星", "金", "悦・社交・楽しみ。喜びと豊かさを周囲に振りまく。"),
    8: ("八白土星", "土", "変革・継承・不動。古いものを終え、新しいものへ繋ぐ。"),
    9: ("九紫火星", "火", "知性・美・名誉。直感の光で本質を見抜く美の探求者。"),
}


def honmei_star(year: int) -> dict:
    """本命星：生年から計算
    2月節分（立春）以前生まれの場合は前年で計算。
    （本ファイルでは簡易のため誕生年で計算）
    """
    # 一白水星の年：1936, 1945, 1954, 1963, ... のように9年周期
    # 計算式：（11 - (年の各桁の合計を一桁にしたもの)）の9を法とする
    s = sum(int(d) for d in str(year))
    while s > 9:
        s = sum(int(d) for d in str(s))
    star_num = (11 - s) % 9
    if star_num == 0:
        star_num = 9
    name, element, meaning = KYUSEI[star_num]
    return {
        "number": star_num,
        "name": name,
        "element": element,
        "meaning": meaning
    }


def gekkimei_star(year: int, month: int) -> dict:
    """月命星：本命星と生まれ月から
    （簡易計算）
    """
    honmei = honmei_star(year)
    h = honmei["number"]

    # 月命星の対応表（節入り考慮なし簡易版）
    # 本命星 → 各月の月命星
    # 詳細な月命星計算は複雑なので、ここでは簡易な月別オフセット
    base = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 9}.get(h, 9)
    star_num = ((base + month - 2) - 1) % 9 + 1

    name, element, meaning = KYUSEI[star_num]
    return {
        "number": star_num,
        "name": name,
        "element": element,
        "meaning": meaning,
        "note": "簡易計算"
    }


if __name__ == "__main__":
    # サラさんのデータでテスト：1963-07-31
    h = honmei_star(1963)
    print(f"本命星: {h}")
    g = gekkimei_star(1963, 7)
    print(f"月命星: {g}")
