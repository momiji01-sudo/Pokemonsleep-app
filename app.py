import streamlit as st
import math

st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊", layout="centered")

# --- CSS (v7.5のスタイルを継承) ---
st.markdown("""
    <style>
    .main .block-container { max-width: 500px !important; padding-left: 10px !important; padding-right: 10px !important; }
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    button { padding: 0px 6px !important; font-size: 0.7rem !important; height: 22px !important; width: auto !important; min-width: 40px !important; }
    .stCheckbox { margin-bottom: -10px !important; }
    .group-label { font-weight: bold; font-size: 0.85rem; margin-right: 5px; white-space: nowrap; display: inline-block; }
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

GOLD_SKILLS = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス"]
SILVER_WHITE_SKILLS = ["🔵おてつだいスピードM", "🔵食材確率アップM", "🔵スキル確率アップM", "🔵スキルレベルアップS", "🔵最大所持数アップL", "🔵最大所持数アップM", "⚪おてつだいスピードS", "⚪食材確率アップS", "⚪スキル確率アップS", "⚪最大所持数アップS"]
ALL_SKILLS = GOLD_SKILLS + SILVER_WHITE_SKILLS

ING_LIST = ['AAA', 'AAB', 'AAC', 'ABA', 'ABB', 'ABC']
ING_VALS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

# --- ロジック関数 ---
def get_theoretical_probability():
    # 1. 食材配列の確率
    sel_i = [i for i in ING_LIST if st.session_state.get(f"i_{i}")]
    p_ing = sum([ING_VALS[i] for i in sel_i])

    # 2. 性格の確率 (全25種から選択数)
    sel_n = [n[0] for g in NATURE_GROUPS.values() for n in g if st.session_state.get(f"n_{n[0]}")]
    p_nature = len(sel_n) / 25

    # 3. サブスキルの確率 (理論計算)
    # ユーザー指定条件
    filters = [st.session_state.get("s10"), st.session_state.get("s25"), st.session_state.get("s50"), st.session_state.get("s75"), st.session_state.get("s100")]
    must_have = st.session_state.get("sany", [])
    medal_level = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[st.session_state.get("medal_select", "なし (1〜9)")]

    # 全ての組み合わせを網羅的に判定（または順列計算）
    # 理論ベースの場合、全パターン 17*16*15*14*13 通りを考慮
    # ここでは計算負荷を考慮し、正確な組合せ確率を算出
    
    match_count = 0
    total_patterns = 0
    
    # 簡易的な確率計算のための再帰的探索（10-100Lvの5枠）
    def solve(depth, current_skills):
        nonlocal match_count, total_patterns
        if depth == 5:
            total_patterns += 1
            # 順不同（必須）チェック
            if must_have and not all(skill in current_skills for skill in must_have):
                return
            # 各枠の固定条件チェック
            for i, f in enumerate(filters):
                if f and current_skills[i] not in f:
                    return
            match_count += 1
            return

        # その枠で選べるスキルのプール
        pool = GOLD_SKILLS if depth < medal_level else ALL_SKILLS
        available = [s for s in pool if s not in current_skills]
        
        # 枝刈り：もし残りの枠で必須スキルを埋められないなら終了
        remaining_slots = 5 - depth
        needed_must = [m for m in must_have if m not in current_skills]
        if len(needed_must) > remaining_slots:
            return

        # 確率の重みは一律（1/プール数）
        for s in available:
            current_skills.append(s)
            solve(depth + 1, current_skills)
            current_skills.pop()

    # サブスキルが指定されていない場合は1.0
    if not any(filters) and not must_have:
        p_sub = 1.0
    else:
        # 高速化のため、全列挙ではなく数理的に算出（簡略版ロジック）
        # ※本来は超幾何分布等を使うが、ポケスリは「枠ごとにプールが変わる」ため全列挙が確実
        # ただし17P5=742,560通りなので、瞬時に終わる
        solve(0, [])
        p_sub = match_count / total_patterns if total_patterns > 0 else 0

    return p_ing * p_nature * p_sub

# --- UI コールバック ---
def set_nature_group(g_key, val):
    for n in NATURE_GROUPS[g_key]: st.session_state[f"n_{n[0]}"] = val
def set_all_natures(val):
    for g in NATURE_GROUPS.values():
        for n in g: st.session_state[f"n_{n[0]}"] = val
def set_all_ings(val):
    for i in ING_LIST: st.session_state[f"i_{i}"] = val

# --- UI 構築 ---
st.title("📊 ポケスリ理論値計算機")
st.caption("Ver 8.0 - 理論確率ベース / シミュレーション廃止")

st.header("1. 基本条件")
st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1, key="medal_select")

st.write("▼ 性格選択")
anc1, anc2 = st.columns([1, 1])
anc1.button("全性格を選択", on_click=set_all_natures, args=(True,))
anc2.button("全性格を解除", on_click=set_all_natures, args=(False,))

for g_label, natures in NATURE_GROUPS.items():
    st.markdown('<div class="section-margin"></div>', unsafe_allow_html=True)
    h_cols = st.columns([1.2, 0.4, 0.4, 2]) 
    h_cols[0].markdown(f'<div class="group-label">【{g_label}】</div>', unsafe_allow_html=True)
    h_cols[1].button("全選", key=f"all_{g_label}", on_click=set_nature_group, args=(g_label, True))
    h_cols[2].button("解除", key=f"clr_{g_label}", on_click=set_nature_group, args=(g_label, False))
    for j in range(0, len(natures), 2):
        row_cols = st.columns(2)
        for k in range(2):
            if j + k < len(natures):
                name, sub = natures[j + k]
                st.checkbox(f"{name}({sub})", key=f"n_{name}")

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
    with st.spinner('全パターンから理論値を算出中...'):
        prob = get_theoretical_probability() * 100
        if prob > 0:
            st.success(f"出現確率(理論値): {prob:.6f} %")
            st.metric("期待値", f"約 {int(100/prob):,} 匹に1匹")
        else:
            st.error("この条件に一致する個体は存在しません。")
