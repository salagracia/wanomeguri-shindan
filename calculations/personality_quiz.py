"""
性格診断質問＋詳細プロファイル（v3.2 拡張版）
石野さんアプリの18問を採用、判定軸を多角化
- MBTI 16パーソナリティ（4軸×3問=12問）
- ウェルスダイナミクス 8タイプ（4問でWD8択）
- エニアグラム 9タイプ
- RIASEC職業興味 6種
- 5つの愛の言語
- VAK感覚優位
- アタッチメント 4タイプ
"""

# ============= 質問データ =============
# 各質問にtagsで判定軸を指定。複数軸を判定可能。
ALL_QUESTIONS = [
    # Q1-3 : MBTI E/I (3問)
    {
        "id": "Q1", "category": "personality",
        "question": "ぽっかり空いた休日。あなたが「あー今日はこれだな」と自然に選ぶ過ごし方は？",
        "options": {
            "A": ("友達と急に集まって、ワイワイ飲んだりカフェ巡り", {"EI": "E"}),
            "B": ("一人で本やNetflixに没頭して、誰とも話さず充電", {"EI": "I"}),
            "C": ("前から気になってた展示・ライブ・新しい街を散策", {"EI": "E"}),
            "D": ("部屋を片付けたり、溜まってた手続きを一気に終わらせる", {"EI": "I"}),
        }
    },
    {
        "id": "Q2", "category": "personality",
        "question": "10人の飲み会、席が決まっていない。あなたが自然に座るのは？",
        "options": {
            "A": ("真ん中。誰とでも話せる席が居心地いい", {"EI": "E"}),
            "B": ("端っこ。話したい人と深く話せる位置", {"EI": "I"}),
            "C": ("幹事の隣。場をうまく回す側に回りたい", {"EI": "E", "EnT": "DealMaker"}),
            "D": ("どこでもいい。誰かが指定してくれたらそこ", {"EI": "I"}),
        }
    },
    {
        "id": "Q3", "category": "personality",
        "question": "一日ヘトヘトに疲れた夜。どう回復する？",
        "options": {
            "A": ("友達に電話して2時間しゃべる", {"EI": "E", "LL": "Time"}),
            "B": ("お風呂に長く浸かって、ストレッチして寝る", {"EI": "I", "VAK": "K"}),
            "C": ("好きな音楽や動画でゆったり過ごす", {"VAK": "Au"}),
            "D": ("散歩や運動でリセット", {"VAK": "K"}),
        }
    },

    # Q4-6 : MBTI S/N (3問)
    {
        "id": "Q4", "category": "personality",
        "question": "上司から「これやっといて」と新しいタスクを振られた。最初に何をする？",
        "options": {
            "A": ("ゴールと締切と評価基準を明確にする", {"SN": "S", "JP": "J"}),
            "B": ("ググって類似事例とテンプレートを探す", {"SN": "S", "RIASEC": "I"}),
            "C": ("過去にやった人に話を聞きに行く", {"SN": "S", "EI": "E"}),
            "D": ("とりあえず手を動かして、分からなくなったら考える", {"SN": "N", "JP": "P"}),
        }
    },
    {
        "id": "Q5", "category": "personality",
        "question": "学生のころ、テストで「これは苦じゃない」と思えた科目は？",
        "options": {
            "A": ("数学・物理。論理が積み上がる感覚が好きだった", {"SN": "N", "RIASEC": "I"}),
            "B": ("国語・英語。言葉の裏のニュアンスを掴むのが楽しかった", {"SN": "N", "RIASEC": "A"}),
            "C": ("美術・音楽・体育。身体や感性で表現する科目", {"SN": "S", "RIASEC": "A", "VAK": "K"}),
            "D": ("社会・歴史。人間ドラマと因果関係が面白かった", {"SN": "N", "RIASEC": "S"}),
            "E": ("実験・実習・調理。手を動かして結果が出るやつ", {"SN": "S", "RIASEC": "R"}),
        }
    },
    {
        "id": "Q6", "category": "personality",
        "question": "情報を取り入れるとき、どちらに惹かれますか？",
        "options": {
            "A": ("具体的な事実・データ・実体験", {"SN": "S"}),
            "B": ("可能性・直感・物事の本質や意味", {"SN": "N"}),
        }
    },

    # Q7-9 : MBTI T/F (3問)
    {
        "id": "Q7", "category": "personality",
        "question": "チームミーティング、意見が真っ向対立。会議室の空気が凍ってる。あなたは？",
        "options": {
            "A": ("データと論理で、相手の論を丁寧に崩す", {"TF": "T"}),
            "B": ("「両方の意見、いいとこあるよね」と統合案を出す", {"TF": "F", "EnT": "DealMaker"}),
            "C": ("黙って観察して、後から個別に意見を伝える", {"EI": "I", "TF": "F"}),
            "D": ("「とりあえず一回試してみよう」と実行に倒す", {"JP": "P", "EnT": "Trader"}),
        }
    },
    {
        "id": "Q8", "category": "personality",
        "question": "一緒に過ごしてて「この人とは合わない」と心が閉じる瞬間。それはどんな相手？",
        "options": {
            "A": ("約束を平気で破る、時間にルーズな人", {"TF": "T", "ENNEA": "E1"}),
            "B": ("表面的で、本音を見せない人", {"TF": "F", "ENNEA": "E4"}),
            "C": ("弱い立場の人を見下す人", {"TF": "F", "ENNEA": "E2"}),
            "D": ("自分の話ばかりで、人の話を聞かない人", {"TF": "F", "ENNEA": "E9"}),
        }
    },
    {
        "id": "Q9", "category": "personality",
        "question": "誰かを評価するとき、より大事なのは？",
        "options": {
            "A": ("仕事の成果・能力・実績", {"TF": "T"}),
            "B": ("人柄・思いやり・誠実さ", {"TF": "F"}),
        }
    },

    # Q10-12 : MBTI J/P (3問)
    {
        "id": "Q10", "category": "personality",
        "question": "予定の立て方として、好ましいのは？",
        "options": {
            "A": ("事前に計画を立てて実行する", {"JP": "J"}),
            "B": ("その時の状況や気分で柔軟に対応", {"JP": "P"}),
        }
    },
    {
        "id": "Q11", "category": "personality",
        "question": "締め切りに対する姿勢は？",
        "options": {
            "A": ("早めに片付けて余裕を持つ", {"JP": "J"}),
            "B": ("ギリギリに集中力を発揮するタイプ", {"JP": "P"}),
        }
    },
    {
        "id": "Q12", "category": "personality",
        "question": "パートナーと気まずい雰囲気。あなたが取りがちな行動は？",
        "options": {
            "A": ("その場で全部話し合って、解決するまで離れない", {"JP": "J", "ATT": "At-Sec"}),
            "B": ("一旦距離を取って、頭を冷やしてから話す", {"JP": "J", "ATT": "At-Av"}),
            "C": ("何かサプライズや行動で、気持ちで埋め合わせる", {"TF": "F", "LL": "Act"}),
            "D": ("時間が経てば自然に戻ると、放っておく", {"JP": "P", "ATT": "At-Av"}),
        }
    },

    # Q13 : 愛の言語 (5LL)
    {
        "id": "Q13", "category": "love_language",
        "question": "大切な人の誕生日。「何かしてあげたい」と思ったとき、自然に選ぶアクションは？",
        "options": {
            "A": ("一緒に過ごす一日をプランニングする", {"LL": "Time"}),
            "B": ("手紙やメッセージで気持ちを言葉にする", {"LL": "Word"}),
            "C": ("ハグしたり、手をつないだり、近くにいる", {"LL": "Touch"}),
            "D": ("欲しがってたものをサプライズでプレゼント", {"LL": "Gift"}),
            "E": ("普段やってる家事や雑務を全部代わりにやる", {"LL": "Act"}),
        }
    },

    # Q14 : エニアグラム (怒りトリガー)
    {
        "id": "Q14", "category": "enneagram",
        "question": "普段は穏やかなあなたが、内側から怒りで震えるのはどんなとき？",
        "options": {
            "A": ("自分の大事な人が傷つけられたとき", {"ENNEA": "E2", "ATT": "At-Sec"}),
            "B": ("不正・嘘・裏切りを目撃したとき", {"ENNEA": "E1"}),
            "C": ("自分の領域や時間を一方的に侵されたとき", {"ENNEA": "E5", "EI": "I"}),
            "D": ("自分のプライド・誇りを踏みにじられたとき", {"ENNEA": "E3", "ENNEA": "E8"}),
        }
    },

    # Q15 : 価値観
    {
        "id": "Q15", "category": "values",
        "question": "月末、口座にちょっと余裕がある。何に使う？",
        "options": {
            "A": ("旅行・体験・ライブなど、思い出に残ること", {"ENNEA": "E7", "EnT": "Star"}),
            "B": ("服・コスメ・インテリアなど、見た目を整えるもの", {"ENNEA": "E3", "VAK": "V"}),
            "C": ("本・講座・スキルアップなど、自分への投資", {"ENNEA": "E5", "RIASEC": "I"}),
            "D": ("投資・貯金・将来のために蓄える", {"ENNEA": "E6", "EnT": "Accumulator"}),
        }
    },

    # Q16 : チーム役割 (WD判定)
    {
        "id": "Q16", "category": "wd",
        "question": "5人のチームで何かを成し遂げる場面。あなたが自然にハマる役割は？",
        "options": {
            "A": ("ビジョンを語って全員を引っ張る人", {"EnT": "Star", "MBTI_axis": "EJ"}),
            "B": ("全体を俯瞰して、抜けや遅れを管理する人", {"EnT": "Lord", "MBTI_axis": "TJ"}),
            "C": ("メンバーのモチベを保って、空気を整える人", {"EnT": "Supporter", "MBTI_axis": "FJ"}),
            "D": ("自分の専門領域を徹底的に磨いて貢献する人", {"EnT": "Mechanic", "MBTI_axis": "TP"}),
            "E": ("新しいアイデアを出し続ける人", {"EnT": "Creator", "MBTI_axis": "NP"}),
        }
    },

    # Q17 : ミス後感情 (エニアグラム)
    {
        "id": "Q17", "category": "enneagram",
        "question": "仕事で大きなミス、または大事な人を傷つけた後。最初に身体を駆け抜ける感情は？",
        "options": {
            "A": ("自分への怒り。「なぜできなかった」が最初", {"ENNEA": "E1"}),
            "B": ("周囲への申し訳なさ。「迷惑かけた」が先", {"ENNEA": "E2"}),
            "C": ("不安。「これからどうしよう」が頭を支配する", {"ENNEA": "E6"}),
            "D": ("解決モード。感情は一旦置いて、リカバリ策を考え始める", {"ENNEA": "E3", "EnT": "Trader"}),
        }
    },

    # Q18 : ウェルスダイナミクス (8択・本命)
    {
        "id": "Q18", "category": "wd",
        "question": "明日から「自分で何かやって食ってけ」と言われたら、どんな方向に動く？",
        "options": {
            "A": ("自分の作品やコンテンツで世界観を売る", {"EnT": "Creator"}),
            "B": ("SNSやコミュニティで人を集めて拡散ビジネス", {"EnT": "Star"}),
            "C": ("ニッチな専門スキルで企業に高単価で請負う", {"EnT": "Mechanic"}),
            "D": ("影響力を作って、ブランド化していく", {"EnT": "Star"}),
            "E": ("人を育てる教室・コーチング・スクール", {"EnT": "Supporter"}),
            "F": ("投資やデータ分析で、リターンを最大化する", {"EnT": "Accumulator"}),
            "G": ("プロジェクト統括として、複数事業を回す", {"EnT": "Lord"}),
            "H": ("大規模に組織を作って、業界そのものを動かす", {"EnT": "Lord"}),
        }
    },
]


