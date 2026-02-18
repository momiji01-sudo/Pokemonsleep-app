import streamlit as st
import math

st.set_page_config(page_title="ポケスリ理論値計算機", page_icon="📊", layout="centered")

# --- CSS: Chromeで2×2、3×2を強制する ---
st.markdown("""
    <style>
    .main .block-container { max-width: 500px !important; padding-left: 10px !important; padding-right: 10px !important; }
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    
    /* 性格(2列)と食材(3列)のグリッド調整 */
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }

    button { padding: 0px 6px !important; font-size: 0.7rem !important; height: 22px !important; width: auto !important; min-width: 40px !important; }
    .stCheckbox { margin-bottom: -10px !important; }
    .stCheckbox label p { font-size: 0.75rem !important; white-space: nowrap !important; }
    
    .group-label { font-weight: bold; font-size: 0.85rem; margin-right: 5px; white-space: nowrap; }
    .section-margin { margin-top: 30px !important; margin-bottom: 5px !important; display: block; }
    
    h1 { font-size: 1.3rem !important; margin-bottom: -15px !important; }
    h2 { font-size: 1.0rem !important; margin-top: 5px !important; }
    </style>
""", unsafe_allow_html=True)

# --- データ定義 ---
NATURE_GROUPS = {
    "おてスピ↑": [("さみしがり", "スピ↑げんき↓"), ("いじっぱり", "スピ↑食材↓"), ("やんちゃ", "スピ↑スキル↓"), ("ゆうかん", "スピ↑EXP↓")],
    "食材↑": [("ひかえめ", "食材↑スピ↓"), ("おっとり", "食材↑げんき↓"), ("うっかりや", "食材↑スキル↓"), ("れいせい", "食材↑EXP↓")],
    "スキル↑": [("おだやか", "スキル↑スピ↓"), ("おとなしい", "スキル↑げんき↓"), ("しんちょう", "スキル↑食材↓"), ("なまいき", "スキル↑EXP↓")],
    "げんき↑": [("ずぶとい", "げんき↑スピ↓"), ("わんぱく", "げんき↑食材↓"), ("のうてんき", "げんき↑スキル↓"), ("のんき", "げんき↑EXP↓")],
    "EXP↑": [("おくびょう", "EXP↑スピ↓"), ("せっかち", "EXP↑げんき↓"), ("ようき", "EXP↑食材↓"), ("むじゃき", "EXP↑スキル↓")],
    "無補正": [("てれや", "無補正"), ("がんばりや", "無補正"), ("すなお", "無補正"), ("まじめ", "無補正"), ("きまぐれ", "無補正")]
}

ALL_SKILLS = [
    "🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス",
    "🔵おてつだいスピードM", "⚪おてつだいスピードS", "🔵食材確率アップM", "⚪食材確率アップS", "🔵スキル確率アップM", "⚪スキル確率アップS",
    "🔵スキルレベルアップS", "🔵最大所持数アップL", "🔵最大所持数アップM", "⚪最大所持数アップS"
]

# 幽閉チェック用ペア
SUB_PAIRS = [
    ("🔵おてつだいスピードM", "⚪おてつだいスピードS"),
    ("🔵食材確率アップM", "⚪食材確率アップS"),
    ("🔵スキル確率アップM", "⚪スキル確率アップS"),
    ("🔵最大所持数アップL", "🔵最大所持数アップM"),
    ("🔵最大所持数アップL", "⚪最大所持数アップS"),
    ("🔵最大所持数アップM", "⚪最大所持数アップS"),
    ("🟡スキルレベルアップM", "🔵スキルレベルアップS")
]

ING_LIST = ['AAA', 'AAB', 'AAC', 'ABA', 'ABB', 'ABC']
ING_VALS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

