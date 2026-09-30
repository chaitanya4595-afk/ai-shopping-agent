import logging
import os
import tempfile

import streamlit as st

from ai_shopping_agent.agent import agent

st.set_page_config(
    page_title="AI Shopping Agent",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "request_error" not in st.session_state:
    st.session_state.request_error = None

st.title("🛒 AI Shopping Agent")
st.caption(
    "A multimodal, tool-using agent that searches products, checks ratings, "
    "and executes a demo checkout only after confirmation."
)

step1, step2, step3 = st.columns(3)
with step1:
    with st.container(border=True):
        st.markdown("**1 · Search**")
        st.caption("Describe what you want or upload a product image.")
with step2:
    with st.container(border=True):
        st.markdown("**2 · Compare**")
        st.caption("The agent searches the catalog and checks ratings.")
with step3:
    with st.container(border=True):
        st.markdown("**3 · Confirm**")
        st.caption("Checkout is triggered only after you select a product.")

with st.expander("How this demo works"):
    st.markdown(
        """
        **Text path:** request → agent → product search → rating lookup → candidates  
        **Image path:** image → vision model → search intent → same product-search flow  
        **Order path:** displayed candidates → explicit user selection → demo checkout

        Product data, ratings, and demo orders are stored in SQLite. The language model
        orchestrates tools; it does not directly query or write the database.
        """
    )

with st.sidebar:
    st.header("Demo guide")
    st.markdown("Try this prompt:")
    st.code("I want organic honey under $20 with a 4.5+ rating", language=None)
    st.caption("Then reply with `order #1` or `yes` to test the checkout path.")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.request_error = None
        st.session_state.pop("pending_image", None)
        pending_path = st.session_state.pop("pending_image_path", None)
        if pending_path and os.path.exists(pending_path):
            os.remove(pending_path)
        st.rerun()

    st.divider()
    st.subheader("Shop by image")
    st.caption("Upload a product photo and the vision model will turn it into search intent.")

    uploaded_file = st.file_uploader(
        "Upload product image",
        type=["jpg", "jpeg", "png", "webp"],
    )

    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)

    if uploaded_file and st.button("Find similar products", use_container_width=True):
        suffix = os.path.splitext(uploaded_file.name)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            image_path = tmp.name

        prompt = (
            "I uploaded a product image. Please analyze it and find similar products "
            f"in the store. Image path: {image_path}"
        )
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pending_image = uploaded_file.name
        st.session_state.pending_image_path = image_path
        st.rerun()

if st.session_state.request_error:
    st.error(st.session_state.request_error)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and msg["content"].startswith("I uploaded a product image"):
            st.markdown(
                f"Searching by image: **{st.session_state.get('pending_image', 'uploaded product')}**"
            )
        else:
            st.markdown(msg["content"].replace("$", r"\$"))

if (
    st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
    and "pending_image" in st.session_state
):
    with st.chat_message("assistant"):
        try:
            st.session_state.request_error = None
            with st.spinner("Analyzing the image, searching the catalog, and checking ratings…"):
                result = agent.invoke({"messages": st.session_state.messages})
                response = result["messages"][-1].content.replace("`", "")
            st.markdown(response.replace("$", r"\$"))
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception:
            logging.getLogger(__name__).exception("Shopping request failed")
            st.session_state.request_error = "The agent could not complete that request. Please try again."
        finally:
            pending_path = st.session_state.pop("pending_image_path", None)
            if pending_path and os.path.exists(pending_path):
                os.remove(pending_path)
            st.session_state.pop("pending_image", None)
        st.rerun()

if prompt := st.chat_input("Ask for a product, price range, organic preference, or minimum rating"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            st.session_state.request_error = None
            with st.spinner("Searching and checking the best matches…"):
                result = agent.invoke({"messages": st.session_state.messages})
                response = result["messages"][-1].content.replace("`", "")
            st.markdown(response.replace("$", r"\$"))
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception:
            logging.getLogger(__name__).exception("Shopping request failed")
            st.session_state.request_error = "The agent could not complete that request. Please try again."

    st.rerun()

st.divider()
st.caption(
    "Portfolio demo · Uses a small local catalog and simulated checkout. "
    "No real payment or fulfillment occurs."
)
