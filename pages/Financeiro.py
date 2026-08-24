import streamlit as st

from header.page_config import page_config, hide_sidebar
from header.navigation import navigation

def agendamento():
    page_config()

    st.title("Financeiro")
    st.write("Esta é a página de financeiro.")
    
if __name__ == "__main__":
    agendamento()