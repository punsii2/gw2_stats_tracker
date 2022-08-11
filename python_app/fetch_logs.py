import concurrent.futures
import sys
import time

import pandas as pd
import requests
import streamlit as st
from streamlit.scriptrunner import add_script_run_ctx

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
    # "squadBuffsActive", XXX TBD complicated since buff ids have to be mapped to names
    # "extHealingStats", XXX TBD
    # "extBarrierStats", XXX TBD (also seems to be inaccurate)
    "name",
    # "healing", XXX -> always 0 or 10
    "dpsAll",
    "statsAll",
    # "outgoingHealing" XXX does not show up anymore?
]

# These are keyes where i dont see a scenario in which they would
# contain information that another key would not also contain.
_DROP_KEYS = [
    "damage",  # -> dps
    "condiDamage",  # -> condiDps
    "powerDamage",  # -> powerDps
    "breakbarDamage",  # -> always 0
    "actorDamage",  # -> almost same as damge
    "actorCondiDps",  # -> ...
    "actorCondiDamage",  # -> ...
    "actorPowerDps",  # -> ...
    "actorPowerDamage",  # -> ...
    "actorBreakbarDamage",  # -> ...
    "condiCleanseTime",  # -> condiCleanse
    "condiCleanseTimeSelf",  # -> ...
    "boonStripsTime",  # -> ...
    "connectedDamageCount",  # -> unclear
    "connectedDirectDamageCount",  # -> unclear
    "critableDirectDamageCount",  # -> unclear
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

    # XXX TBD: healing stats has do be done extra
    # st.write(df['extHealingStats'])
    # df['hps'] = df['extHealingStats']['outgoingHealing'][0]['hps']
    # df['healing'] = df['extHealingStats']['outgoingHealing'][0]['healing']
    # df['downedHps'] = df['extHealingStats']['outgoingHealing'][0]['downedHps']
    # df['downedHealing'] = df['extHealingStats']['outgoingHealing'][0]['downedHealing']
    # df = df.drop(columns='extHealingStats')

    # cleanup data
    # skillCastUptime does not exist in older versions
    # Alswo some of the values in skillCastUptime are clearly wrong
    if 'skillCastUptime' in df:
        df['skillCastUptime'] = df['skillCastUptime'].clip(-5, 105)
    if 'skillCastUptimeNoAA' in df:
        df['skillCastUptimeNoAA'] = df['skillCastUptimeNoAA'].clip(-5, 105)

    # filter useless data
    df = df.drop(columns=_DROP_KEYS)

    # fix datetime columns
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


def fetch_log_thread_func(log_metadata):
    # This gives the main thread time to call add_script_run_ctx, which does not work from the child thread
    time.sleep(1)

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
        logPromises = [executor.submit(fetch_log_thread_func, log)
                       for log in uploads]

        for thread in executor._threads:
            add_script_run_ctx(thread)
        # Merge all the promises
        for promise in concurrent.futures.as_completed(logPromises):
            log_data = pd.concat([log_data, promise.result()])

    log_data = log_data.sort_values('timeStart').reset_index(drop=True)
    return log_data


if __name__ == "__main__":
    log_list = fetch_log_list(sys.argv[1])
    print(fetch_log_data(log_list)[
          'extHealingStats'][20]['outgoingHealing'][0]['hps'])
