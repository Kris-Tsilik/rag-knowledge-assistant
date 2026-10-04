import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from generator import Generator
from profile import list_profiles, load_profile

st.set_page_config(page_title="RAG-конструктор")


@st.cache_resource
def get_generator(profile_name):
    return Generator(load_profile(profile_name))


names = list_profiles()
display = {n: load_profile(n)["display_name"] for n in names}

choice = st.sidebar.radio(
    "Профиль", names, format_func=lambda n: display[n], key="profile_choice"
)

if st.session_state.get("profile") != choice:
    st.session_state.profile = choice
    st.session_state.messages = []
    st.rerun()

generator = get_generator(st.session_state.profile)

st.title(display[st.session_state.profile])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

question = st.chat_input("Спроси что-нибудь...")
if question:
    st.session_state.messages.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            answer = generator.ask(question)
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "text": answer})