# ============= 自由記述質問（男性版：4問） =============
# 仕様書「男性版診断_構成仕様書.md」§4 に準拠。
# N4は男性版で追加。「原因の解明」の素材として第6章で使う。
NARRATIVE_QUESTIONS = [
    {
        "id": "N1",
        "question": "仕事の没頭体験：時間を忘れるほど夢中になれるのは、どんな仕事の瞬間ですか？",
        "hint": "・何をしている時か／どんな手応えがあるか／終わった後に残るのは達成感？充足感？",
        "max_length": 2000,
    },
    {
        "id": "N2",
        "question": "譲れない信念：「これだけは絶対に曲げない」と思っている価値観・信条は？",
        "hint": "・何を大事にしているか／なぜ絶対なのか（原体験）／守ったことで得たもの・失ったもの",
        "max_length": 2000,
    },
    {
        "id": "N3",
        "question": "家族（妻）に対して、本当はどうありたいですか？",
        "hint": "・理想の自分像／今の自分とのギャップ／妻に何を渡せている、何を渡せていないと感じるか",
        "max_length": 2000,
    },
    {
        "id": "N4",
        "question": "最近、うまくいかない・空回りすると感じるのは、どんな場面ですか？",
        "hint": "・仕事／家庭／自分自身、どこで感じるか／その時、頭の中で何が起きているか／本音では何が引っかかっているか",
        "max_length": 2000,
    },
]