# --- ロジック ---
def get_theoretical_probability(allow_imprison):
    sel_i = [i for i in ING_LIST if st.session_state.get(f"i_{i}")]
    p_ing = sum([ING_VALS[i] for i in sel_i])
    sel_n = [n[0] for g in NATURE_GROUPS.values() for n in g if st.session_state.get(f"n_{n[0]}")]
    p_nature = len(sel_n) / 25

    filters = [st.session_state.get("s10"), st.session_state.get("s25"), st.session_state.get("s50"), st.session_state.get("s75"), st.session_state.get("s100")]
    must_have = st.session_state.get("sany", [])
    medal_level = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[st.session_state.get("medal_select")]

    match_count = 0
    total_patterns = 0
    
    def solve(depth, current_skills):
        nonlocal match_count, total_patterns
        if depth == 5:
            # 幽閉（下位が先にきて上位が後にくる）の判定
            if not allow_imprison:
                for upper, lower in SUB_PAIRS:
                    if lower in current_skills and upper in current_skills:
                        # 下位のインデックス < 上位のインデックス なら幽閉（進化不可）
                        if current_skills.index(lower) < current_skills.index(upper):
                            return

            total_patterns += 1
            if must_have and not all(s in current_skills for s in must_have): return
            for i, f in enumerate(filters):
                if f and current_skills[i] not in f: return
            match_count += 1
            return

        pool = ALL_SKILLS[0:7] if depth < medal_level else ALL_SKILLS
        available = [s for s in pool if s not in current_skills]
        for s in available:
            current_skills.append(s)
            solve(depth + 1, current_skills)
            current_skills.pop()

    if not any(filters) and not must_have and allow_imprison: p_sub = 1.0
    else:
        solve(0, [])
        p_sub = match_count / total_patterns if total_patterns > 0 else 0

    return p_ing * p_nature * p_sub

# --- UI ---
st.title("📊 ポケスリ理論値計算機")

st.header("1. 基本条件")
st.selectbox("フレンドレベル", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1, key="medal_select")
allow_imp = st.radio("幽閉（下位スキルが上位より先に来る並び）", ["幽閉あり（すべて許可）", "幽閉なし（進化不可を除外）"], horizontal=True)

st.write("▼ 性格選択 (2×2)")
anc1, anc2 = st.columns(2)
anc1.button("全性格を選択", on_click=lambda: [st.session_state.update({f"n_{n[0]}": True for g in NATURE_GROUPS.values() for n in g})])
anc2.button("全性格を解除", on_click=lambda: [st.session_state.update({f"n_{n[0]}": False for g in NATURE_GROUPS.values() for n in g})])

for g_label, natures in NATURE_GROUPS.items():
    st.markdown('<div class="section-margin"></div>', unsafe_allow_html=True)
    h_cols = st.columns([1.2, 0.4, 0.4, 2.0])
    h_cols[0].markdown(f'<div class="group-label">【{g_label}】</div>', unsafe_allow_html=True)
    h_cols[1].button("全", key=f"all_{g_label}", on_click=lambda g=g_label: [st.session_state.update({f"n_{n[0]}": True for n in NATURE_GROUPS[g]})])
    h_cols[2].button("解", key=f"clr_{g_label}", on_click=lambda g=g_label: [st.session_state.update({f"n_{n[0]}": False for n in NATURE_GROUPS[g]})])
    for j in range(0, len(natures), 2):
        r_cols = st.columns(2)
        for k in range(2):
            if j+k < len(natures):
                name, sub = natures[j+k]
                st.checkbox(f"{name}({sub})", key=f"n_{name}")

st.markdown('<div class="section-margin" style="margin-top: 40px !important;"></div>', unsafe_allow_html=True)
st.write("▼ 食材配列選択 (3×2)")
for i in range(0, 6, 3):
    r_cols_i = st.columns(3)
    for j in range(3):
        n = ING_LIST[i+j]
        st.checkbox(n, key=f"i_{n}")

st.markdown('<div class="section-margin"></div>', unsafe_allow_html=True)
st.header("2. サブスキル条件")
st.multiselect("10Lv", ALL_SKILLS, key="s10")
st.multiselect("25Lv", ALL_SKILLS, key="s25")
st.multiselect("50Lv", ALL_SKILLS, key="s50")
st.multiselect("75Lv", ALL_SKILLS, key="s75")
st.multiselect("100Lv", ALL_SKILLS, key="s100")
st.multiselect("順不同：必須スキル", ALL_SKILLS, key="sany")

if st.button("計算開始", type="primary", use_container_width=True):
    prob = get_theoretical_probability(allow_imp == "幽閉あり（すべて許可）") * 100
    if prob > 0:
        st.success(f"出現確率(理論値): {prob:.6f} %")
        st.metric("期待値", f"約 {int(100/prob):,} 匹に1匹")
    else: st.error("一致する個体は存在しません。")
