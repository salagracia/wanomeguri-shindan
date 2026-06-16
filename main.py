"""
45歳からの 信頼される男 診断 メインオーケストレーター（lunar-python + skyfield統合）
"""
from datetime import date, datetime
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculations.numerology import life_path_number, birth_day_number, destiny_number_from_name, get_life_path_deep
from calculations.western_astrology import get_sun_sign, get_moon_sign, get_ascendant
from calculations.kyusei import honmei_star, gekkimei_star
from calculations.shichuusuimei import year_pillar, month_pillar, day_pillar, hour_pillar
from calculations.doubutsu_teiou import get_doubutsu_kyara, get_teiougaku, get_shusei
from calculations.personality_quiz import calculate_mbti, calculate_wd
from calculations.shinrai_otoko import calculate_shinrai_otoko
from calculations.tenchuusatsu import get_tenchusatsu, get_year_fortune, get_tenchusatsu_years, get_multi_year_fortune
from calculations.seimei_handan import seimei_handan
from pdf_generator import generate_pdf


def _build_personality(answers: dict, occult_result: dict | None = None) -> dict:
    """45歳からの 信頼される男 診断（24問×占術重みづけ・4タイプ・メイン+隠れ）

    v1.1: occult_result を渡すことで占術主・質問補強のハイブリッド判定にする。
    """
    kaika = calculate_shinrai_otoko(answers, occult_result=occult_result)

    # メインタイプ（第2章で使う）— jinsei_kaika後方互換のためキー名はそのまま
    main_compat = {
        "type": kaika["type"],
        "label": kaika["name"],
        "subtitle": kaika["tagline"],
        "summary": kaika["strength_body"],
        "strengths": [
            kaika["tagline"],
            f"「{kaika['name']}」として現場で発揮してきた力",
            "ブレない判断軸と、背中で見せる胆力",
        ],
        "weaknesses": [
            "強みが家庭で裏目に出ている可能性",
            "近い人ほど、つい後回しになる癖",
        ],
        "relationships": (
            f"あなたの隠れタイプは「{kaika['second_name']}」（{kaika['second_tagline']}）。"
            f"二つの顔を使い分けられるようになると、家庭でも仕事でも、別次元の信頼が立ち上がります。"
        ),
        "career": f"「{kaika['name']}」の強みは、肩書きや業界が変わっても、あなたの中に残り続けます。",
        "challenge": (
            f"仕事で武器になっている「{kaika['tagline']}」を、"
            f"家庭では一度オフにする練習を始めること。"
        ),
        "love_match": (
            f"妻からは今、{kaika['wife_view']}と映っている可能性があります。"
            f"これは性格の問題ではなく、強みの向きが家庭で噛み合っていないだけです。"
        ),
        "biz_match": f"「{kaika['name']}」と「{kaika['second_name']}」の二面を使い分けると、人を動かす力が一段上がります。",
        "fortune_strategy": (
            f"立て直しの一手は明快です——\n\n"
            f"{kaika['key_shift']}\n\n"
            f"派手な変化ではなく、これ一点を仕事の場ではなく『家のドアの内側』で実行する。"
            f"それが、{kaika['name']}の男にとって最も効くテコです。"
        ),
        "body": kaika["strength_body"],
        # 男性版独自フィールド（narrative_generator が直接参照）
        "strength_body": kaika["strength_body"],
        "shadow_body": kaika["shadow_body"],
        "wife_view": kaika["wife_view"],
        "key_shift": kaika["key_shift"],
    }

    # 隠れタイプ（第3章で使う）
    second_compat = {
        "type": kaika["second_type"],
        "label": kaika["second_name"],
        "subtitle": kaika["second_tagline"],
        "summary": kaika["second_strength_body"],
        "strengths": [
            kaika["second_tagline"],
            "普段は表に出ていないが確かに存在する力",
            "意識して呼び出すと一気に厚みが増す",
        ],
        "weaknesses": ["まだ十分に使われていない可能性があります"],
        "fortune_strategy": (
            f"隠れタイプ「{kaika['second_name']}」は、あなたの中に確かに眠っています。\n\n"
            f"普段はメインタイプ「{kaika['name']}」が前に出ますが、\n"
            f"意識的に「{kaika['second_tagline']}」を発揮する場面を作ると、\n"
            f"あなたの男としての厚みが立体的になります。\n\n"
            f"きっかけは小さくていい。\n"
            f"いつもと違う場所、違う温度、違う相手。\n"
            f"そこに身を置くだけで、隠れたあなたが顔を出します。"
        ),
        "body": kaika["second_strength_body"],
        "strength_body": kaika["second_strength_body"],
        "shadow_body": kaika["second_shadow_body"],
        "biz_match": f"メインタイプ「{kaika['name']}」と組み合わせて発揮しましょう。",
        "love_match": f"メインタイプ「{kaika['name']}」と組み合わせると、妻に対しても新しい顔を見せられます。",
    }

    return {
        "mbti": main_compat,
        "wd": second_compat,
        "jinsei_kaika": kaika,  # キー名は互換維持（narrative_generator が参照）
    }


