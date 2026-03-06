import html
import json
import requests
from bs4 import BeautifulSoup
import streamlit as st

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
BG_COLOR = "#f5f5f5"
CARD_COLOR = "#ffffff"
INPUT_COLOR = "#f7f7f7"
TEXT_COLOR = "#111111"
SUBTEXT_COLOR = "#666666"
ACCENT_RED = "#d62021"
BUTTON_BLUE = "#3f7bd9"
BORDER_COLOR = "#d9d9d9"

st.markdown(f"""
<style>
html, body, .main {{
    background-color: {BG_COLOR};
    color: {TEXT_COLOR};
}}

.block-container {{
    max-width: 850px;
}}

h1 {{
    color: {ACCENT_RED};
    font-weight: 700;
    text-align: center;
}}

.card {{
    background-color: {CARD_COLOR};
    border-radius: 12px;
    padding: 26px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}}

button[kind="primary"] {{
    background-color: {BUTTON_BLUE} !important;
    border-radius: 8px !important;
    font-weight: 700;
}}

.subtext {{
    text-align: center;
    color: {SUBTEXT_COLOR};
}}

.footer {{
    text-align: center;
    margin-top: 24px;
    color: {SUBTEXT_COLOR};
}}

.copy-row {{
    margin-bottom: 20px;
}}

.copy-label {{
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: {TEXT_COLOR};
}}

.copy-flex {{
    display: grid;
    grid-template-columns: 1fr 92px;
    gap: 12px;
    align-items: start;
}}

.copy-field {{
    width: 100%;
    min-height: 86px;
    resize: vertical;
    padding: 14px 16px;
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    background: {INPUT_COLOR};
    color: {TEXT_COLOR};
    font-size: 16px;
    line-height: 1.45;
    font-family: sans-serif;
    box-sizing: border-box;
}}

.copy-button {{
    height: 54px;
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    background: white;
    color: {TEXT_COLOR};
    font-weight: 700;
    font-size: 16px;
    cursor: pointer;
    transition: 0.15s ease;
}}

.copy-button:hover {{
    border-color: {ACCENT_RED};
    color: {ACCENT_RED};
}}

.copy-status {{
    font-size: 0.85rem;
    color: {SUBTEXT_COLOR};
    margin-top: 6px;
    min-height: 18px;
}}

@media (max-width: 640px) {{
    .copy-flex {{
        grid-template-columns: 1fr;
    }}

    .copy-button {{
        width: 100%;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.title("Newsletter Content Collector")
st.markdown(
    "<div class='subtext'>Paste the link to the story below.</div>",
    unsafe_allow_html=True
)
st.write("")


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
        "Teaser with author": teaser_author
    }


def render_copy_row(label, value, idx):
    escaped_label = html.escape(label)
    escaped_value = html.escape(value or "")
    js_value = json.dumps(value or "")

    st.markdown(
        f"""
        <div class="copy-row">
            <div class="copy-label">{escaped_label}</div>
            <div class="copy-flex">
                <textarea
                    id="copy-field-{idx}"
                    class="copy-field"
                >{escaped_value}</textarea>

                <div>
                    <button
                        class="copy-button"
                        type="button"
                        onclick='copyFieldValue("copy-field-{idx}", "copy-status-{idx}")'
                    >
                        Copy
                    </button>
                    <div id="copy-status-{idx}" class="copy-status"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <script>
    async function copyFieldValue(fieldId, statusId) {
        const field = document.getElementById(fieldId);
        const status = document.getElementById(statusId);

        if (!field) return;

        try {
            await navigator.clipboard.writeText(field.value);
            if (status) status.textContent = "Copied";
        } catch (err) {
            field.select();
            field.setSelectionRange(0, 999999);

            try {
                document.execCommand("copy");
                if (status) status.textContent = "Copied";
            } catch (fallbackErr) {
                if (status) status.textContent = "Copy failed";
            }
        }

        setTimeout(() => {
            if (status) status.textContent = "";
        }, 1200);
    }
    </script>
    """,
    unsafe_allow_html=True
)

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
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Collected content")

    for i, (label, value) in enumerate(st.session_state.data.items()):
        render_copy_row(label, value, i)

    st.markdown("</div>", unsafe_allow_html=True)

# ================== FOOTER ==================
st.markdown("""
<div class="footer">
Questions? +1 (707) 412-8684<br><br>
<strong>Dig up the gold for your newsletter</strong><br>
❤️ Michal Ruprecht from the Science Desk
</div>
""", unsafe_allow_html=True)
