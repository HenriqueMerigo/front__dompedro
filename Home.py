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
        st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
    with col_dashboard2:
        st.metric(label="Humidity", value="50 %", delta="-0.5 %")
    with col_dashboard3:
        st.metric(label="Pressure", value="1013 hPa", delta="2 hPa")
    with col_dashboard4:
        st.metric(label="Wind Speed", value="15 mph", delta="-1 mph")
