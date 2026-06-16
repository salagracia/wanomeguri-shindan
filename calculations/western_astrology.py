"""
西洋占星術（skyfield版・NASA天体データで正確計算）
"""
import os
from skyfield.api import load


# 太陽星座の特徴
SIGN_THEMES = {
    "牡羊座": "情熱・先駆・行動",
    "牡牛座": "安定・五感・蓄積",
    "双子座": "好奇心・情報・対話",
    "蟹座": "保護・感情・家族",
    "獅子座": "自己表現・輝き・誇り",
    "乙女座": "分析・奉仕・完璧",
    "天秤座": "調和・美・関係性",
    "蠍座": "深淵・変容・集中",
    "射手座": "探究・自由・哲学",
    "山羊座": "達成・規律・社会",
    "水瓶座": "革新・友愛・未来",
    "魚座": "包容・夢想・献身",
}

SIGNS = list(SIGN_THEMES.keys())

_eph = None
_ts = None


def _load_ephemeris():
    global _eph, _ts
    if _eph is None:
        _ts = load.timescale()
        # de421.bsp は最初の呼び出しでダウンロードされる
        _eph = load('de421.bsp')
    return _eph, _ts


def _lon_to_sign(lon_degrees: float) -> str:
    return SIGNS[int(lon_degrees / 30) % 12]


def get_sun_sign(year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> dict:
    """太陽星座（正確計算）"""
    eph, ts = _load_ephemeris()
    # JST -> UTC は -9 時間
    utc_hour = hour - 9
    t = ts.utc(year, month, day, utc_hour, minute)
    earth, sun = eph['earth'], eph['sun']
    pos = earth.at(t).observe(sun).apparent()
    _, lon, _ = pos.ecliptic_latlon()
    sign = _lon_to_sign(lon.degrees)
    return {
        "name": sign,
        "longitude": round(lon.degrees, 2),
        "theme": SIGN_THEMES[sign]
    }


def get_moon_sign(year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> dict:
    """月星座（正確計算）"""
    eph, ts = _load_ephemeris()
    utc_hour = hour - 9
    t = ts.utc(year, month, day, utc_hour, minute)
    earth, moon = eph['earth'], eph['moon']
    pos = earth.at(t).observe(moon).apparent()
    _, lon, _ = pos.ecliptic_latlon()
    sign = _lon_to_sign(lon.degrees)
    return {
        "name": sign,
        "longitude": round(lon.degrees, 2),
        "theme": SIGN_THEMES[sign]
    }


def get_ascendant(year: int, month: int, day: int, hour: int, minute: int = 0,
                  lat: float = 35.6762, lon: float = 139.6503) -> dict:
    """アセンダント（上昇星座）
    緯度経度のデフォルトは東京。サラさんの長崎は (32.75, 129.88)
    """
    # 簡易計算：恒星時を使って上昇黄経を算出
    import math
    eph, ts = _load_ephemeris()
    utc_hour = hour - 9
    t = ts.utc(year, month, day, utc_hour, minute)

    # Local Sidereal Time（恒星時）の概算
    gmst = t.gmst  # 時間単位
    lst = (gmst + lon / 15.0) % 24  # 度→時間に変換、観測地恒星時
    ramc = lst * 15  # MC黄経の赤経

    # 黄道傾斜
    epsilon = math.radians(23.4393)
    ramc_rad = math.radians(ramc)
    lat_rad = math.radians(lat)

    # アセンダント計算式（簡略）
    asc_rad = math.atan2(
        math.cos(ramc_rad),
        -(math.sin(ramc_rad) * math.cos(epsilon) + math.tan(lat_rad) * math.sin(epsilon))
    )
    asc_deg = math.degrees(asc_rad) % 360
    sign = _lon_to_sign(asc_deg)
    return {
        "name": sign,
        "longitude": round(asc_deg, 2),
        "theme": SIGN_THEMES[sign]
    }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== サラさん(1963-07-31 06:00 長崎) ===")
    print(f"太陽星座: {get_sun_sign(1963, 7, 31, 6, 0)}")
    print(f"月星座: {get_moon_sign(1963, 7, 31, 6, 0)}")
    print(f"アセンダント: {get_ascendant(1963, 7, 31, 6, 0, 32.75, 129.88)}")
