import concurrent.futures
import sys
import threading

import pandas as pd
import requests
import streamlit as st
from streamlit.scriptrunner import add_script_run_ctx, get_script_run_ctx

# logList.keys()=dict_keys([
#   'pages'
#   'totalUploads'
#   'userToken'
#   'uploads'
# ])

_RELEVANT_KEYS_METADATA = [
    # logList['uploads'][0].keys()=dict_keys([
    "id",
    "permalink",
    "uploadTime",
    "encounterTime",
    #  'generator'
    #  'generatorId'
    #  'generatorVersion'
    #  'language'
    #  'languageId'
    #  'evtc'
    #  'players' The player list is also part or the dataset
    #  'encounter'
    #  'report'
    #  'tempApiId'
    # ])
]

_RELEVANT_KEYS_DATA = [
    "timeStart",
    "timeEnd",
    "duration",
    "players",
]

_RELEVANT_KEYS_DATA_PLAYERS = [
    "account",
    "group",
    "hasCommanderTag",
    "profession",
    "support",
    # "squadBuffsActive", XXX TBD
    # "extHealingStats", XXX TBD
    # "extBarrierStats", XXX TBD
    "name",
    # "healing", XXX this is either 10 or 0 -> not usefull
    "dpsAll",
    "statsAll",
    "outgoingHealing"
]


def explode_apply(df: pd.DataFrame, column: str):
    return pd.concat([df.drop(columns=[column]), df.explode(
        column)[column].apply(pd.Series)], axis=1)


def transform_log(log: dict) -> pd.DataFrame:
    df = pd.DataFrame({k: [v]
                      for k, v in (log['metaData'] | log['data']).items()})

    # create a separate row for each player of a fight
    players = df.explode('players')['players'].apply(pd.Series)
    # and join to original dataFrame
    df = df.drop(columns=['players'])
    df = df.join(players)

    # create a separate row for each stat
    for column in ['dpsAll', 'support', 'statsAll']:
        df = explode_apply(df, column)

    # cleanup data
    df['skillCastUptime'] = df['skillCastUptime'].clip(-5, 105)
    df['skillCastUptimeNoAA'] = df['skillCastUptimeNoAA'].clip(-5, 105)

    # Fix datetime columns
    df['timeStart'] = pd.to_datetime(df['timeStart'])
    df['timeEnd'] = pd.to_datetime(df['timeEnd'])
    return df


def filter_log_data(log):
    for key in list(log['metaData'].keys()):
        if key not in _RELEVANT_KEYS_METADATA:
            del log['metaData'][key]
    for key in list(log['data'].keys()):
        if key not in _RELEVANT_KEYS_DATA:
            del log['data'][key]
    for player in log['data']['players']:
        for key in list(player.keys()):
            if key not in _RELEVANT_KEYS_DATA_PLAYERS:
                del player[key]
    return log


def fetch_log_thread_func(log_metadata, streamlit_context):
    add_script_run_ctx(
        threading.currentThread(), streamlit_context)
    return fetch_log(log_metadata)


@st.experimental_memo(max_entries=1000)
def fetch_log(log_metadata):
    data_response = requests.get(
        f"https://dps.report/getJson?id={log_metadata['id']}")
    data_response.raise_for_status()
    log = filter_log_data({
        'metaData': log_metadata,
        'data': data_response.json()
    })
    log = transform_log(log)
    return log


@st.experimental_memo(ttl=120)
def fetch_log_list(userToken):
    response = requests.get(
        f"https://dps.report/getUploads?userToken={userToken}")
    response.raise_for_status()
    return response.json()


@st.experimental_memo(max_entries=3)
def fetch_log_data(logList):

    uploads = logList['uploads']

    # Fetch all data in multiple threads
    log_data = pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        streamlit_context = get_script_run_ctx()
        logPromises = [executor.submit(fetch_log_thread_func, log, streamlit_context)
                       for log in uploads]
        # Merge all the promises
        for promise in concurrent.futures.as_completed(logPromises):
            log_data = pd.concat([log_data, promise.result()])

    log_data = log_data.sort_values('timeStart').reset_index(drop=True)
    return log_data


if __name__ == "__main__":
    log_list = fetch_log_list(sys.argv[1])
    print(fetch_log_data(log_list))
