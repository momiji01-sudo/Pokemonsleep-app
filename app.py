import streamlit as st
import random

st.set_page_config(page_title="ポケスリ厳選計算機", page_icon="📊")

# --- CSS: ボタンの横並びを維持し、チェックボックスを押しやすくする ---
st.markdown("""
    <style>
    /* ボタンの横並び強制 */
    [data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }
    [data-testid="stHorizontalBlock"]:has(button) > div {
        flex: 1 1 50% !important;
        min-width: 0 !important;
    }
    /* チェックボックスの文字を折り返さない */
    .stCheckbox {
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- データ定義 ---
GOLD_LIST = ["🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス"]
ALL_SKILLS = [
    "🟡きのみの数S", "🟡おてつだいボーナス", "🟡睡眠EXPボーナス", "🟡スキルレベルアップM", "🟡げんき回復ボーナス", "🟡ゆめのかけらボーナス", "🟡リサーチEXPボーナス",
    "🔵おてつだいスピードM", "🔵食材確率アップM", "🔵スキル確率アップM", "🔵スキルレベルアップS", "🔵最大所持数アップL", "🔵最大所持数アップM",
    "⚪おてつだいスピードS", "⚪食材確率アップS", "⚪スキル確率アップS", "⚪最大所持数アップS"
]

NATURE_MASTER = [
    ("さみしがり", "スピ↑/げん↓"), ("いじっぱり", "スピ↑/食↓"), ("やんちゃ", "スピ↑/スキ↓"), ("ゆうかん", "スピ↑/EXP↓"),
    ("ひかえめ", "食↑/スピ↓"), ("おっとり", "食↑/げん↓"), ("うっかりや", "食↑/スキ↓"), ("れいせい", "食↑/EXP↓"),
    ("おだやか", "スキ↑/スピ↓"), ("おとなしい", "スキ↑/げん↓"), ("しんちょう", "スキ↑/食↓"), ("なまいき", "スキ↑/EXP↓"),
    ("ずぶとい", "げん↑/スピ↓"), ("わんぱく", "げん↑/食↓"), ("のうてんき", "げん↑/スキ↓"), ("のんき", "げん↑/EXP↓"),
    ("おくびょう", "EXP↑/スピ↓"), ("せっかち", "EXP↑/げん↓"), ("ようき", "EXP↑/食↓"), ("むじゃき", "EXP↑/スキ↓"),
    ("てれや", "無補正"), ("がんばりや", "無補正"), ("すなお", "無補正"), ("まじめ", "無補正"), ("きまぐれ", "無補正")
]
ING_LIST = ['AAA', 'AAB', 'AAC', 'ABA', 'ABB', 'ABC']
ING_VALS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

# --- セッション状態の初期化 ---
if 'sel_n' not in st.session_state: st.session_state.sel_n = []
if 'sel_i' not in st.session_state: st.session_state.sel_i = []

st.title("📊 ポケスリ厳選計算機")

st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_v = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

# --- 性格選択（チェックボックス版） ---
st.write("▼ 性格選択（対象にする性格にチェック）")
c1, c2 = st.columns(2)
if c1.button("性格を全選択"): st.session_state.sel_n = [n[0] for n in NATURE_MASTER]
if c2.button("性格を全解除"): st.session_state.sel_n = []

selected_natures = []
# スマホで見やすいよう2列でチェックボックスを配置
cols = st.columns(2)
for i, (name, effect) in enumerate(NATURE_MASTER):
    is_on = name in st.session_state.sel_n
    if cols[i % 2].checkbox(f"{name} ({effect})", value=is_on, key=f"n_{name}"):
        selected_natures.append(name)

# --- 食材配列（チェックボックス版） ---
st.write("▼ 食材配列選択")
c3, c4 = st.columns(2)
if c3.button("食材を全選択"): st.session_state.sel_i = ING_LIST
if c4.button("食材を全解除"): st.session_state.sel_i = []

selected_ings = []
cols_i = st.columns(3)
for i, name in enumerate(ING_LIST):
    is_on_i = name in st.session_state.sel_i
    if cols_i[i % 3].checkbox(name, value=is_on_i, key=f"i_{name}"):
        selected_ings.append(name)

st.header("2. サブスキル条件")
# サブスキルは種類が多いので、ここはマルチセレクトを継続（絵文字で判別）
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

# --- 計算ロジック ---
if st.button("計算開始", type="primary", use_container_width=True):
    if not selected_natures or not selected_ings:
        st.error("性格と食材を少なくとも1つずつ選択してください")
    else:
        with st.spinner('10万回のシミュレーション中...'):
            it = 100000; ok = 0
            total_ing_p = sum([ING_VALS[p] for p in selected_ings])
            
            for _ in range(it):
                # 1. 食材判定
                if random.random() > total_ing_p: continue
                
                # 2. 性格判定
                nature_sample = random.choice(NATURE_MASTER)[0]
                if nature_sample not in selected_natures: continue
                
                # 3. サブスキル判定
                s = []
                def pk(pool):
                    v = [x for x in pool if x not in s]
                    return random.choice(v) if v else None
                
                v10 = pk(GOLD_LIST if medal_v >= 1 else ALL_SKILLS); s.append(v10)
                v25 = pk(GOLD_LIST if medal_v >= 2 else ALL_SKILLS); s.append(v25)
                v50 = pk(GOLD_LIST if medal_v >= 3 else ALL_SKILLS); s.append(v50)
                v75 = pk(ALL_SKILLS); s.append(v75)
                v100 = pk(ALL_SKILLS); s.append(v100)
                
                # 条件チェック
                ca = True
                for target, val in zip([s10, s25, s50, s75, s100], [v10, v25, v50, v75, v100]):
                    if target and val not in target:
                        ca = False
                        break
                
                cb = all(req in s for req in sany) if sany else True
                
                if (not any([s10, s25, s50, s75, s100])) and not sany:
                    ok += 1 # 条件なし
                elif ca and cb:
                    ok += 1
            
            prob = (ok / it) * 100
            st.balloons()
            st.metric("出現確率", f"{prob:.5f} %")
            if prob > 0:
                st.info(f"期待値: 約 {int(100/prob):,} 匹に1匹")
            else:
                st.warning("現在の条件では10万匹の中に1匹も存在しませんでした。")