# ============= MBTI詳細プロファイル (既存16タイプ) =============
MBTI_PROFILES = {
    "ENFP": {"label": "情熱の伝道者 / The Campaigner",
             "summary": "可能性と人への愛で世界を動かす、直感的なエネルギーの源。",
             "strengths": ["創造性と発想力が豊か", "人を励まし、希望を見せる才能", "未来志向で楽観的", "多様な分野に好奇心", "コミュニケーション能力が高い"],
             "weaknesses": ["計画的に物事を進めるのが苦手", "細部や反復作業に飽きやすい", "感情の波が大きい", "「ノー」と言うのが難しい", "未完了が多い"],
             "relationships": "温かく開放的。深く理解されたい願望が強い。",
             "career": "教育・カウンセリング・芸術・コーチング・起業家・作家・YouTuber等。",
             "challenge": "1つのことを最後まで完遂する練習。具体的なゴール設定と小さな締切。",
             "love_match": "INFJ／INTJ／ENFJと相性◎。深い対話と新しい視点を共有できる相手。",
             "biz_match": "ISTJ／INTJが補完関係。地に足のついた実務家と組むと最強。"},
    "ENFJ": {"label": "教育者・調和の指導者", "summary": "人の可能性を引き出し、共に成長する道を導く。",
             "strengths": ["カリスマ性", "共感力", "人を導く力", "情熱", "理想主義"],
             "weaknesses": ["自己犠牲しがち", "批判に弱い", "完璧主義", "他人優先で疲弊", "感情的"],
             "relationships": "深く相手を理解し、人の成長を喜ぶ。",
             "career": "教師・カウンセラー・コーチ・牧師・人事。",
             "challenge": "自分自身のケアを後回しにしない。",
             "love_match": "INFP・ISFP と相性◎。", "biz_match": "ISTP・INTP が補完関係。"},
    "INFP": {"label": "理想主義者・詩人", "summary": "深い価値観と内なる世界を大切にする魂。",
             "strengths": ["深い共感力", "創造性", "誠実さ", "価値観の明確さ", "他者への配慮"],
             "weaknesses": ["現実逃避しがち", "批判に過敏", "完璧主義で動けない", "孤立しやすい", "決断を先延ばし"],
             "relationships": "深い理解と魂レベルの繋がりを求める。",
             "career": "作家・カウンセラー・芸術家・心理学者。", "challenge": "理想と現実のバランス。",
             "love_match": "ENFJ・ENTJ と相性◎。", "biz_match": "ESTJ・ENTJ が補完関係。"},
    "INFJ": {"label": "提唱者・予言者", "summary": "深い洞察と使命感で人々を導く稀有な存在。",
             "strengths": ["洞察力", "使命感", "創造性", "決意の固さ", "理想主義"],
             "weaknesses": ["燃え尽きやすい", "他人の問題を抱える", "批判に弱い", "完璧主義", "孤独"],
             "relationships": "少数の深い関係を好む。",
             "career": "セラピスト・作家・教師・スピリチュアルリーダー。",
             "challenge": "境界線を保ち、現実的な行動計画を立てる。",
             "love_match": "ENFP・ENTP と相性◎。", "biz_match": "ESTP・ESTJ が補完関係。"},
    "ENTP": {"label": "革新の発想家", "summary": "常識を疑い、新しい解決策と未来を発明する。",
             "strengths": ["革新性", "議論好き", "適応力", "知的好奇心", "リーダーシップ"],
             "weaknesses": ["飽きっぽい", "細部弱い", "口論好き", "感情に鈍感", "未完了多い"],
             "relationships": "知的刺激のある関係を好む。", "career": "起業家・コンサル・発明家・弁護士。",
             "challenge": "アイデアを実行に移す。",
             "love_match": "INFJ・INTJ と相性◎。", "biz_match": "ISTJ・ISFJ が補完関係。"},
    "ENTJ": {"label": "司令官・統率者", "summary": "ビジョンを掲げ、組織と人を動かす。",
             "strengths": ["リーダーシップ", "戦略的思考", "決断力", "効率性", "自信"],
             "weaknesses": ["短気", "感情無視", "頑固", "支配的", "完璧主義"],
             "relationships": "尊敬できる相手と対等な関係を求める。",
             "career": "経営者・CEO・政治家・将軍。", "challenge": "他者の感情に配慮する。",
             "love_match": "INFP・INTP と相性◎。", "biz_match": "ISFP・ISFJ が補完関係。"},
    "INTJ": {"label": "建築家・戦略家", "summary": "長期ビジョンを設計し、淡々と実現する。",
             "strengths": ["戦略性", "独立性", "決意", "創造性", "知性"],
             "weaknesses": ["傲慢", "感情表現弱い", "完璧主義", "批判的", "孤立"],
             "relationships": "知的に深い関係を求める。",
             "career": "科学者・戦略家・建築家・投資家。", "challenge": "感情を表現する。",
             "love_match": "ENFP・ENTP と相性◎。", "biz_match": "ESFP・ESFJ が補完関係。"},
    "INTP": {"label": "論理学者・思索家", "summary": "真理を追究し、独自の理論を構築する。",
             "strengths": ["分析力", "独創性", "客観性", "好奇心", "適応力"],
             "weaknesses": ["先延ばし", "社交弱い", "感情無視", "実務弱い", "完璧主義"],
             "relationships": "知的会話と独立を尊重する。",
             "career": "科学者・哲学者・プログラマー・教授。", "challenge": "実用的に物事を完成させる。",
             "love_match": "ENTJ・ENFJ と相性◎。", "biz_match": "ESTJ・ESFJ が補完関係。"},
    "ESFP": {"label": "エンターテイナー", "summary": "今この瞬間を楽しみ、人を笑顔にする太陽。",
             "strengths": ["社交性", "実用性", "観察力", "楽天性", "人を喜ばせる力"],
             "weaknesses": ["計画弱い", "学業苦手", "感情的", "ストレス耐性低い", "退屈に弱い"],
             "relationships": "楽しさと愛情の表現を大切にする。",
             "career": "俳優・営業・イベント企画・教師。", "challenge": "長期計画を立てる。",
             "love_match": "ISFJ・ISTJ と相性◎。", "biz_match": "INTJ・ENTJ が補完関係。"},
    "ESFJ": {"label": "世話役・コミュニティの要", "summary": "人を支え、調和を育てる温かい存在。",
             "strengths": ["協調性", "忠誠心", "実用性", "面倒見", "責任感"],
             "weaknesses": ["他人優先", "批判過敏", "保守的", "自己犠牲", "承認欲求"],
             "relationships": "家族や仲間を大切にする。",
             "career": "看護師・教師・人事・カウンセラー。", "challenge": "自分のニーズを大切に。",
             "love_match": "ISFP・ISTP と相性◎。", "biz_match": "INTP・ENTP が補完関係。"},
    "ESTP": {"label": "起業家・実行家", "summary": "瞬発力と現場感で道を切り開く行動派。",
             "strengths": ["行動力", "適応力", "実用性", "観察力", "社交性"],
             "weaknesses": ["短気", "計画弱い", "退屈嫌い", "リスク好き", "感情薄い"],
             "relationships": "刺激と楽しさを共有したい。",
             "career": "起業家・営業・トレーダー・パイロット。", "challenge": "長期視点を持つ。",
             "love_match": "ISFJ・ISTJ と相性◎。", "biz_match": "INFJ・INTJ が補完関係。"},
    "ESTJ": {"label": "管理者・実務リーダー", "summary": "秩序と効率で組織を動かす責任者。",
             "strengths": ["責任感", "組織力", "忠誠心", "実用性", "決断力"],
             "weaknesses": ["頑固", "感情無視", "批判的", "変化嫌い", "支配的"],
             "relationships": "明確で安定した関係を好む。",
             "career": "管理職・軍人・警察・経営者。", "challenge": "柔軟性を持つ。",
             "love_match": "ISFP・INFP と相性◎。", "biz_match": "INFP・INTP が補完関係。"},
    "ISFP": {"label": "芸術家・冒険家", "summary": "繊細な感性で美と自由を表現する。",
             "strengths": ["創造性", "感受性", "誠実さ", "観察力", "柔軟性"],
             "weaknesses": ["優柔不断", "ストレス弱い", "競争嫌い", "計画弱い", "自己批判"],
             "relationships": "穏やかで自由な関係を好む。",
             "career": "芸術家・デザイナー・看護師・職人。", "challenge": "意見を主張する。",
             "love_match": "ESFJ・ESTJ と相性◎。", "biz_match": "ENTJ・ENFJ が補完関係。"},
    "ISFJ": {"label": "守護者・支援者", "summary": "静かな愛で大切な人を守り続ける。",
             "strengths": ["責任感", "忠誠心", "観察力", "実用性", "思いやり"],
             "weaknesses": ["自己犠牲", "批判過敏", "変化嫌い", "自己主張弱い", "完璧主義"],
             "relationships": "家族や仲間に深い愛情を注ぐ。",
             "career": "看護師・教師・秘書・社会福祉。", "challenge": "自分のニーズを優先する。",
             "love_match": "ESFP・ESTP と相性◎。", "biz_match": "ENTP・ENFP が補完関係。"},
    "ISTP": {"label": "職人・分析家", "summary": "手と頭を使い、実用的な解決を生む。",
             "strengths": ["実用性", "柔軟性", "観察力", "問題解決力", "冷静さ"],
             "weaknesses": ["プライベート", "感情表現弱い", "長期計画弱い", "退屈嫌い", "リスク好き"],
             "relationships": "自由と尊重を求める。",
             "career": "エンジニア・職人・整備士・パイロット。", "challenge": "感情を表現する。",
             "love_match": "ESFJ・ESTJ と相性◎。", "biz_match": "ENFJ・ENTJ が補完関係。"},
    "ISTJ": {"label": "実直な管理者", "summary": "信頼と継続で社会を支える縁の下の力持ち。",
             "strengths": ["責任感", "信頼性", "実用性", "組織力", "忠誠心"],
             "weaknesses": ["頑固", "変化嫌い", "感情表現弱い", "批判的", "ストレス溜めやすい"],
             "relationships": "安定と信頼を重視する。",
             "career": "会計士・管理職・公務員・教師。", "challenge": "柔軟性を持つ。",
             "love_match": "ESFP・ENFP と相性◎。", "biz_match": "ENFP・ENTP が補完関係。"},
}


