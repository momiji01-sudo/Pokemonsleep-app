import streamlit as st
import random

# ページ設定
st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- 【究極カスタマイズ】改行禁止 ＆ サブスキル色分けCSS ---
st.markdown("""
    <style>
    /* 1. 性格補正を絶対に改行させず、横長に表示する */
    .stMultiSelect [data-baseweb="tag"] {
        max-width: none !important;
        width: auto !important;
        white-space: nowrap !important; /* 改行禁止 */
        overflow: visible !important;
        display: inline-flex !important;
    }
    .stMultiSelect [data-baseweb="tag"] span {
        white-space: nowrap !important;
    }

    /* 2. スマホ横並びボタンの強制維持 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    [data-testid="column"] {
        flex: 1 1 48% !important;
        min-width: 48% !important;
    }

    /* 3. サブスキルの背景色付け（ドロップダウン内と選択後） */
    /* 金スキル（黄色系） */
    span[data-baseweb="tag"]:has(span:contains("きのみの数S")), 
    span[data-baseweb="tag"]:has(span:contains("おてつだいボーナス")),
    span[data-baseweb="tag"]:has(span:contains("睡眠EXP")),
    span[data-baseweb="tag"]:has(span:contains("スキルレベルアップM")),
    span[data-baseweb="tag"]:has(span:contains("げんき回復ボーナス")),
    span[data-baseweb="tag"]:has(span:contains("ゆめのかけら")),
    span[data-baseweb="tag"]:has(span:contains("リサーチEXP")) {
        background-color: rgba(255, 215, 0, 0.3) !important; /* 薄い金 */
        border: 1px solid gold !important;
    }

    /* 銀スキル（青・銀系） */
    span[data-baseweb="tag"]:has(span:contains("M")), 
    span[data-baseweb="tag"]:has(span:contains("最大所持数アップL")) {
        /* すでに金判定されたもの以外を青くする */
        background-color: rgba(100, 149, 237, 0.2) !important; /* 薄い青 */
        border: 1px solid cornflowerblue !important;
    }
    
    /* 白スキルはデフォルトのまま（または薄いグレー） */
    </style>
""", unsafe_allow_html=True)

# --- データ定義 ---
GOLD_SKILLS = ["きのみの数S", "おてつだいボーナス", "睡眠EXPボーナス", "スキルレベルアップM", "げんき回復ボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]
# 銀スキル判定用（Mが付くものなど）
SILVER_SKILLS = ["おてつだいスピードM", "食材確率アップM", "スキル確率アップM", "スキルレベルアップS", "最大所持数アップL", "最大所持数アップM"]
ALL_SKILLS = ["きのみの数S", "おてつだいボーナス", "おてつだいスピードM", "おてつだいスピードS", "食材確率アップM", "食材確率アップS", "スキル確率アップM", "スキル確率アップS", "スキルレベルアップM", "スキルレベルアップS", "最大所持数アップL", "最大所持数アップM", "最大所持数アップS", "げんき回復ボーナス", "睡眠EXPボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]

NATURE_OPTIONS = [
    "さみしがり (おてスピ↑/げんき↓)", "いじっぱり (おてスピ↑/食材↓)", "やんちゃ (おてスピ↑/スキル↓)", "ゆうかん (おてスピ↑/EXP↓)",
    "ひかえめ (食材↑/おてスピ↓)", "おっとり (食材↑/げんき↓)", "うっかりや (食材↑/スキル↓)", "れいせい (食材↑/EXP↓)",
    "おだやか (スキル↑/おてスピ↓)", "おとなしい (スキル↑/げんき↓)", "しんちょう (スキル↑/食材↓)", "なまいき (スキル↑/EXP↓)",
    "ずぶとい (げんき↑/おてスピ↓)", "わんぱく (げんき↑/食材↓)", "のうてんき (げんき↑/スキル↓)", "のんき (げんき↑/EXP↓)",
    "おくびょう (EXP↑/おてスピ↓)", "せっかち (EXP↑/げんき↓)", "ようき (EXP↑/食材↓)", "むじゃき (EXP↑/スキル↓)",
    "てれや (無補正)", "がんばりや (無補正)", "すなお (無補正)", "まじめ (無補正)", "きまぐれ (無補正)"
]
ING_PATTERNS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

if 'selected_natures' not in st.session_state: st.session_state.selected_natures = []
if 'selected_ings' not in st.session_state: st.session_state.selected_ings = []

st.title("📊 ポケスリ厳選計算機")

# --- 1. 基本条件 ---
st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_val = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

st.write("▼ 性格選択")
col_n1, col_n2 = st.columns(2)
if col_n1.button("性格を全選択"): st.session_state.selected_natures = NATURE_OPTIONS
if col_n2.button("性格を全解除"): st.session_state.selected_natures = []
selected_natures = st.multiselect("性格を選んでください", options=NATURE_OPTIONS, key="selected_natures")

st.write("▼ 食材配列")
col_i1, col_i2 = st.columns(2)
if col_i1.button("食材を全選択"): st.session_state.selected_ings = list(ING_PATTERNS.keys())
if col_i2.button("食材を全解除"): st.session_state.selected_ings = []
selected_ings = st.multiselect("食材配列を選んでください", list(ING_PATTERNS.keys()), key="selected_ings")

# --- 2. サブスキル条件 ---
st.header("2. サブスキル条件")
c1, c2, c3 = st.columns(3)
with c1:
    s10 = st.multiselect("10Lv", ALL_SKILLS)
    s75 = st.multiselect("75Lv", ALL_SKILLS)
with c2:
    s25 = st.multiselect("25Lv", ALL_SKILLS)
    s100 = st.multiselect("100Lv", ALL_SKILLS)
with c3:
    s50 = st.multiselect("50Lv", ALL_SKILLS)
sany = st.multiselect("順不同：必須スキル", ALL_SKILLS)

# --- 計算ロジック (v4.5と同じ) ---
if st.button("計算開始 (10万回試行)", type="primary", use_container_width=True):
    if not selected_natures or not selected_ings:
        st.error("条件を選んでください")
    else:
        with st.spinner('計算中...'):
            iterations = 100000; success = 0
            total_ing_prob = sum([ING_PATTERNS[p] for p in selected_ings])
            selected_nature_names = [n.split(" ")[0] for n in selected_natures]
            for _ in range(iterations):
                if random.random() > total_ing_prob: continue
                all_n_names = [n.split(" ")[0] for n in NATURE_OPTIONS]
                if random.choice(all_n_names) not in selected_nature_names: continue
                sel = []
                def pk(p):
                    v = [x for x in p if x not in sel]
                    return random.choice(v) if v else None
                s10v = pk(GOLD_SKILLS if medal_val >= 1 else ALL_SKILLS); sel.append(s10v)
                s25v = pk(GOLD_SKILLS if medal_val >= 2 else ALL_SKILLS); sel.append(s25v)
                s50v = pk(GOLD_SKILLS if medal_val >= 3 else ALL_SKILLS); sel.append(s50v)
                s75v = pk(ALL_SKILLS); sel.append(s75v)
                s100v = pk(ALL_SKILLS); sel.append(s100v)
                ca = True
                for t, v in zip([s10, s25, s50, s75, s100], [s10v, s25v, s50v, s75v, s100v]):
                    if t and v not in t: ca = False; break
                cb = all(r in sel for r in sany) if sany else False
                if (not any([s10, s25, s50, s75, s100, sany])) or ca or cb: success += 1
            p = success / iterations
            st.metric("出現確率", f"{p*100:.5f} %")
            if p > 0: st.info(f"期待値: 約 {int(1/p):,} 匹に1匹")
