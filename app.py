import streamlit as st
import random

# ページ設定
st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- 【スマホ完全強制】レイアウト & 色分けCSS ---
st.markdown("""
    <style>
    /* 1. 性格補正の改行を物理的に禁止し、省略(...)を許さない */
    [data-baseweb="tag"] {
        max-width: 5000px !important; /* 極端に大きく */
        width: auto !important;
        white-space: nowrap !important;
        display: inline-flex !important;
    }
    [data-baseweb="tag"] span {
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: unset !important;
    }

    /* 2. ボタンをスマホでも絶対に横並びにする(フレックスボックス強制) */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 8px !important;
    }
    div[data-testid="column"] {
        flex: 1 1 50% !important;
        min-width: 0 !important; /* 縮小を許可して横並びを維持 */
    }

    /* 3. サブスキルの色分け (属性セレクタでより確実に) */
    /* 金色 */
    div[data-baseweb="tag"]:has(span:contains("きのみ")),
    div[data-baseweb="tag"]:has(span:contains("おてつだいボーナス")),
    div[data-baseweb="tag"]:has(span:contains("睡眠EXP")),
    div[data-baseweb="tag"]:has(span:contains("スキルレベルアップM")),
    div[data-baseweb="tag"]:has(span:contains("げんき回復")),
    div[data-baseweb="tag"]:has(span:contains("ゆめのかけら")),
    div[data-baseweb="tag"]:has(span:contains("リサーチEXP")) {
        background-color: #ffd700 !important; /* 金 */
        color: #000 !important;
        border: 1px solid #b8860b !important;
    }
    /* 青色 (銀) */
    div[data-baseweb="tag"]:has(span:contains("M")):not(:has(span:contains("レベルアップ"))),
    div[data-baseweb="tag"]:has(span:contains("最大所持数アップL")),
    div[data-baseweb="tag"]:has(span:contains("スキルレベルアップS")) {
        background-color: #add8e6 !important; /* 水色 */
        color: #000 !important;
        border: 1px solid #4682b4 !important;
    }
    /* 白色 */
    div[data-baseweb="tag"]:has(span:contains("S")):not(:has(span:contains("きのみ"))):not(:has(span:contains("おてつだいボーナス"))):not(:has(span:contains("M"))):not(:has(span:contains("L"))) {
        background-color: #ffffff !important;
        color: #000 !important;
        border: 1px solid #ccc !important;
    }

    /* 全体のフォントサイズ微調整(スマホ用) */
    .stMultiSelect label, .stSelectbox label {
        font-size: 14px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- データ定義 ---
GOLD_LIST = ["きのみの数S", "おてつだいボーナス", "睡眠EXPボーナス", "スキルレベルアップM", "げんき回復ボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]
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

if 'sn' not in st.session_state: st.session_state.sn = []
if 'si' not in st.session_state: st.session_state.si = []

st.title("📊 ポケスリ厳選計算機")

# --- UIセクション ---
st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_v = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

st.write("▼ 性格選択")
c1, c2 = st.columns(2)
if c1.button("全選択", key="na"): st.session_state.sn = NATURE_OPTIONS
if c2.button("全解除", key="nc"): st.session_state.sn = []
sel_n = st.multiselect("性格", options=NATURE_OPTIONS, key="sn", label_visibility="collapsed")

st.write("▼ 食材配列")
c3, c4 = st.columns(2)
if c3.button("全選択", key="ia"): st.session_state.si = list(ING_PATTERNS.keys())
if c4.button("全解除", key="ic"): st.session_state.si = []
sel_i = st.multiselect("食材", list(ING_PATTERNS.keys()), key="si", label_visibility="collapsed")

st.header("2. サブスキル条件")
col1, col2, col3 = st.columns(3)
with col1:
    s10 = st.multiselect("10Lv", ALL_SKILLS)
    s75 = st.multiselect("75Lv", ALL_SKILLS)
with col2:
    s25 = st.multiselect("25Lv", ALL_SKILLS)
    s100 = st.multiselect("100Lv", ALL_SKILLS)
with col3:
    s50 = st.multiselect("50Lv", ALL_SKILLS)
sany = st.multiselect("順不同：必須スキル", ALL_SKILLS)

# --- 計算 ---
if st.button("計算開始", type="primary", use_container_width=True):
    if not sel_n or not sel_i:
        st.error("条件を選んでください")
    else:
        with st.spinner('計算中...'):
            it = 100000; ok = 0
            total_ip = sum([ING_PATTERNS[p] for p in sel_i])
            sel_n_names = [n.split(" ")[0] for n in sel_n]
            for _ in range(it):
                if random.random() > total_ip: continue
                if random.choice([n.split(" ")[0] for n in NATURE_OPTIONS]) not in sel_n_names: continue
                s = []
                def pk(p):
                    v = [x for x in p if x not in s]
                    return random.choice(v) if v else None
                v10 = pk(GOLD_LIST if medal_v >= 1 else ALL_SKILLS); s.append(v10)
                v25 = pk(GOLD_LIST if medal_v >= 2 else ALL_SKILLS); s.append(v25)
                v50 = pk(GOLD_LIST if medal_v >= 3 else ALL_SKILLS); s.append(v50)
                v75 = pk(ALL_SKILLS); s.append(v75)
                v100 = pk(ALL_SKILLS); s.append(v100)
                ca = True
                for t, v in zip([s10, s25, s50, s75, s100], [v10, v25, v50, v75, v100]):
                    if t and v not in t: ca = False; break
                cb = all(r in s for r in sany) if sany else False
                if (not any([s10, s25, s50, s75, s100, sany])) or ca or cb: ok += 1
            p = ok / it
            st.metric("出現確率", f"{p*100:.5f} %")
            if p > 0: st.info(f"期待値: 約 {int(1/p):,} 匹に1匹")
