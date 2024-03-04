from os import write
import sys

import pandas as pd
import requests
import streamlit as st

from process_logs import filter_log_data, transform_log


@st.cache_data(max_entries=1000)
def _fetch_log_data(log_id: str):
    data_response = requests.get(f"https://dps.report/getJson?id={log_id}")
    data_response.raise_for_status()
    d = data_response.json()["players"][0]
    for k in d.keys():
        st.write(k)
        # st.write(type(d[k]))
    st.write(d["groupBuffsActive"])
    st.write(d["groupBuffs"])
    return transform_log(filter_log_data(data_response.json()), log_id)


@st.cache_data(ttl=120)
def fetch_log_list(userToken: str):
    response = requests.get(f"https://dps.report/getUploads?userToken={userToken}")
    response.raise_for_status()
    json = response.json()
    max_pages = json["pages"]
    uploads = json["uploads"]
    for page in range(1, 5):
        if page > max_pages:
            break
        response = requests.get(
            f"https://dps.report/getUploads?userToken={userToken}&page={page+1}"
        )
        response.raise_for_status()
        uploads.extend(response.json()["uploads"])
    return [upload["id"] for upload in uploads]


# @st.cache_data(max_entries=3)
def fetch_logs(log_list):
    progress_bar = st.progress(0)
    log_data_list = pd.DataFrame()
    num_logs = len(log_list)
    for index, log_id in enumerate(log_list):
        progress_bar.progress(index / num_logs)
        log_data_list = pd.concat([log_data_list, _fetch_log_data(log_id)])

    # XXX streamlit caching does not work with multiple threads...
    # import threading
    # def fetch_log_thread_func(data_list, idx, log_metadata):
    #     data_list[idx] = fetch_log(log_metadata)
    # Fetch all data in multiple threads
    # data_list = [None] * len(uploads)
    # thread_list = []
    # for idx, log in enumerate(uploads):
    #     thread = threading.Thread(
    #         target=fetch_log_thread_func, args=[data_list, idx, log])
    #     thread = add_script_run_ctx(thread)
    #     thread_list.append(thread)
    #     thread.start()
    # for t in thread_list:
    #     t.join()
    # for data in data_list:
    #     log_data = pd.concat([log_data, data])

    log_data_list = log_data_list.sort_values("timeStart").reset_index(drop=True)
    progress_bar.progress(100)
    progress_bar.empty()
    return log_data_list


if __name__ == "__main__":
    # log_list = [fetch_log_list(sys.argv[1])[0]]
    log_id = fetch_log_list(sys.argv[1])[0]
    data_response = requests.get(f"https://dps.report/getJson?id={log_id}")
    data_response.raise_for_status()
    d = data_response.json()
    import json

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)