# ============= WD詳細プロファイル =============
WD_PROFILES = {
    "Creator": {"label": "クリエイター（創造者）", "subtitle": "震雷の戦略",
                "summary": "ゼロから1を生み出す発明家。新しい価値の源泉。",
                "strengths": ["斬新なアイデアを生み出す", "革新的な視点と直感", "未来を見通す力", "プロトタイプ作りが得意", "他者を巻き込むビジョン"],
                "weaknesses": ["細部の詰めが苦手", "ルーティン作業を嫌う", "完了より新規を求める", "コミュニケーション偏りがち", "感情の波"],
                "fortune_strategy": "自分の閃きを形にする時間を確保する。1人で考え込むより、信頼できる仲間と話す中で価値が形になる。",
                "biz_match": "Trader・Lord・Mechanic とパートナーを組むと最強。",
                "love_match": "Supporter・DealMaker と相性◎。"},
    "Star": {"label": "スター（表現者）", "subtitle": "離火の戦略",
             "summary": "人を魅了して影響を広げる表現者。光を放つ存在。",
             "strengths": ["カリスマ性", "表現力", "人気を呼ぶ力", "舞台度胸", "情熱"],
             "weaknesses": ["注目欲求", "傷つきやすい", "実務薄い", "完璧主義", "他者依存"],
             "fortune_strategy": "ステージ・YouTube・SNSで光を放つ。",
             "biz_match": "Mechanic・Accumulator が補完。", "love_match": "DealMaker・Trader と相性◎。"},
    "Supporter": {"label": "サポーター（支援者）", "subtitle": "兌沢の戦略",
                  "summary": "人を励まし機会をつなぐ繋ぎ手。",
                  "strengths": ["人を励ます力", "ネットワーク力", "共感力", "コーチング", "情報通"],
                  "weaknesses": ["自己主張弱い", "他人優先", "燃え尽き", "孤立しやすい", "ノーが言えない"],
                  "fortune_strategy": "コミュニティを作り、人をつなぐ役を担う。",
                  "biz_match": "Creator・Star が補完。", "love_match": "Creator・Star と相性◎。"},
    "DealMaker": {"label": "ディールメーカー（交渉者）", "subtitle": "坎水の戦略",
                  "summary": "人と人、機会と機会を結ぶ調停者。",
                  "strengths": ["交渉力", "人間関係", "直感", "タイミング感覚", "場の空気を読む"],
                  "weaknesses": ["優柔不断", "ストレス溜めやすい", "感情に左右", "結論先延ばし", "他人優先"],
                  "fortune_strategy": "人と人の間に立つ場を作る。",
                  "biz_match": "Lord・Accumulator が補完。", "love_match": "Supporter・Star と相性◎。"},
    "Trader": {"label": "トレーダー（目利き）", "subtitle": "艮山の戦略",
               "summary": "価値を見極めて適切に交換する目利き。",
               "strengths": ["タイミング感覚", "市場感覚", "決断力", "リスク管理", "実行力"],
               "weaknesses": ["短期視点", "感情を表に出さない", "焦りやすい", "孤独", "完璧主義"],
               "fortune_strategy": "市場の流れを読み、適切な時に動く。",
               "biz_match": "Creator・Star が補完。", "love_match": "Supporter・Mechanic と相性◎。"},
    "Accumulator": {"label": "アキュムレーター（蓄積者）", "subtitle": "震雷地戦略",
                    "summary": "地道に積み上げ財を育てる職人。",
                    "strengths": ["継続力", "信頼性", "実務力", "計画性", "誠実さ"],
                    "weaknesses": ["保守的", "変化嫌い", "リスク回避", "発想弱い", "頑固"],
                    "fortune_strategy": "長期目線で積み立てる。",
                    "biz_match": "Star・Creator が補完。", "love_match": "DealMaker・Lord と相性◎。"},
    "Lord": {"label": "ロード（統治者）", "subtitle": "坤地の戦略",
             "summary": "仕組みを設計し組織を動かす指揮官。",
             "strengths": ["組織力", "戦略性", "規律", "数値感覚", "統率力"],
             "weaknesses": ["共感弱い", "頑固", "支配的", "感情無視", "完璧主義"],
             "fortune_strategy": "システム化と仕組み化。",
             "biz_match": "DealMaker・Supporter が補完。", "love_match": "Mechanic・Accumulator と相性◎。"},
    "Mechanic": {"label": "メカニック（職人）", "subtitle": "巽風の戦略",
                 "summary": "細部を磨き完璧に仕上げる職人。",
                 "strengths": ["品質追求", "完成力", "技術力", "細部観察", "粘り強さ"],
                 "weaknesses": ["完璧主義", "コミュ弱い", "プロセス遅い", "変化嫌い", "新規苦手"],
                 "fortune_strategy": "自分の専門領域を深め、職人として尖る。",
                 "biz_match": "Star・Trader が補完。", "love_match": "Star・Lord と相性◎。"},
}


