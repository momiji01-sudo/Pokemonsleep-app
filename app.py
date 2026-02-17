import streamlit as st
import random

st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- 【究極の強制力】標準機能を無視して横並びと省略禁止を叩き込む ---
st.markdown("""
    <style>
    /* 1. 性格タグの省略[...]を絶対に許さず、中身に合わせて幅を無限に広げる */
    div[data-baseweb="tag"] {
        max-width: none !important;
        width: auto !important;
        min-width: max-content !important;
        white-space: nowrap !important;
        display: inline-flex !important;
        flex-shrink: 0 !important;
    }
    div[data-baseweb="tag"] span {
        display: inline !important;
        text-overflow: clip !important;
        overflow: visible !important;
        white-space: nowrap !important;
    }
    /* 性格選択欄を横スクロール可能にする */
    div[data-baseweb="select"] > div:first-child {
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        display: flex !important;
    }

    /* 2. ボタンを「絶対に」横に2つ並べる（Streamlitのcolumnを無視してフレックス化） */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: space-between !important;
        width: 100% !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        width: 48% !important;
        min-width: 48% !important;
        flex: 1 1 48% !important;
    }
    button {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- データ定義 ---
GOLD_LIST = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス"]
ALL_SKILLS = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス",
              "🔵おてつだいスピードM", "🔵食材確率アップM", "🔵スキル確率アップM", "🔵スキルレベルアップS", "🔵最大所持数アップL", "🔵最大所持数アップM",
              "⚪おてつだいスピードS", "⚪食材確率アップS", "⚪スキル確率アップS", "⚪最大所持数アップS"]
NATURE_OPTIONS = ["さみしがり (スピ↑/げん↓)", "いじっぱり (スピ↑/食↓)", "やんちゃ (スピ↑/スキ↓)", "ゆうかん (スピ↑/EXP↓)",
                  "ひかえめ (食↑/スピ↓)", "おっとり (食↑/げん↓)", "うっかりや (食↑/スキ↓)", "れいせい (食↑/EXP↓)",
                  "おだやか (スキ↑/スピ↓)", "おとなしい (スキ↑/げん↓)", "しんちょう (スキ↑/食↓)", "なまいき (スキ↑/EXP↓)",
                  "ずぶとい (げん↑/スピ↓)", "わんぱく (げん↑/食↓)", "のうてんき (げん↑/スキ↓)", "のんき (げん↑/EXP↓)",
                  "おくびょう (EXP↑/スピ↓)", "せっかち (EXP↑/げん↓)", "ようき (EXP↑/食↓)", "むじゃき (EXP↑/スキ↓)",
                  "てれや (無補正)", "がんばりや (無補正)", "すなお (無補正)", "まじめ (無補正)", "きまぐれ (無補正)"]
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
st.multiselect("性格", options=NATURE_OPTIONS, key="sn", label_visibility="collapsed")

st.write("▼ 食材配列")
c3, c4 = st.columns(2)
if c3.button("全選択", key="ia"): st.session_state.si = list(ING_PATTERNS.keys())
if c4.button("全解除", key="ic"): st.session_state.si = []
st.multiselect("食材", list(ING_PATTERNS.keys()), key="si", label_visibility="collapsed")

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

if st.button("計算開始", type="primary", use_container_width=True):
    if not st.session_state.sn or not st.session_state.si:
        st.error("条件を選んでください")
    else:
        with st.spinner('計算中...'):
            it = 100000; ok = 0
            total_ip = sum([ING_PATTERNS[p] for p in st.session_state.si])
            sn_names = [n.split(" ")[0] for n in st.session_state.sn]
            for _ in range(it):
                if random.random() > total_ip: continue
                if random.choice([n.split(" ")[0] for n in NATURE_OPTIONS]) not in sn_names: continue
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
            st.metric("出現確率", f"{(ok/it)*100:.5f} %")
