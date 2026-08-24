from pathlib import Path
import streamlit as st

def hide_sidebar():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="stSidebarCollapsedControl"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True)

def page_config():
    # 1. Caminho dos arquivos de imagem
    icon_path = Path(__file__).resolve().with_name("ico.png")

    # 2. Configuração da página
    st.set_page_config(
        page_title="Barber GO",
        page_icon=str(icon_path),
        layout="centered",
        initial_sidebar_state="expanded"
    )