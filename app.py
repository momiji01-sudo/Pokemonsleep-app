import streamlit as st
import random

# デザイン設定
st.set_page_config(page_title="ポケスリ厳選計算機", layout="centered")
st.title("📊 ポケスリ厳選計算機")

# --- データ定義 ---
GOLD_SKILLS = ["きのみの数S", "おてつだいボーナス", "睡眠EXPボーナス", "スキルレベルアップM", "げんき回復ボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]
ALL_SKILLS = ["きのみの数S", "おてつだいボーナス", "おてつだいスピードM", "おてつだいスピードS", "食材確率アップM", "食材確率アップS", "スキル確率アップM", "スキル確率アップS", "スキルレベルアップM", "スキルレベルアップS", "最大所持数アップL", "最大所持数アップM", "最大所持数アップS", "げんき回復ボーナス", "睡眠EXPボーナス", "ゆめのかけらボーナス", "リサーチEXPボーナス"]
NATURE_DATA = [("さみしがり", "おてスピ▲/げんき▼"), ("いじっぱり", "おてスピ▲/食材▼"), ("やんちゃ", "おてスピ▲/スキル▼"), ("ゆうかん", "おてスピ▲/EXP▼"), ("ひかえめ", "食材▲/おてスピ▼"), ("おっとり", "食材▲/げんき▼"), ("うっかりや", "食材▲/スキル▼"), ("れいせい", "食材▲/EXP▼"), ("おだやか", "スキル▲/おてスピ▼"), ("おとなしい", "スキル▲/げんき▼"), ("しんちょう", "スキル▲/食材▼"), ("なまいき", "スキル▲/EXP▼"), ("ずぶとい", "げんき▲/おてスピ▼"), ("わんぱく", "げんき▲/食材▼"), ("のうてんき", "げんき▲/スキル▼"), ("のんき", "げんき▲/EXP▼"), ("おくびょう", "EXP▲/おてスピ▼"), ("せっかち", "EXP▲/げんき▼"), ("ようき", "EXP▲/食材▼"), ("むじゃき", "EXP▲/スキル▼"), ("てれや", "無補正"), ("がんばりや", "無補正"), ("すなお", "無補正"), ("まじめ", "無補正"), ("きまぐれ", "無補正")]
ING_PATTERNS = {'AAA': 1/9, 'AAB': 1/9, 'AAC': 1/9, 'ABA': 2/9, 'ABB': 2/9, 'ABC': 2/9}

# --- サイドバー / 設定 ---
st.header("1. 基本条件")
medal = st.selectbox("フレンドレベル（メダル）", ["なし (1〜9)", "銅 (10〜39)", "銀 (40〜99)", "金 (100〜)"], index=1)
medal_val = {"なし (1〜9)": 0, "銅 (10〜39)": 1, "銀 (40〜99)": 2, "金 (100〜)": 3}[medal]

col1, col2 = st.columns(2)
with col1:
    selected_natures = st.multiselect("性格（複数可）", [n[0] for n in NATURE_DATA])
with col2:
    selected_ings = st.multiselect("食材配列", list(ING_PATTERNS.keys()))

st.header("2. サブスキル条件")
st.subheader("枠指定 (10 / 25 / 50 / 75 / 100)")
s10 = st.multiselect("10Lv固定", ALL_SKILLS)
s25 = st.multiselect("25Lv固定", ALL_SKILLS)
s50 = st.multiselect("50Lv固定", ALL_SKILLS)
s75 = st.multiselect("75Lv固定", ALL_SKILLS)
s100 = st.multiselect("100Lv固定", ALL_SKILLS)

st.subheader("順不同（どこでもいいから入ってほしい）")
sany = st.multiselect("必須サブスキル", ALL_SKILLS)

# --- 計算ロジック ---
if st.button("計算開始 (10万回シミュレーション)", type="primary", use_container_width=True):
    if not selected_natures or not selected_ings:
        st.error("性格と食材を選択してください")
    else:
        with st.spinner('計算中...'):
            iterations = 100000
            success = 0
            total_ing_prob = sum([ING_PATTERNS[p] for p in selected_ings])
            
            for _ in range(iterations):
                if random.random() > total_ing_prob: continue
                if random.choice(NATURE_DATA)[0] not in selected_natures: continue
                
                selected = []
                def pick(pool):
                    valid = [x for x in pool if x not in selected]
                    return random.choice(valid) if valid else None

                sub10 = pick(GOLD_SKILLS if medal_val >= 1 else ALL_SKILLS); selected.append(sub10)
                sub25 = pick(GOLD_SKILLS if medal_val >= 2 else ALL_SKILLS); selected.append(sub25)
                sub50 = pick(GOLD_SKILLS if medal_val >= 3 else ALL_SKILLS); selected.append(sub50)
                sub75 = pick(ALL_SKILLS); selected.append(sub75)
                sub100 = pick(ALL_SKILLS); selected.append(sub100)
                
                # 判定
                cond_a = True
                for target, slot in zip([s10, s25, s50, s75, s100], [sub10, sub25, sub50, sub75, sub100]):
                    if target and slot not in target: cond_a = False; break
                cond_b = all(req in selected for req in sany) if sany else False
                
                if (not s10 and not s25 and not s50 and not s75 and not s100 and not sany) or cond_a or cond_b:
                    success += 1
            
            prob = success / iterations
            st.metric("出現確率", f"{prob*100:.5f} %")
            if prob > 0:
                st.write(f"**期待値:** 約 **{int(1/prob):,}** 匹に1匹")
            else:
                st.write("この条件で一致する個体は見つかりませんでした。")