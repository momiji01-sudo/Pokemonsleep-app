import streamlit as st
import random

st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- CSS: レイアウト調整 ---
st.markdown("""
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 5px !important;
    }
    button { padding: 2px 8px !important; font-size: 0.75rem !important; }
    .stCheckbox { white-space: nowrap !important; margin-bottom: -10px !important; }
    .group-label { font-weight: bold; font-size: 0.85rem; white-space: nowrap; }
    /* 結果表示エリアの装飾 */
    .result-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.caption("Ver 7.0 - 期待値・厳選難易度判定付き")

# --- データ定義 ---
GOLD_LIST = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス"]
ALL_SKILLS = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス",
              "🔵おてつだいスピードM", "🔵食材確率アップM", "🔵スキル確率アップM", "🔵スキルレベルアップS", "🔵最大所持数アップL", "🔵最大所持数アップM",
              "⚪おてつだいスピードS", "⚪食材確率アップS", "⚪スキル確率アップS", "⚪最大所持数アップS"]

NATURE_GROUPS = {
    "おてスピ↑": [("さみしがり", "げんき↓"), ("いじっぱり", "食材↓"), ("やんちゃ", "スキル↓"), ("ゆうかん", "EXP↓")],
    "食材↑": [("ひかえめ", "おてスピ↓"), ("おっとり", "げんき↓"), ("うっかりや", "スキル↓"), ("れいせい", "EXP↓")],
    "スキル↑": [("おだやか", "おてスピ↓"), ("おとなしい", "げんき↓"), ("しんちょう", "食材↓"), ("なまいき", "EXP↓")],
    "げんき↑": [("ずぶとい", "おてスピ↓"), ("わんぱく", "食材↓"), ("のうてんき", "スキル↓"), ("のんき", "EXP↓")],
    "EXP↑": [("おくびょう", "おてスピ↓"), ("せっかち", "げんき↓"), ("ようき", "食材↓"), ("むじゃき", "スキル↓")],
    "無補正": [("てれや", ""), ("がんばりや", ""), ("すなお", ""), ("まじめ", ""), ("きまぐれ", "")]
}
ING_LIST = ['AAA', 'AAB', 'AAC', 'ABA', 'ABB', 'ABC']
ING_VALS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

# --- コールバック関数 ---
def set_nature_group(g_key, val):
    for n in NATURE_GROUPS[g_key]: st.session_state[f"n_{n[0]}"] = val
def set_all_natures(val):
    for g in NATURE_GROUPS.values():
        for n in g: st.session_state[f"n_{n[0]}"] = val
def set_all_ings(val):
    for i in ING_LIST: st.session_state[f"i_{i}"] = val

st.title("📊 ポケスリ厳選計算機")

st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_v = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

st.write("▼ 性格選択")
anc1, anc2 = st.columns(2)
anc1.button("全性格を選択", on_click=set_all_natures, args=(True,))
anc2.button("全性格を解除", on_click=set_all_natures, args=(False,))

selected_natures = []
for g_label, natures in NATURE_GROUPS.items():
    h_cols = st.columns([2, 1, 1])
    h_cols[0].markdown(f'<div class="group-label">【{g_label}】</div>', unsafe_allow_html=True)
    h_cols[1].button("全選", key=f"all_{g_label}", on_click=set_nature_group, args=(g_label, True))
    h_cols[2].button("解除", key=f"clr_{g_label}", on_click=set_nature_group, args=(g_label, False))
    for j in range(0, len(natures), 2):
        row_cols = st.columns(2)
        for k in range(2):
            if j + k < len(natures):
                name, effect = natures[j + k]
                label = f"{name} ({effect})" if effect else name
                if row_cols[k].checkbox(label, key=f"n_{name}"):
                    selected_natures.append(name)

st.write("▼ 食材配列選択")
ic1, ic2 = st.columns(2)
ic1.button("全食材を選択", on_click=set_all_ings, args=(True,))
ic2.button("全食材を解除", on_click=set_all_ings, args=(False,))
selected_ings = []
for i in range(0, len(ING_LIST), 3):
    row_cols_i = st.columns(3)
    for j in range(3):
        if i + j < len(ING_LIST):
            name = ING_LIST[i + j]
            if row_cols_i[j].checkbox(name, key=f"i_{name}"):
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
        with st.spinner('10万回のシミュレーションを実行中...'):
            it = 100000; ok = 0
            total_ing_p = sum([ING_VALS[p] for p in selected_ings])
            flat_all_n = [n[0] for g in NATURE_GROUPS.values() for n in g]
            for _ in range(it):
                if random.random() > total_ing_p: continue
                nature_sample = random.choice(flat_all_n)
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
                cb = all(req in s for req in sany) if sany else True
                if (not any([s10, s25, s50, s75, s100])) and not sany: ok += 1
                elif ca and cb: ok += 1

            prob = (ok / it) * 100
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.subheader("🏁 計算結果")
            col_res1, col_res2 = st.columns(2)
            col_res1.metric("出現確率", f"{prob:.4f} %")
            
            if prob > 0:
                expected_count = int(100 / prob)
                col_res2.metric("期待値", f"約 {expected_count:,} 匹に1匹")
                
                # 難易度アドバイス
                if prob >= 1.0:
                    st.success("🍀 厳選難易度: やさしい。比較的すぐに出会えるでしょう。")
                elif prob >= 0.1:
                    st.info("🏃 厳選難易度: 普通。粘り強く厳選すれば十分狙える範囲です。")
                elif prob >= 0.01:
                    st.warning("🔥 厳選難易度: 高い。サブレの消費を覚悟する必要があるかもしれません。")
                else:
                    st.error("💀 厳選難易度: 地獄。この個体は伝説級です。妥協案も考えましょう。")
            else:
                st.error("該当する個体は0件でした。条件が厳しすぎるようです。")
            st.markdown('</div>', unsafe_allow_html=True)
            if prob > 0: st.balloons()
