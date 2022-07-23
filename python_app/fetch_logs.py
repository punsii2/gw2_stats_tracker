import concurrent.futures
import sys

import requests
import streamlit as st

_RELEVANT_KEYS_LIST = [
    "id",
    "permalink",
    "uploadTime",
    "encounterTime",
    # "players", The player list is also part or the dataset
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
    "squadBuffsActive",
    # "extHealingStats", XXX TBD
    # "extBarrierStats", XXX TBD
    "name",
    "healing",
    "dpsAll",
    "statsAll",
    "outgoingHealing"
]


def _filter_log_data(data: dict):
    for key in list(data.keys()):
        if key not in _RELEVANT_KEYS_DATA:
            del data[key]

    for player in data['players']:
        for key in list(player.keys()):
            if key not in _RELEVANT_KEYS_DATA_PLAYERS:
                del player[key]

    return data


# @st.cache() XXX: st.cache does not seem to work inside separate thread
def fetch_log(id: str):
    return requests.get(f"https://dps.report/getJson?id={id}")


@st.cache(ttl=120)
def fetch_log_list(userToken):
    response = requests.get(
        f"https://dps.report/getUploads?userToken={userToken}")
    response.raise_for_status()
    logList = response.json()
    return logList


@st.cache(suppress_st_warning=True)
def fetch_log_data(logList):

    # logList.keys()=dict_keys([
    #   'pages'
    #   'totalUploads'
    #   'userToken'
    #   'uploads'
    # ])
    # logList['uploads'][0].keys()=dict_keys([
    #  'id'
    #  'permalink'
    #  'uploadTime'
    #  'encounterTime'
    #  'generator'
    #  'generatorId'
    #  'generatorVersion'
    #  'language'
    #  'languageId'
    #  'evtc'
    #  'players'
    #  'encounter'
    #  'report'
    #  'tempApiId'
    # ])
    uploads = logList['uploads']

    # Fetch all data
    with concurrent.futures.ThreadPoolExecutor() as executor:  # optimally defined number of threads
        logPromises = [
            {
                "id": log['id'],
                "logPromise": executor.submit(fetch_log, log['id'])
            } for log in uploads
        ]
        concurrent.futures.wait([entry['logPromise'] for entry in logPromises])

    logsData = {}
    for log in uploads:
        logsData[log['id']] = {
            'metaData': {},
            'data': {}
        }
        for key in _RELEVANT_KEYS_LIST:
            logsData[log['id']]['metaData'][key] = log[key]

    # Merge all the promises
    for promise in logPromises:
        response = promise['logPromise'].result()
        response.raise_for_status()
        data = response.json()
        logsData[promise['id']]['data'] = _filter_log_data(data)

    return logsData


if __name__ == "__main__":
    print(fetch_log_data(sys.argv[1]))
