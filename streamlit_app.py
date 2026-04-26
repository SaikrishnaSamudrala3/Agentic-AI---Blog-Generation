import os

import requests
import streamlit as st

from src.config.languages import language_options


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Agentic Blog Generator", page_icon="AG", layout="wide")

st.title("Agentic Blog Generator")


@st.cache_data(ttl=300)
def get_supported_languages(api_base_url: str):
    response = requests.get(f"{api_base_url}/languages", timeout=5)
    response.raise_for_status()
    return [language["name"] for language in response.json()["languages"]]


try:
    supported_languages = get_supported_languages(API_BASE_URL)
except requests.RequestException:
    supported_languages = language_options()
    st.warning("Could not load supported languages from the API. Using local defaults.")

with st.sidebar:
    st.header("Generation Settings")
    topic = st.text_input("Topic", "Agentic AI in software engineering")
    language = st.selectbox("Language", supported_languages)
    audience = st.text_input("Audience", "software engineers")
    tone = st.selectbox(
        "Tone",
        ["professional", "technical", "beginner-friendly", "conversational", "executive"],
    )
    length = st.selectbox("Length", ["short", "medium", "long"])
    generate = st.button("Generate Blog", type="primary")

if generate:
    payload = {
        "topic": topic,
        "language": language,
        "audience": audience,
        "tone": tone,
        "length": length,
    }
    with st.spinner("Running agentic workflow..."):
        response = requests.post(f"{API_BASE_URL}/blogs", json=payload, timeout=300)

    if response.ok:
        st.session_state["selected_blog"] = response.json()
        st.success("Blog generated.")
    else:
        try:
            detail = response.json().get("detail", "Blog generation failed.")
        except ValueError:
            detail = "Blog generation failed."
        st.error(detail)

tab_blog, tab_research, tab_history = st.tabs(["Blog", "Research & SEO", "History"])

with tab_blog:
    selected_blog = st.session_state.get("selected_blog")
    if selected_blog:
        st.caption(f"Blog ID: {selected_blog['id']} | Status: {selected_blog['status']}")
        st.subheader(selected_blog["title"])
        st.markdown(selected_blog["content"])
        st.download_button(
            "Download Markdown",
            data=f"# {selected_blog['title']}\n\n{selected_blog['content']}",
            file_name=f"{selected_blog['seo'].get('slug', 'blog-post')}.md",
            mime="text/markdown",
        )
    else:
        st.info("Generate a blog from the sidebar to preview it here.")

with tab_research:
    selected_blog = st.session_state.get("selected_blog")
    if selected_blog:
        st.subheader("Research Notes")
        st.markdown(selected_blog.get("research_notes") or "No research notes saved.")

        st.subheader("Outline")
        st.markdown(selected_blog.get("outline") or "No outline saved.")

        st.subheader("SEO")
        seo = selected_blog.get("seo", {})
        st.json(seo)
    else:
        st.info("Research, outline, and SEO metadata appear after generation.")

with tab_history:
    try:
        history_response = requests.get(f"{API_BASE_URL}/blogs", timeout=30)
        history_response.raise_for_status()
        blogs = history_response.json()
    except requests.RequestException:
        blogs = []
        st.warning("Could not load blog history. Make sure the FastAPI server is running.")

    for blog in blogs:
        with st.container(border=True):
            st.write(f"**{blog['title']}**")
            st.caption(f"ID {blog['id']} | {blog['topic']} | {blog['created_at']}")
            col_preview, col_delete = st.columns([1, 1])
            if col_preview.button("Preview", key=f"preview-{blog['id']}"):
                st.session_state["selected_blog"] = blog
                st.rerun()
            if col_delete.button("Delete", key=f"delete-{blog['id']}"):
                requests.delete(f"{API_BASE_URL}/blogs/{blog['id']}", timeout=30)
                st.rerun()
