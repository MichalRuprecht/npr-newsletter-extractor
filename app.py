import requests
from bs4 import BeautifulSoup
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Newsletter Content Collector",
    page_icon="📰",
    layout="centered"
)

# ---------------- STYLE (NPR THEME) ----------------
st.markdown("""
<style>
    body, .main { background-color: #ffffff; }
    h1 { color: #d62021; }
    .stButton button {
        background-color: #d62021;
        color: white;
        font-weight: 600;
        border-radius: 6px;
    }
    .copy-btn button {
        background-color: #374151;
    }
    textarea {
        font-size: 14px;
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

    return headline, link, photo, teaser, teaser_author

def copy_row(label, value, key):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.text_area(label, value, key=key, height=70)
    with col2:
        if st.button("Copy", key=f"copy_{key}"):
            st.session_state["_clipboard"] = value
            st.toast(f"{label} copied")

# ---------------- FORM (ENTER KEY WORKS HERE) ----------------
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
            headline, link, photo, teaser, teaser_author = extract_npr(url)

            st.subheader("Collected content")

            copy_row("Headline", headline, "headline")
            copy_row("Link", link, "link")
            copy_row("Photo URL", photo, "photo")
            copy_row("Teaser", teaser, "teaser")
            copy_row("Teaser with author", teaser_author, "teaser_author")

        except Exception as e:
            st.error(f"Failed to fetch story: {e}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("""
Questions?  
+1 (707) 412-8684  

Dig up the gold for your newsletter
❤️ Michal Ruprecht from the Science Desk
""")
