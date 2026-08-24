import streamlit as st

from header.page_config import page_config, hide_sidebar
from header.navigation import navigation


def main():
    page_config()
    hide_sidebar()
    navigation()


if __name__ == "__main__":
    main()
    st.title("Dashboard")
    st.write("Welcome to the dashboard! Here you can monitor various metrics in real-time.")


    col_dashboard1, col_dashboard2, col_dashboard3, col_dashboard4 = st.columns([1, 1, 1, 1], border=True)

    with col_dashboard1:
        st.metric(label="Dashboard 1", value="Teste", delta="Teste")
    with col_dashboard2:
        st.metric(label="Dashboard 2", value="Teste", delta="Teste")
    with col_dashboard3:
        st.metric(label="Dashboard 3", value="Teste", delta="Teste")
    with col_dashboard4:
        st.metric(label="Dashboard 4", value="Teste", delta="Teste")
