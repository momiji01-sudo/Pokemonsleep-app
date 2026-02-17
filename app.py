import streamlit as st
import random

# ページ設定
st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- スマホで補正値が省略されないための魔法のスタイル ---
st.markdown("""
    <style>
    /* 選択済みのラベルが省略(濃縮)されないようにする */
    .stMultiSelect [data-baseweb="tag"] {
        max-width: 1000px !important;
        white-space: normal !important;
    }
    /* ボタンの余白調整 */
    div.stButton > button {
        width: 100%;
        padding: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- データ定義 ---
GOLD_SKILLS = ["きのみの数S", "おてつだいボーナス", "睡眠EXPボーナス", "スキルレベルアップM", "げんき回復ボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]
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
col_n1, col_n2 = st.columns(2) # ボタンを横並びに配置
if col_n1.button("性格を全選択"):
    st.session_state.selected_natures = NATURE_OPTIONS
if col_n2.button("性格を全解除"):
    st.session_state.selected_natures = []

selected_natures = st.multiselect(
    "性格を選んでください", 
    options=NATURE_OPTIONS, 
    key="selected_natures"
)

# --- 食材配列セクション ---
st.write("▼ 食材配列")
col_i1, col_i2 = st.columns(2) # ボタンを横並びに配置
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
            total_
