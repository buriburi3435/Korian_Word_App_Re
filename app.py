import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import tempfile

# =========================
# 音声再生関数
# =========================
def play_sound(text):
    tts = gTTS(text=text, lang="ko")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, autoplay=True)

# =========================
# CSV読み込み
# =========================
@st.cache_data
def load_words():
    return pd.read_csv("words.csv")

df = load_words()

# =========================
# セッション初期化
# =========================
if "word" not in st.session_state:
    st.session_state.word = None

if "options" not in st.session_state:
    st.session_state.options = None

if "answered" not in st.session_state:
    st.session_state.answered = False

if "wrong_words" not in st.session_state:
    st.session_state.wrong_words = []

# =========================
# タイトル
# =========================
st.title("🇰🇷 韓国語単語学習アプリ")

# =========================
# モード選択
# =========================
mode = st.radio("モード選択", ["学習モード", "復習モード"])

# =========================
# データソース切替
# =========================
if mode == "復習モード":
    if len(st.session_state.wrong_words) == 0:
        st.info("復習する単語がありません 🎉")
        st.stop()
    source_df = pd.DataFrame(st.session_state.wrong_words)
else:
    source_df = df

# =========================
# データチェック
# =========================
if len(source_df) < 4:
    st.warning("単語が4つ以上必要です")
    st.stop()

# =========================
# 問題生成
# =========================
if st.session_state.word is None:
    st.session_state.word = source_df.sample(1).iloc[0]

if st.session_state.options is None:
    w = st.session_state.word

    others = source_df[source_df["japanese"] != w["japanese"]]

    if len(others) < 3:
        others = df[df["japanese"] != w["japanese"]]

    opts = others.sample(3)["japanese"].tolist()
    opts.append(w["japanese"])
    random.shuffle(opts)

    st.session_state.options = opts

w = st.session_state.word

# =========================
# 問題表示（韓国語）
# =========================
st.markdown(f"""
<h1 style='text-align:center'>{w['korean']}</h1>
""", unsafe_allow_html=True)

# =========================
# 4択（回答専用）
# =========================
cols = st.columns(2)

for i, opt in enumerate(st.session_state.options):
    if cols[i % 2].button(opt, use_container_width=True, disabled=st.session_state.answered):

        st.session_state.answered = True

        if opt == w["japanese"]:
            st.success("正解！")
        else:
            st.error(f"不正解 😢 正解: {w['japanese']}")

            if w.to_dict() not in st.session_state.wrong_words:
                st.session_state.wrong_words.append(w.to_dict())

# =========================
# 発音ボタン（完全分離）
# =========================
st.markdown("### 🔊 発音")

if st.button("韓国語を再生", key=f"audio_{w['korean']}"):
    play_sound(w["korean"])

# =========================
# romanization（回答後表示）
# =========================
if st.session_state.answered:
    st.markdown(
        f"<p style='text-align:center; color:gray; font-size:20px'>{w['romanization']}</p>",
        unsafe_allow_html=True
    )

# =========================
# 次の問題
# =========================
if st.session_state.answered:
    if st.button("次の問題"):
        st.session_state.word = None
        st.session_state.options = None
        st.session_state.answered = False
        st.rerun()