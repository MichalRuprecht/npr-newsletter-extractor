import requests
from bs4 import BeautifulSoup
import streamlit as st

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Newsletter Content Collector",
    page_icon="📰",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "data" not in st.session_state:
    st.session_state.data = None

# ---------------- STYLE (DARK NPR THEME) ----------------
st.markdown("""
<style>
html, body, .main {
    background-color: #0b0f14;
    color: #f5f5f5;
}
.block-container {
    max-width: 900px;
}
h1 {
    color: #e11c2a;
    font-weight: 700;
}
.card {
    background-color: #161b22;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}
label {
    font-weight: 600;
}
textarea {
    background-color: #1f2430 !important;
    color: #f5f5f5 !important;
    border-radius: 8px !important;
}
button[kind="primary"] {
    background-color: #e11c2a !important;
    border-radius: 8px !important;
    font-weight: 700;
}
.copy-btn button {
    background-color: #e11c2a !important;
    height: 46px;
    width: 100%;
    font-weight: 700;
}
.footer {
    text-align: center;
    margin-top: 30px;
    color: #c9c9c9;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("Newsletter Content Collector")
st.write("Paste the link to the story below.")

# ---------------- HELPERS ----------------
def meta(soup, prop=None, name=None):
    if prop:
        tag = soup.find("meta", property=prop)
    else:
        tag = soup.find("meta", attrs={"name": name})
    return tag["content"].strip() if tag and tag.get("content") else ""

def extract_npr(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    headline = meta(soup, prop="og:title")
    link = meta(soup, prop="og:url") or url
    teaser = meta(soup, name="description")
    photo = meta(soup, prop="og:image")

    authors_raw = meta(soup, name="cXenseParse:author")
    authors = [a.strip() for a in authors_raw.split("|")] if authors_raw else []

    if len(authors) == 1:
        teaser_author = f"{teaser}. {authors[0]} reports for NPR."
    elif len(authors) > 1:
        teaser_author = f"{teaser}. {' and '.join(authors)} report for NPR."
    else:
        teaser_author = teaser

    return {
        "Headline": headline,
        "Link": link,
        "Photo URL": photo,
        "Teaser": teaser,
        "Teaser with author": teaser_author
    }

def render_row(label, value, key):
    c1, c2 = st.columns([6, 1])
    with c1:
        st.text_area(label, value, key=f"text_{key}", height=80)
    with c2:
        st.markdown('<div class="copy-btn">', unsafe_allow_html=True)
        if st.button("Copy", key=f"copy_{key}"):
            st.session_state["_clipboard"] = value
            st.toast(f"{label} copied")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FORM (ENTER WORKS) ----------------
with st.form("collect_form"):
    url = st.text_input(
        "",
        placeholder="https://www.npr.org/...",
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Collect content")

# ---------------- ACTION ----------------
if submitted:
    if not url or "npr.org" not in url:
        st.error("Please paste a valid NPR story link.")
    else:
        try:
            st.session_state.data = extract_npr(url)
        except Exception as e:
            st.error(f"Failed to fetch story: {e}")

# ---------------- OUTPUT (PERSISTENT) ----------------
if st.session_state.data:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Collected content")

    for i, (label, value) in enumerate(st.session_state.data.items()):
        render_row(label, value, i)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
Questions? +1 (707) 412-8684<br><br>
❤️ Michal Ruprecht
</div>
""", unsafe_allow_html=True)
