import json
import requests
from bs4 import BeautifulSoup
import streamlit as st
import streamlit.components.v1 as components

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Newsletter Content Collector",
    page_icon="📰",
    layout="centered"
)

# ================== SESSION STATE ==================
if "data" not in st.session_state:
    st.session_state.data = None

# ================== THEME ==================
BG_COLOR = "#060913"
CARD_COLOR = "#0b1020"
INPUT_BG = "#f2f2f2"
TEXT_COLOR = "#f5f5f5"
DARK_TEXT = "#111111"
SUBTEXT_COLOR = "#b7bcc8"
BORDER_COLOR = "#394150"
BUTTON_BG = "#111827"
BUTTON_TEXT = "#f9fafb"

st.markdown(
    f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
    }}

    .block-container {{
        max-width: 980px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    h1 {{
        color: {TEXT_COLOR};
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }}

    .subtext {{
        color: {SUBTEXT_COLOR};
        margin-bottom: 1.2rem;
    }}

    .card {{
        background: transparent;
        border-radius: 18px;
        padding: 0;
        box-shadow: none;
    }}

    div[data-testid="stTextInput"] input {{
        background-color: {INPUT_BG} !important;
        color: {DARK_TEXT} !important;
        border-radius: 16px !important;
        border: none !important;
        min-height: 58px !important;
        font-size: 18px !important;
    }}

    div[data-testid="stTextArea"] textarea {{
        background-color: {INPUT_BG} !important;
        color: {DARK_TEXT} !important;
        border-radius: 16px !important;
        border: none !important;
        font-size: 18px !important;
        line-height: 1.45 !important;
        padding: 18px 20px !important;
    }}

    div[data-testid="stForm"] {{
        border: 1px solid {BORDER_COLOR};
        border-radius: 18px;
        padding: 18px;
        background: transparent;
    }}

    div[data-testid="stFormSubmitButton"] button {{
        background-color: {BUTTON_BG} !important;
        color: {BUTTON_TEXT} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 0.7rem 1.2rem !important;
    }}

    .section-title {{
        font-size: 2.2rem;
        font-weight: 800;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: {TEXT_COLOR};
    }}

    .field-label {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {TEXT_COLOR};
        margin-top: 0.25rem;
        margin-bottom: 0.3rem;
    }}

    .footer {{
        text-align: center;
        margin-top: 32px;
        color: {SUBTEXT_COLOR};
        font-size: 0.95rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ================== HEADER ==================
st.title("Newsletter Content Collector")
st.markdown(
    "<div class='subtext'>Paste the link to the story below.</div>",
    unsafe_allow_html=True
)

# ================== HELPERS ==================
def meta(soup, prop=None, name=None):
    if prop:
        tag = soup.find("meta", property=prop)
    else:
        tag = soup.find("meta", attrs={"name": name})
    return tag["content"].strip() if tag and tag.get("content") else ""


def extract_npr(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    headline = meta(soup, prop="og:title")
    link = meta(soup, prop="og:url") or url
    teaser = meta(soup, name="description")
    photo = meta(soup, prop="og:image")

    authors_raw = meta(soup, name="cXenseParse:author")
    authors = [a.strip() for a in authors_raw.split("|") if a.strip()] if authors_raw else []

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
        "Teaser with author": teaser_author,
    }


def copy_button_component(value: str, key: str):
    safe_value = json.dumps(value or "")
    html_code = f"""
    <html>
      <body style="margin:0;padding:0;background:transparent;">
        <button id="copy-btn-{key}"
          style="
            width:100%;
            height:54px;
            border-radius:14px;
            border:1px solid {BORDER_COLOR};
            background:{BUTTON_BG};
            color:{BUTTON_TEXT};
            font-weight:700;
            font-size:16px;
            cursor:pointer;
          ">
          Copy
        </button>

        <script>
          const btn = document.getElementById("copy-btn-{key}");
          const textToCopy = {safe_value};

          btn.onclick = async function() {{
            try {{
              await navigator.clipboard.writeText(textToCopy);
              btn.innerText = "Copied";
              setTimeout(() => btn.innerText = "Copy", 1000);
            }} catch (err) {{
              btn.innerText = "Failed";
              setTimeout(() => btn.innerText = "Copy", 1200);
            }}
          }};
        </script>
      </body>
    </html>
    """
    components.html(html_code, height=54)


def render_row(label, value, key):
    st.markdown(f"<div class='field-label'>{label}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([8.5, 1.5], vertical_alignment="top")

    with col1:
        line_count = max(2, min(8, (len(value or "") // 75) + 1))
        st.text_area(
            label=f"{label}_{key}",
            value=value,
            height=max(90, line_count * 30 + 26),
            label_visibility="collapsed",
            key=f"text_{key}",
        )

    with col2:
        copy_button_component(value, key)


# ================== FORM ==================
with st.form("collect_form"):
    url = st.text_input(
        "",
        placeholder="https://www.npr.org/...",
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("Collect Content!")

# ================== ACTION ==================
if submitted:
    if not url or "npr.org" not in url:
        st.error("Please paste a valid NPR story link.")
    else:
        try:
            st.session_state.data = extract_npr(url)
        except Exception as e:
            st.error(f"Failed to fetch story: {e}")

# ================== OUTPUT ==================
if st.session_state.data:
    st.markdown("<div class='section-title'>Collected content</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    for i, (label, value) in enumerate(st.session_state.data.items()):
        render_row(label, value, i)

    st.markdown("</div>", unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown(
    """
    <div class="footer">
    Questions? +1 (707) 412-8684<br><br>
    <strong>Dig up the gold for your newsletter</strong><br>
    ❤️ Michal Ruprecht from the Science Desk
    </div>
    """,
    unsafe_allow_html=True
)
