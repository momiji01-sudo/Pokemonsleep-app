import streamlit as st
import random

# ページ設定
st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- データ定義 ---
GOLD_SKILLS = ["きのみの数S", "おてつだいボーナス", "睡眠EXPボーナス", "スキルレベルアップM", "げんき回復ボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]
ALL_SKILLS = ["きのみの数S", "おてつだいボーナス", "おてつだいスピードM", "おてつだいスピードS", "食材確率アップM", "食材確率アップS", "スキル確率アップM", "スキル確率アップS", "スキルレベルアップM", "スキルレベルアップS", "最大所持数アップL", "最大所持数アップM", "最大所持数アップS", "げんき回復ボーナス", "睡眠EXPボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]

# 性格データ（常に補正値が見えるようにラベル自体を補正値込みの名前に統一）
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
col_n1, col_n2 = st.columns(2)
if col_n1.button("性格を全選択"):
    st.session_state.selected_natures = NATURE_OPTIONS
if col_n2.button("性格を全解除"):
    st.session_state.selected_natures
