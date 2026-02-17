import streamlit as st
import random

st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- CSS ---
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        gap: 10px !important;
    }
    .stCheckbox {
        white-space: nowrap !important;
        margin-bottom: -10px !important;
    }
    /* 見出しを少し目立たせる */
    .group-label {
        font-weight: bold;
        color: #ff4b4b;
        margin-top: 10px;
        border-bottom: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# バージョン確認用（Chromeのキャッシュ対策）
st.caption("Ver 6.4 - 2026/02/18")

# --- データ定義 ---
GOLD_LIST = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス"]
ALL_SKILLS = [
    "🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス",
    "🔵おてつだいスピードM", "🔵食材確率アップM", "🔵スキル確率アップM", "🔵スキルレベルアップS", "🔵最大所持数アップL", "🔵最大所持数アップM",
    "⚪おてつだいスピードS", "⚪食材確率アップS", "⚪スキル確率アップS", "⚪最大所持数アップS"
]

# 上昇補正ごとにグループ化
NATURE_GROUPS = {
    "【おてスピ↑】": [("さみしがり", "げんき↓"), ("いじっぱり", "食材↓"), ("やんちゃ", "スキル↓"), ("ゆうかん", "EXP↓")],
    "【食材↑】": [("ひかえめ", "おてスピ↓"), ("おっとり", "げんき↓"), ("うっかりや", "スキル↓"), ("れいせい", "EXP↓")],
    "【スキル↑】": [("おだやか", "おてスピ↓"), ("おとなしい", "げんき↓"), ("しんちょう", "食材↓"), ("なまいき", "EXP↓")],
    "【げんき↑】": [("ずぶとい", "おてスピ↓"), ("わんぱく", "食材↓"), ("のうてんき", "スキル↓"), ("のんき", "EXP↓")],
    "【EXP↑】": [("おくびょう", "おてスピ↓"), ("せっかち", "げんき↓"), ("ようき", "食材↓"), ("むじゃき", "スキル↓")],
    "【無補正】": [("てれや", ""), ("がんばりや", ""), ("すなお", ""), ("まじめ", ""), ("きまぐれ", "")]
}

# 食材：アルファベット順
ING_LIST = ['AAA', 'AAB', 'AAC', 'ABA', 'ABB', 'ABC']
ING_VALS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

if 'sel_n' not in st.session_state: st.session_state.sel_n = []
if 'sel_i' not in st.session_state: st.session_state.sel_i = []

st.title("📊 ポケスリ厳選計算機")

st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_v = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

st.write("▼ 性格選択")
nc1, nc2 = st.columns(2)
if nc1.button("性格を全選択"): 
    all_n = []
    for g in NATURE_GROUPS.values(): all_n.extend([n[0] for n in g])
    st.session_state.sel_n = all_n
if nc2.button("性格を全解除"): st.session_state.sel_n = []

selected_natures = []
# グループごとに表示
for group_name, natures in NATURE_GROUPS.items():
    st.markdown(f'<div class="group-label">{group_name}</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (name, effect) in enumerate(natures):
        is_on = name in st.session_state.sel_n
        label = f"{name} ({effect})" if effect else name
        if cols[i % 2].checkbox(label, value=is_on, key=f"n_{name}"):
            selected_natures.append(name)

st.write("▼ 食材配列（アルファベット順）")
ic1, ic2 = st.columns(2)
if ic1.button("食材を全選択"): st.session_state.sel_i = ING_LIST
if ic2.button("食材を全解除"): st.session_state.sel_i = []

selected_ings = []
cols_i = st.columns(3)
for i, name in enumerate(ING_LIST):
    is_on_i = name in st.session_state.sel_i
    if cols_i[i % 3].checkbox(name, value=is_on_i, key=f"i_{name}"):
        selected_ings.append(name)

st.header("2. サブスキル条件")
s10 = st.multiselect("10Lv", ALL_SKILLS)
s25 = st.multiselect("25Lv", ALL_SKILLS)
s50 = st.multiselect("50Lv", ALL_SKILLS)
s75 = st.multiselect("75Lv", ALL_SKILLS)
s100 = st.multiselect("100Lv", ALL_SKILLS)
sany = st.multiselect("順不同：必須スキル", ALL_SKILLS)

if st.button("計算開始", type="primary", use_container_width=True):
    if not selected_natures or not selected_ings:
        st.error("条件を選んでください")
    else:
        with st.spinner('計算中...'):
            it = 100000; ok = 0
            total_ing_p = sum([ING_VALS[p] for p in selected_ings])
            for _ in range(it):
                if random.random() > total_ing_p: continue
                # 性格判定
                flat_natures = []
                for g in NATURE_GROUPS.values(): flat_natures.extend([n[0] for n in g])
                nature_sample = random.choice(flat_natures)
                if nature_sample not in selected_natures: continue
                
                s = []
                def pk(pool):
                    v = [x for x in pool if x not in s]
                    return random.choice(v) if v else None
                v10 = pk(GOLD_LIST if medal_v >= 1 else ALL_SKILLS); s.append(v10)
                v25 = pk(GOLD_LIST if medal_v >= 2 else ALL_SKILLS); s.append(v25)
                v50 = pk(GOLD_LIST if medal_v >= 3 else ALL_SKILLS); s.append(v50)
                v75 = pk(ALL_SKILLS); s.append(v75)
                v100 = pk(ALL_SKILLS); s.append(v100)
                
                ca = True
                for t, v in zip([s10, s25, s50, s75, s100], [v10, v25, v50, v75, v100]):
                    if t and v not in t: ca = False; break
                cb = all(r in s for r in sany) if sany else True
                if (not any([s10, s25, s50, s75, s100])) and not sany: ok += 1
                elif ca and cb: ok += 1
            st.metric("出現確率", f"{(ok/it)*100:.5f} %")