# ============= 補助プロファイル =============
ENNEAGRAM_NAMES = {
    "E1": "改革者（完璧主義）", "E2": "援助者（人を助ける）", "E3": "達成者（成功志向）",
    "E4": "個性的（深い感情）", "E5": "観察者（知の探究）", "E6": "忠実者（安定志向）",
    "E7": "熱中者（楽しみ追求）", "E8": "挑戦者（強さと正義）", "E9": "調停者（調和重視）"
}

RIASEC_NAMES = {
    "R": "現実的（手仕事・技術・実務）", "I": "研究的（探究・分析・知性）",
    "A": "芸術的（創造・表現・美）", "S": "社会的（教育・支援・対人）",
    "EE": "企業的（リーダー・営業・起業）", "C": "慣習的（管理・組織・規律）"
}

LL_NAMES = {
    "Time": "クオリティタイム（共有する時間）", "Word": "肯定の言葉（褒め・感謝）",
    "Touch": "身体的タッチ（触れる・抱きしめる）", "Gift": "贈り物（サプライズ）",
    "Act": "サービス行動（家事・代行）"
}

VAK_NAMES = {
    "V": "視覚優位（見て学ぶ）", "Au": "聴覚優位（聞いて学ぶ）",
    "K": "体感覚優位（やって学ぶ）"
}

