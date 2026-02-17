import streamlit as st
import random

# ページ設定
st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- データ定義 ---
GOLD_SKILLS = ["きのみの数S", "おてつだいボーナス", "睡眠EXPボーナス", "スキルレベルアップM", "げんき回復ボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]
ALL_SKILLS = ["きのみの数S", "おてつだいボーナス", "おてつだいスピードM", "おてつだいスピードS", "食材確率アップM", "食材確率アップS", "スキル確率アップM", "スキル確率アップS", "スキルレベルアップM", "スキルレベルアップS", "最大所持数アップL", "最大所持数アップM", "最大所持数アップS", "げんき回復ボーナス", "睡眠EXPボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]

# 性格データ（表示用ラベルと内部処理用の値を分離）
NATURE_DATA = [
    {"name": "さみしがり", "label": "さみしがり (おてスピ↑/げんき↓)"},
    {"name": "いじっぱり", "label": "いじっぱり (おてスピ↑/食材↓)"},
    {"name": "やんちゃ", "label": "やんちゃ (おてスピ↑/スキル↓)"},
    {"name": "ゆうかん", "label": "ゆうかん (おてスピ↑/EXP↓)"},
    {"name": "ひかえめ", "label": "ひかえめ (食材↑/おてスピ↓)"},
    {"name": "おっとり", "label": "おっとり (食材↑/げんき↓)"},
    {"name": "うっかりや", "label": "うっかりや (食材↑/スキル↓)"},
    {"name": "れいせい", "label": "れいせい (食材↑/EXP↓)"},
    {"name": "おだやか", "label": "おだやか (スキル↑/おてスピ↓)"},
    {"name": "おとなしい", "label": "おとなしい (スキル↑/げんき↓)"},
    {"name": "しんちょう", "label": "しんちょう (スキル↑/食材↓)"},
    {"name": "なまいき", "label": "なまいき (スキル↑/EXP↓)"},
    {"name": "ずぶとい", "label": "ずぶとい (げんき↑/おてスピ↓)"},
    {"name": "わんぱく", "label": "わんぱく (げんき↑/食材↓)"},
    {"name": "のうてんき", "label": "のうてんき (げんき↑/スキル↓)"},
    {"name": "のんき", "label": "のんき (げんき↑/EXP↓)"},
    {"name": "おくびょう", "label": "おくびょう (EXP↑/おてスピ↓)"},
    {"name": "せっかち", "label": "せっかち (EXP↑/げんき↓)"},
    {"name": "ようき", "label": "ようき (EXP↑/食材↓)"},
    {"name": "むじゃき", "label": "むじゃき (EXP↑/スキル↓)"},
    {"name": "てれや", "label": "てれや (無補正)"},
    {"name": "がんばりや", "label": "がんばりや (無補正)"},
    {"name": "すなお", "label": "すなお (無補正)"},
    {"name": "まじめ", "label": "まじめ (無補正)"},
    {"name": "きまぐれ", "label": "きまぐれ (無補正)"},
]

ING_PATTERNS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

st.title("📊 ポケスリ厳選計算機")

# --- セッション状態の初期化 ---
if 'selected_natures' not in st.session_state:
    st.session_state.selected_natures = []
if 'selected_ings' not in st.session_state:
    st.session_state.selected_ings = []

# --- 1. 基本条件 ---
st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_val = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

# --- 性格選択セクション ---
st.write("▼ 性格選択")
col_n1, col_n2 = st.columns(2)
if col_n1.button("性格を全選択"):
    # 内部値(name)をセッションに格納
    st.session_state.selected_natures = [n["name"] for n in NATURE_DATA]
if col_n2.button("性格を全解除"):
    st.session_state.selected_natures = []

# format_funcを使うことで、選択肢リストはlabelを表示し、選択後はスッキリさせる
selected_natures = st.multiselect(
    "性格を選んでください", 
    options=[n["name"] for n in NATURE_DATA], 
    format_func=lambda x: next(n["label"] for n in NATURE_DATA if n["name"] == x),
    key="selected_natures"
)

# --- 食材配列セクション ---
st.write("▼ 食材配列")
col_i1, col_i2 = st.columns(2)
if col_i1.button("食材を全選択"):
    st.session_state.selected_ings = list(ING_PATTERNS.keys())
if col_i2.button("食材を全解除"):
    st.session_state.selected_ings = []

selected_ings = st.multiselect("食材配列を選んでください", list(ING_PATTERNS.keys()), key="selected_ings")

# --- 2. サブスキル条件 ---
st.header("2. サブスキル条件")
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    s10 = st.multiselect("10Lv", ALL_SKILLS)
    s75 = st.multiselect("75Lv", ALL_SKILLS)
with col_s2:
    s25 = st.multiselect("25Lv", ALL_SKILLS)
    s100 = st.multiselect("100Lv", ALL_SKILLS)
with col_s3:
    s50 = st.multiselect("50Lv", ALL_SKILLS)

st.subheader("順不同（どこでもいいから必須）")
sany = st.multiselect("このスキルは絶対持っててほしい！", ALL_SKILLS)

# --- 計算ロジック ---
if st.button("計算開始 (10万回試行)", type="primary", use_container_width=True):
    if not selected_natures or not selected_ings:
        st.error("性格と食材を少なくとも1つずつ選択してください")
    else:
        with st.spinner('シミュレーション中...'):
            iterations = 100000
            success = 0
            total_ing_prob = sum([ING_PATTERNS[p] for p in selected_ings])
            
            for _ in range(iterations):
                if random.random() > total_ing_prob: continue
                # 抽選された性格名が選択リストにあるか確認
                if random.choice([n["name"] for n in NATURE_DATA]) not in selected_natures: continue
                
                selected_skills = []
                def pick(pool):
                    valid = [x for x in pool if x not in selected_skills]
                    return random.choice(valid) if valid else None

                sub10 = pick(GOLD_SKILLS if medal_val >= 1 else ALL_SKILLS); selected_skills.append(sub10)
                sub25 = pick(GOLD_SKILLS if medal_val >= 2 else ALL_SKILLS); selected_skills.append(sub25)
                sub50 = pick(GOLD_SKILLS if medal_val >= 3 else ALL_SKILLS); selected_skills.append(sub50)
                sub75 = pick(ALL_SKILLS); selected_skills.append(sub75)
                sub100 = pick(ALL_SKILLS); selected_skills.append(sub100)
                
                cond_a = True
                for target, slot in zip([s10, s25, s50, s75, s100], [sub10, sub25, sub50, sub75, sub100]):
                    if target and slot not in target: cond_a = False; break
                cond_b = all(req in selected_skills for req in sany) if sany else False
                
                if (not any([s10, s25, s50, s75, s100, sany])) or cond_a or cond_b:
                    success += 1
            
            prob = success / iterations
            st.success(f"結果が出ました！")
            st.metric("出現確率", f"{prob*100:.5f} %")
            if prob > 0:
                st.info(f"期待値: 約 {int(1/prob):,} 匹に1匹")
            else:
                st.warning("この条件に合う個体は10万回中0回でした。")
