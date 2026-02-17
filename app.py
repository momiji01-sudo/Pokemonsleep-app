import streamlit as st
import random

st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊", layout="centered")

# --- CSS: レイアウト微調整 ---
st.markdown("""
    <style>
    .main .block-container {
        max-width: 500px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    [data-testid="stVerticalBlock"] { gap: 0px !important; }

    button {
        padding: 0px 6px !important;
        font-size: 0.7rem !important;
        height: 22px !important;
        width: auto !important;
        min-width: 40px !important;
    }

    .stCheckbox { margin-bottom: -10px !important; }
    .stCheckbox label { padding: 0px !important; }

    .group-label {
        font-weight: bold;
        font-size: 0.85rem;
        margin-right: 5px;
        white-space: nowrap;
        display: inline-block;
    }
    
    /* グループ間の余白を強制 */
    .section-margin {
        margin-top: 30px !important;
        margin-bottom: 5px !important;
        display: block;
    }

    h1 { font-size: 1.3rem !important; margin-bottom: -15px !important; }
    h2 { font-size: 1.0rem !important; margin-top: 5px !important; }
    </style>
""", unsafe_allow_html=True)

st.caption("Ver 7.5 - グループ間・セクション間の間隔修正版")

# --- データ定義 ---
NATURE_GROUPS = {
    "おてスピ↑": [
        ("さみしがり", "スピ↑げんき↓"), ("いじっぱり", "スピ↑食材↓"), 
        ("やんちゃ", "スピ↑スキル↓"), ("ゆうかん", "スピ↑EXP↓")
    ],
    "食材↑": [
        ("ひかえめ", "食材↑スピ↓"), ("おっとり", "食材↑げんき↓"), 
        ("うっかりや", "食材↑スキル↓"), ("れいせい", "食材↑EXP↓")
    ],
    "スキル↑": [
        ("おだやか", "スキル↑スピ↓"), ("おとなしい", "スキル↑げんき↓"), 
        ("しんちょう", "スキル↑食材↓"), ("なまいき", "スキル↑EXP↓")
    ],
    "げんき↑": [
        ("ずぶとい", "げんき↑スピ↓"), ("わんぱく", "げんき↑食材↓"), 
        ("のうてんき", "げんき↑スキル↓"), ("のんき", "げんき↑EXP↓")
    ],
    "EXP↑": [
        ("おくびょう", "EXP↑スピ↓"), ("せっかち", "EXP↑げんき↓"), 
        ("ようき", "EXP↑食材↓"), ("むじゃき", "EXP↑スキル↓")
    ],
    "無補正": [
        ("てれや", "無補正"), ("がんばりや", "無補正"), 
        ("すなお", "無補正"), ("まじめ", "無補正"), ("きまぐれ", "無補正")
    ]
}

GOLD_LIST = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス"]
ALL_SKILLS = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス",
              "🔵おてつだいスピードM", "🔵食材確率アップM", "🔵スキル確率アップM", "🔵スキルレベルアップS", "🔵最大所持数アップL", "🔵最大所持数アップM",
              "⚪おてつだいスピードS", "⚪食材確率アップS", "⚪スキル確率アップS", "⚪最大所持数アップS"]
ING_LIST = ['AAA', 'AAB', 'AAC', 'ABA', 'ABB', 'ABC']
ING_VALS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

# --- コールバック ---
def set_nature_group(g_key, val):
    for n in NATURE_GROUPS[g_key]: st.session_state[f"n_{n[0]}"] = val
def set_all_natures(val):
    for g in NATURE_GROUPS.values():
        for n in g: st.session_state[f"n_{n[0]}"] = val
def set_all_ings(val):
    for i in ING_LIST: st.session_state[f"i_{i}"] = val

st.title("📊 ポケスリ厳選計算機")

# --- 1. 基本条件 ---
st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_v = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

st.write("▼ 性格選択")
anc1, anc2 = st.columns([1, 1])
anc1.button("全性格を選択", on_click=set_all_natures, args=(True,))
anc2.button("全性格を解除", on_click=set_all_natures, args=(False,))

# 性格グループ表示
for i, (g_label, natures) in enumerate(NATURE_GROUPS.items()):
    # 各グループの前に十分なスペースを挿入
    st.markdown('<div class="section-margin"></div>', unsafe_allow_html=True)
    
    h_cols = st.columns([1.2, 0.4, 0.4, 2]) 
    h_cols[0].markdown(f'<div class="group-label">【{g_label}】</div>', unsafe_allow_html=True)
    h_cols[1].button("全選", key=f"all_{g_label}", on_click=set_nature_group, args=(g_label, True))
    h_cols[2].button("解除", key=f"clr_{g_label}", on_click=set_nature_group, args=(g_label, False))

    for j in range(0, len(natures), 2):
        row_cols = st.columns(2)
        for k in range(2):
            if j + k < len(natures):
                name, sub_label = natures[j + k]
                full_display = f"{name}({sub_label})"
                st.session_state.setdefault(f"n_{name}", False)
                row_cols[k].checkbox(full_display, key=f"n_{name}")

# 食材配列の前に特別な間隔
st.markdown('<div class="section-margin" style="margin-top: 40px !important;"></div>', unsafe_allow_html=True)
st.write("▼ 食材配列選択")
ic1, ic2 = st.columns([1, 1])
ic1.button("全食材を選択", on_click=set_all_ings, args=(True,))
ic2.button("全食材を解除", on_click=set_all_ings, args=(False,))
for i in range(0, len(ING_LIST), 3):
    row_cols_i = st.columns(3)
    for j in range(3):
        if i + j < len(ING_LIST):
            n = ING_LIST[i + j]
            row_cols_i[j].checkbox(n, key=f"i_{n}")

# --- 2. サブスキル ---
st.markdown('<div class="section-margin"></div>', unsafe_allow_html=True)
st.header("2. サブスキル条件")
s10 = st.multiselect("10Lv", ALL_SKILLS)
s25 = st.multiselect("25Lv", ALL_SKILLS)
s50 = st.multiselect("50Lv", ALL_SKILLS)
s75 = st.multiselect("75Lv", ALL_SKILLS)
s100 = st.multiselect("100Lv", ALL_SKILLS)
sany = st.multiselect("順不同：必須スキル", ALL_SKILLS)

if st.button("計算開始", type="primary", use_container_width=True):
    sel_n = [n[0] for g in NATURE_GROUPS.values() for n in g if st.session_state.get(f"n_{n[0]}")]
    sel_i = [i for i in ING_LIST if st.session_state.get(f"i_{i}")]
    
    if not sel_n or not sel_i:
        st.error("条件を選んでください")
    else:
        with st.spinner('計算中...'):
            it = 100000; ok = 0
            total_ing_p = sum([ING_VALS[p] for p in sel_i])
            for _ in range(it):
                if random.random() > total_ing_p: continue
                nature_sample = random.choice([n[0] for g in NATURE_GROUPS.values() for n in g])
                if nature_sample not in sel_n: continue
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
                cb = all(req in s for req in sany) if sany else True
                if (not any([s10, s25, s50, s75, s100])) and not sany: ok += 1
                elif ca and cb: ok += 1

            prob = (ok / it) * 100
            st.success(f"出現確率: {prob:.4f} % / 期待値: 約 {int(100/prob if prob > 0 else 0):,} 匹に1匹")