ATT_NAMES = {
    "At-Sec": "安定型（健全な関係を築く）", "At-Av": "回避型（距離を保つ）",
    "At-Anx": "不安型（依存しやすい）", "At-Fea": "恐れ型（傷つきを恐れる）"
}


# ============= 計算ロジック =============
def calculate_all(answers: dict) -> dict:
    """全質問の回答から総合判定"""
    scores = {
        "EI": {"E": 0, "I": 0},
        "SN": {"S": 0, "N": 0},
        "TF": {"T": 0, "F": 0},
        "JP": {"J": 0, "P": 0},
        "EnT": {"Creator": 0, "Star": 0, "Supporter": 0, "DealMaker": 0,
                "Trader": 0, "Accumulator": 0, "Lord": 0, "Mechanic": 0},
        "ENNEA": {f"E{i}": 0 for i in range(1, 10)},
        "RIASEC": {"R": 0, "I": 0, "A": 0, "S": 0, "EE": 0, "C": 0},
        "LL": {"Time": 0, "Word": 0, "Touch": 0, "Gift": 0, "Act": 0},
        "VAK": {"V": 0, "Au": 0, "K": 0},
        "ATT": {"At-Sec": 0, "At-Av": 0, "At-Anx": 0, "At-Fea": 0},
    }

    for q in ALL_QUESTIONS:
        ans = answers.get(q["id"])
        if ans and ans in q["options"]:
            tags = q["options"][ans][1]
            for axis, value in tags.items():
                if axis in scores and value in scores[axis]:
                    scores[axis][value] += 1

    # MBTI判定
    mbti_type = ""
    mbti_type += "E" if scores["EI"]["E"] >= scores["EI"]["I"] else "I"
    mbti_type += "S" if scores["SN"]["S"] > scores["SN"]["N"] else "N"
    mbti_type += "T" if scores["TF"]["T"] > scores["TF"]["F"] else "F"
    mbti_type += "J" if scores["JP"]["J"] > scores["JP"]["P"] else "P"
    mbti_profile = MBTI_PROFILES.get(mbti_type, {})

    # WD判定（最高スコア）
    wd_top = max(scores["EnT"], key=scores["EnT"].get)
    wd_profile = WD_PROFILES.get(wd_top, {})

    # エニアグラム（最高スコア）
    ennea_top = max(scores["ENNEA"], key=scores["ENNEA"].get)

    # RIASEC（最高スコア）
    riasec_top = max(scores["RIASEC"], key=scores["RIASEC"].get)

    # 愛の言語（最高スコア）
    ll_top = max(scores["LL"], key=scores["LL"].get) if any(scores["LL"].values()) else "Time"

    # VAK（最高スコア）
    vak_top = max(scores["VAK"], key=scores["VAK"].get) if any(scores["VAK"].values()) else "V"

    # アタッチメント（最高スコア）
    att_top = max(scores["ATT"], key=scores["ATT"].get) if any(scores["ATT"].values()) else "At-Sec"

    return {
        "mbti": {"type": mbti_type, "scores": scores["EI"] | scores["SN"] | scores["TF"] | scores["JP"],
                 **mbti_profile},
        "wd": {"type": wd_top, "scores": scores["EnT"], **wd_profile},
        "enneagram": {"type": ennea_top, "name": ENNEAGRAM_NAMES.get(ennea_top, ""), "scores": scores["ENNEA"]},
        "riasec": {"type": riasec_top, "name": RIASEC_NAMES.get(riasec_top, ""), "scores": scores["RIASEC"]},
        "love_language": {"type": ll_top, "name": LL_NAMES.get(ll_top, ""), "scores": scores["LL"]},
        "vak": {"type": vak_top, "name": VAK_NAMES.get(vak_top, ""), "scores": scores["VAK"]},
        "attachment": {"type": att_top, "name": ATT_NAMES.get(att_top, ""), "scores": scores["ATT"]},
    }


