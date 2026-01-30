import requests
from bs4 import BeautifulSoup
import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Newsletter Content Collector",
    page_icon="📰",
    layout="centered"
)

# ---------- NPR THEME (simple + clean) ----------
st.markdown("""
<style>
    body {
        background-color: #ffffff;
    }
    .main {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #d62021; /* NPR red */
    }
    .stButton button {
        background-color: #d62021;
        color: white;
        border-radius: 6px;
        font-weight: 600;
    }
    .copy-box textarea {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.title("Newsletter Content Collector")
st.write("Paste the link to the story below.")

url = st.text_input("", placeholder="https://www.npr.org/...")

# ---------- HELPERS ----------
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

# ---------- ACTION ----------
if st.button("Collect content"):
    if not url or "npr.org" not in url:
        st.error("Please paste a valid NPR story link.")
    else:
        try:
            headline, link, photo, teaser, teaser_author = extract_npr(url)

            st.subheader("Collected content")

            st.markdown("**Headline**")
            st.text_area("", headline, key="headline")

            st.markdown("**Link**")
            st.text_area("", link, key="link")

            st.markdown("**Photo URL**")
            st.text_area("", photo, key="photo")

            st.markdown("**Teaser**")
            st.text_area("", teaser, key="teaser")

            st.markdown("**Teaser + author**")
            st.text_area("", teaser_author, key="teaser_author")

        except Exception as e:
            st.error(f"Failed to fetch story: {e}")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("""
Questions?  
+1 (707) 412-8684  
❤️ Michal Ruprecht
""")
