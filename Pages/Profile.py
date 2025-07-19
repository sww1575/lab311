import streamlit as st

if 'name' not in st.session_state:
    st.session_state.name = ""

if 'name' in st.session_state:
    st.write(st.session_state.name)

name = st.text_input("name")
if name not in st.session_state.name:
    st.write(name)
    st.session_state.name = name