# ============= 後方互換 =============
MBTI_QUESTIONS = [q for q in ALL_QUESTIONS if q["category"] == "personality"][:8]
WD_QUESTIONS = [q for q in ALL_QUESTIONS if q["category"] == "wd"]


def calculate_mbti(answers: dict) -> dict:
    """互換用：MBTIのみ返す"""
    all_result = calculate_all(answers)
    return all_result["mbti"]


def calculate_wd(answers: dict) -> dict:
    """互換用：WDのみ返す"""
    all_result = calculate_all(answers)
    return all_result["wd"]


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    # サラさんENFP想定でテスト
    sara_answers = {q["id"]: "A" for q in ALL_QUESTIONS}
    sara_answers.update({
        "Q1": "A", "Q2": "A", "Q3": "A",  # E
        "Q4": "D", "Q5": "B", "Q6": "B",  # N
        "Q7": "B", "Q8": "B", "Q9": "B",  # F
        "Q10": "B", "Q11": "B", "Q12": "C",  # P + LL=Act
        "Q13": "E",  # LL=Act
        "Q14": "A",  # E2 + Sec
        "Q15": "A",  # E7 + Star
        "Q16": "E",  # Creator
        "Q17": "B",  # E2
        "Q18": "A",  # Creator
    })
    result = calculate_all(sara_answers)
    for k, v in result.items():
        print(f"=== {k} ===")
        print(f"  type: {v.get('type', '')}")
        print(f"  name: {v.get('name', v.get('label', ''))}")