def run_diagnosis(user_input: dict) -> dict:
    bd_str = user_input["birth_date"]
    year, month, day = [int(x) for x in bd_str.split("-")]
    bt = user_input.get("birth_time", "12:00")
    birth_hour = int(bt.split(":")[0])
    birth_minute = int(bt.split(":")[1]) if ":" in bt else 0

    # 出生地（デフォルト東京、サラさんは長崎）
    lat = user_input.get("lat", 35.6762)
    lon = user_input.get("lon", 139.6503)

    lp = life_path_number(year, month, day)

    # 占術データを先に計算（personality 判定で参照する）
    occult_data = {
        "numerology": {
            "life_path": lp,
            "life_path_deep": get_life_path_deep(lp["number"]),
            "birth_day": birth_day_number(day),
            "destiny": destiny_number_from_name(user_input.get("name_kana", "")),
        },
        "western_astrology": {
            "sun": get_sun_sign(year, month, day, birth_hour, birth_minute),
            "moon": get_moon_sign(year, month, day, birth_hour, birth_minute),
            "asc": get_ascendant(year, month, day, birth_hour, birth_minute, lat, lon),
        },
        "kyusei": {
            "honmei": honmei_star(year),
            "gekkimei": gekkimei_star(year, month),
        },
        "shichuusuimei": {
            "year": year_pillar(year, month, day),
            "month": month_pillar(year, month, day),
            "day": day_pillar(year, month, day),
            "hour": hour_pillar(year, month, day, birth_hour, birth_minute),
        },
        "doubutsu": get_doubutsu_kyara(year, month, day),
        "shusei": get_shusei(year, month, day),
        "teiou": get_teiougaku(year, month, day),
    }

    result = {
        **occult_data,
        # v1.1: personality 判定に占術結果を渡す
        "personality": _build_personality(user_input.get("answers", {}), occult_result=occult_data),
        "fortune": get_year_fortune(year, month, day),
        "fortune_3years": get_multi_year_fortune(year, month, day, datetime.now().year, datetime.now().year + 2),
        "tenchusatsu_years": get_tenchusatsu_years(year, month, day),
        "seimei": seimei_handan(
            user_input.get("last_name", user_input.get("name", "").split(" ")[0] if " " in user_input.get("name", "") else ""),
            user_input.get("first_name", user_input.get("name", "").split(" ")[-1] if " " in user_input.get("name", "") else user_input.get("name_kana", ""))
        ),
        "narrative": user_input.get("narrative", {}),
    }
    return result


def main():
    # 50代経営者の男性をテストデータとして使う
    # 山田太郎の占術（LP5・改革型・牡羊座）は D 挑戦タイプ寄りの設計なので、
    # 自由記述と質問回答もそれに合わせた挑戦タイプ・コードの内容にする。
    test_input = {
        "name": "山田 太郎",
        "last_name": "山田",
        "first_name": "太郎",
        "name_kana": "ヤマダタロウ",
        "birth_date": "1975-04-15",
        "birth_time": "08:00",
        "birth_place": "東京都 渋谷区",
        "lat": 35.6762,
        "lon": 139.6503,
        # 挑戦タイプ寄りの回答（D中心、A・B少しずつ混ぜて現実味を出す）
        "answers": {
            "M1": "D", "M2": "A", "M3": "D", "M4": "D", "M5": "D", "M6": "D",
            "M7": "D", "M8": "D", "M9": "D", "M10": "A", "M11": "D", "M12": "D",
            "M13": "D", "M14": "D", "M15": "D", "M16": "D", "M17": "A", "M18": "D",
            "M19": "D", "M20": "D", "M21": "D", "M22": "D", "M23": "D", "M24": "A",
        },
        "narrative": {
            "N1": "誰もやってない領域に最初に飛び込んでいる時。新規事業の立ち上げで、白板の前で一人、夜中まで構想を組み立てている時間が、いちばん夢中になれる。",
            "N2": "止まらない。動き続ければ景色は必ず変わる。これは絶対に曲げない。失敗より、立ち止まる方がよっぽど怖い。",
            "N3": "妻と並んで、未来を語り合える夫でありたい。でも実際は、家にいる時間が短くて、妻が話したいことを最後まで聞けていない気がする。",
            "N4": "家のドアを開けた瞬間、頭はまだ次の挑戦に向かっている。妻と何を話していいか、毎日少しずつ分からなくなっていく。仕事ではあれだけ動けるのに。",
        },
    }

    print("=== 計算開始 ===")
    result = run_diagnosis(test_input)

    print("\n--- 計算結果（主要） ---")
    print(f"信頼される男タイプ: {result['personality']['jinsei_kaika']['name']}")
    print(f"  - 仕事の強み: {result['personality']['jinsei_kaika']['tagline']}")
    print(f"  - 妻からの見え方: {result['personality']['jinsei_kaika']['wife_view']}")
    print(f"隠れタイプ: {result['personality']['jinsei_kaika']['second_name']}")
    print(f"動物キャラ: {result['doubutsu']['name_60']}")
    print(f"算命学主星: {result['shusei']['name']}")

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir,
        f"45歳からの信頼される男診断_{test_input['name'].replace(' ', '')}_v1.3_{datetime.now().strftime('%Y%m%d')}.pdf",
    )

    print(f"\n=== PDF生成中: {output_path} ===")
    generate_pdf(test_input, result, output_path)
    print("=== 完了 ===")


if __name__ == "__main__":
    main()
