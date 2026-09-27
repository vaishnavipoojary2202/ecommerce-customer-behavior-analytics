import streamlit as st

st.set_page_config(
    page_title="E-Commerce Customer Behavior Analytics",
    page_icon="🛒",
    layout="wide",
)

st.title("E-Commerce Customer Behavior Analytics")
st.caption("PySpark-based customer, product and sales analytics")

st.info(
    "Dashboard implementation will be connected to the processed Parquet outputs "
    "after the analytics notebooks are completed."
)

st.subheader("Planned dashboard sections")
st.markdown(
    """
    - Customer overview
    - RFM and customer segments
    - Segment profiles
    - Product and category performance
    - Sales trends
    """
)
