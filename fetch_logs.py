import sys

import pandas as pd
import requests
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

# logList.keys()=dict_keys([
#   'pages'
#   'totalUploads'
#   'userToken'
#   'uploads'
# ])

# _RELEVANT_KEYS_METADATA = [
#     # logList['uploads'][0].keys()=dict_keys([
#     "id",
#     "permalink",
#     "uploadTime",
#     "encounterTime",
#     #  'generator'
#     #  'generatorId'
#     #  'generatorVersion'
#     #  'language'
#     #  'languageId'
#     #  'evtc'
#     #  'players' The player list is also part or the dataset
#     #  'encounter'
#     #  'report'
#     #  'tempApiId'
#     # ])
# ]

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


def transform_log(log: dict, log_id: str) -> pd.DataFrame:
    df = pd.DataFrame({k: [v] for k, v in ({'id': log_id} | log).items()})

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

    df['distToCom'] = df['distToCom'].clip(-5, 2500)
    df['stackDist'] = df['stackDist'].clip(-5, 2500)
    if 'skillCastUptime' in df:
        df['skillCastUptime'] = df['skillCastUptime'].clip(-5, 105)
    if 'skillCastUptimeNoAA' in df:
        df['skillCastUptimeNoAA'] = df['skillCastUptimeNoAA'].clip(-5, 105)

    # filter useless data
    df = df.drop(columns=_DROP_KEYS)

    # fix datetime columns
    df['timeStart'] = (pd.to_datetime(df['timeStart']) + pd.DateOffset(hours=6)).apply(
        lambda x: x.replace(tzinfo=None))
    df['timeEnd'] = (pd.to_datetime(df['timeEnd']) + pd.DateOffset(hours=6)).apply(
        lambda x: x.replace(tzinfo=None))
    return df


def filter_log_data(log):
    for key in list(log.keys()):
        if key not in _RELEVANT_KEYS_DATA:
            del log[key]
    for player in log['players']:
        for key in list(player.keys()):
            if key not in _RELEVANT_KEYS_DATA_PLAYERS:
                del player[key]
    return log


@st.experimental_memo(max_entries=1000)
def fetch_log(log_id: str):
    data_response = requests.get(
        f"https://dps.report/getJson?id={log_id}")
    data_response.raise_for_status()
    return transform_log(filter_log_data(data_response.json()), log_id)


@st.experimental_memo(ttl=120)
def fetch_log_list(userToken: str):
    response = requests.get(
        f"https://dps.report/getUploads?userToken={userToken}")
    response.raise_for_status()
    json = response.json()
    pages = json['pages']
    uploads = json['uploads']
    for page in range(pages-1, pages-4, -1):
        if page < 1:
            break
        response = requests.get(
            f"https://dps.report/getUploads?userToken={userToken}&page={page+1}")
        response.raise_for_status()
        uploads.extend(response.json()['uploads'])
    return uploads


# @st.experimental_memo(max_entries=3)
def fetch_log_data(uploads):
    progress_bar = st.progress(0)
    log_data_list = pd.DataFrame()
    num_logs = len(uploads)
    for idx, log_metadata in enumerate(uploads):
        progress_bar.progress(idx/num_logs)
        log_data_list = pd.concat(
            [log_data_list, fetch_log(log_metadata["id"])])

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

    log_data_list = log_data_list.sort_values(
        'timeStart').reset_index(drop=True)
    progress_bar.progress(100)
    progress_bar.empty()
    return log_data_list


if __name__ == "__main__":
    log_list = fetch_log_list(sys.argv[1])
    print(fetch_log_data(log_list)[
          'extHealingStats'][20]['outgoingHealing'][0]['hps'])
