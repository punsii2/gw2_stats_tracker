import pandas as pd

from color_lib import spec_color_map

# from streamlit.runtime.scriptrunner import add_script_run_ctx #XXX caching seems to broken in multiple threads... maybe try again another time


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

# These are keys where i dont see a scenario in which they would
# contain information that another key would not also contain.
_DROP_KEYS = [
    "damage",  # -> dps
    "condiDamage",  # -> condiDps
    "powerDamage",  # -> powerDps
    "breakbarDamage",  # -> always 0
    "actorDps",  # -> almost the same as dps
    "actorDamage",  # -> ...
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
    return pd.concat(
        [df.drop(columns=[column]), df.explode(column)[column].apply(pd.Series)], axis=1
    )


def transform_log(log: dict, log_id: str) -> pd.DataFrame:
    df = pd.DataFrame({k: [v] for k, v in ({"id": log_id} | log).items()})

    # create a separate row for each player of a fight
    players = df.explode("players")["players"].apply(pd.Series)
    # and join to original dataFrame
    df = df.drop(columns=["players"])
    df = df.join(players)

    # create a separate column for each stat
    for column in ["dpsAll", "support", "statsAll"]:
        df = explode_apply(df, column)

    # XXX TBD: healing stats has do be done extra
    # st.write(df['extHealingStats'])
    # df['hps'] = df['extHealingStats']['outgoingHealing'][0]['hps']
    # df['healing'] = df['extHealingStats']['outgoingHealing'][0]['healing']
    # df['downedHps'] = df['extHealingStats']['outgoingHealing'][0]['downedHps']
    # df['downedHealing'] = df['extHealingStats']['outgoingHealing'][0]['downedHealing']
    # df = df.drop(columns='extHealingStats')

    # add some helper columns
    df["spec_color"] = df["profession"].apply(lambda spec: spec_color_map[spec])
    df["profession+name"] = df["profession"].apply(lambda s: s + " | ") + df["name"]

    # cleanup data
    # skillCastUptime does not exist in older versions
    # Also some of the values in skillCastUptime are clearly wrong
    df["distToCom"] = df["distToCom"].clip(-5, 2500)
    df["stackDist"] = df["stackDist"].clip(-5, 2500)
    if "skillCastUptime" in df:
        df["skillCastUptime"] = df["skillCastUptime"].clip(-5, 105)
    if "skillCastUptimeNoAA" in df:
        df["skillCastUptimeNoAA"] = df["skillCastUptimeNoAA"].clip(-5, 105)

    # filter useless data
    df = df.drop(columns=_DROP_KEYS)

    # fix datetime columns
    df["timeStart"] = (pd.to_datetime(df["timeStart"]) + pd.DateOffset(hours=6)).apply(
        lambda x: x.replace(tzinfo=None)
    )
    df["timeEnd"] = (pd.to_datetime(df["timeEnd"]) + pd.DateOffset(hours=6)).apply(
        lambda x: x.replace(tzinfo=None)
    )
    return df


def filter_log_data(log):
    for key in list(log.keys()):
        if key not in _RELEVANT_KEYS_DATA:
            del log[key]
    for player in log["players"]:
        for key in list(player.keys()):
            if key not in _RELEVANT_KEYS_DATA_PLAYERS:
                del player[key]
    return log
