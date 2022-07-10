from pandas import DataFrame
import streamlit as st

from fetch_logs import fetch_data
from transform_logs import transform_data


@st.cache()  # XXX set ttl to ~5 min for live app
def fetch_data_wrap(userToken: str):
    return fetch_data(userToken)


@st.cache(ttl=5, suppress_st_warning=True)  # XXX remove ttl for live app
def transform_data_wrap(logData):
    return transform_data(logData)


def get_data(userToken: str):
    if not userToken:
        return None
    return transform_data_wrap(fetch_data_wrap(userToken))


userToken = st.text_input(
    "arcDPS userToken:", "")
df = get_data(userToken)
"df:", df
