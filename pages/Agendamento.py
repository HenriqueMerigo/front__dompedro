import streamlit as st

from header.page_config import page_config, hide_sidebar
from header.navigation import navigation

def agendamento():
    page_config()

    st.title("Agendamento")
    st.write("Esta é a página de agendamento.")
    
if __name__ == "__main__":
    agendamento()