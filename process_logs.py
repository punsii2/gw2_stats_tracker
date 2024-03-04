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
    # "buffMap",
    #  IDs:
    # 719 -> Switftness
    # 10269 -> Stealth
    # 725 -> Fury
    # 1122 -> Stability
    # 873 -> Resolution
    # 1187 -> Quickenss
    # 717 -> Protection
    # 743 -> Aegis
    # 718 -> Regeneration
    # 10332 -> ChaosAura
    # 740 -> Might
    # 726 -> Vigor
    # 26980 -> Resistance
]

_RELEVANT_KEYS_DATA_PLAYERS = [
    "account",
    "group",
    "hasCommanderTag",
    "profession",
    "support",
    # "groupBuffsActive", XXX TBD complicated since buff ids have to be mapped to names
    "activeTimes",
    "extHealingStats",
    "extBarrierStats",
    "name",
    # "healing", XXX -> always 0 or 10
    "dpsAll",
    "statsAll",
    # "outgoingHealing" XXX does not show up anymore?
]

# These are keys where i dont see a scenario in which they would
# contain relevant information that another key would not also contain.
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
    "totalDmg",  # --> 'dps' should be enough
    "directDamageCount",  # --> totalDmgCount
    "directDmg",  # --> just use dps
    "connectedConditionCount",  # -> litterally no one cares
    "connectedConditionAbove90HPCount",  # -> ...
    "connectedPowerCount",  # -> totalDmgCount
    "connectedPowerAbove90HPCount",  # -> maybe someday if i feel like it
    "connectedDamageCount",  # -> totalDmgCount
    "connectedDmg",  # --> just use dps
    "connectedDirectDamageCount",  # -> totalDmgCount
    "connectedDirectDmg",  # --> just use dps
    "critableDirectDamageCount",  # -> totalDmgCount
    "againstMovingRate",  # -> always 0
    "stackDist",  # ->  XXX was NaN sometimes, see below
]

# Values that need to be divided by the active time (how long the player actually participated)
_DIVIDE_BY_TIME_KEYS = [
    "resurrects",
    "resurrectTime",
    "condiCleanse",
    "condiCleanseSelf",
    "boonStrips",
    "wasted",
    "timeWasted",
    "saved",
    "timeSaved",
    "swapCount",
    "totalDamageCount",
    "criticalDmg",
    "missed",
    "evaded",
    "blocked",
    "interrupts",
    "invulned",
    "killed",
    "downed",
    "downContribution",
]

_RENAME_KEYS = {
    "dps": "Damage(/s)",
    "condiDps": "ConditionDamage(/s)",
    "powerDps": "PowerDamage(/s)",
    "resurrects": "Resurrects(/s)",
    "resurrectTime": "ResurrectTime(/s)",
    "condiCleanse": "ConditionCleanse(/s)",
    "condiCleanseSelf": "ConditionCleanseSelf(/s)",
    "boonStrips": "BoonStrips(/s)",
    "wasted": "Wasted",
    "timeWasted": "timeWasted(/s)",
    "saved": "Saved",
    "timeSaved": "timeSaved(/s)",
    "distToCom": "DistanceToCommander(avg)",
    "avgBoons": "Boons(avg)",
    "avgActiveBoons": "ActiveBoons(avg)",
    "avgConditions": "Conditions(avg)",
    "avgActiveConditions": "ActiveConditions(avg)",
    "swapCount": "WeaponSwaps(/s)",
    "skillCastUptime": "SkillCastUptime(%)",
    "skillCastUptimeNoAA": "SkillCastUptimeNoAutoAttack(%)",
    "totalDamageCount": "DamageCount(/s)",
    "criticalRate": "CriticalRate(avg)",
    "criticalDmg": "CriticalDamage(/s)",
    "flankingRate": "FlankingRate(avg)",
    "glanceRate": "GlanceRate(avg)",
    "missed": "HitsMissed(/s)",
    "evaded": "HitsEvaded(/s)",
    "blocked": "HitsBlocked(/s)",
    "interrupts": "Interrupts(/s)",
    "invulned": "HitsInvulned(/s)",
    "killed": "Kills(/s)",
    "downed": "Downed(/s)",
    "downContribution": "DownContribution(/s)",
    "downedHealing": "HealingToDowned(/s)",
    "healing": "Healing(/s)",
    "barrier": "Barrier(/s)",
    "percentageAlive": "TimeAlive(%)",
}


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
    if "extHealingStats" in df.columns:
        df["downedHealing"] = df["extHealingStats"].apply(
            lambda x: x["outgoingHealing"][0]["downedHps"]
        )
        df["healing"] = (
            df["extHealingStats"].apply(lambda x: x["outgoingHealing"][0]["hps"])
            - df["downedHealing"]
        )
        df = df.drop(columns="extHealingStats")
    if "extBarrierStats" in df.columns:
        df["barrier"] = df["extBarrierStats"].apply(
            lambda x: x["outgoingBarrier"][0]["bps"]
        )
        df = df.drop(columns="extBarrierStats")

    # filter useless columns
    df = df.drop(columns=_DROP_KEYS, errors="ignore")

    # add some helper columns
    df["spec_color"] = df["profession"].apply(lambda spec: spec_color_map[spec])
    df["profession+name"] = df["profession"].apply(lambda s: s + " | ") + df["name"]

    # cleanup data
    # skillCastUptime does not exist in older versions
    # Also some of the values in skillCastUptime are clearly wrong
    df["distToCom"] = df["distToCom"].clip(-5, 2500)
    # XXX stackDist is sometimes NaN? Check again in the future...
    # if df["stackDist"].dtype != np.float64:
    #    df["stackDist"] = df["stackDist"].clip(-5, 2500)
    if "skillCastUptime" in df:
        df["skillCastUptime"] = df["skillCastUptime"].clip(-5, 105)
    if "skillCastUptimeNoAA" in df:
        df["skillCastUptimeNoAA"] = df["skillCastUptimeNoAA"].clip(-5, 105)

    # absolute values are way less accurate than values per second, so transform some of them
    df["activeTimes"] = df["activeTimes"].apply(lambda x: x[0] / 1000)
    for key in _DIVIDE_BY_TIME_KEYS:
        if key not in df:
            continue
        df[key] = df[key] / df["activeTimes"]

    # add "percentage alive" as it is more understandable than "activeTimes" and fix the "duration" for that
    df["duration"] = pd.to_timedelta(df["duration"]).dt.total_seconds()
    df["percentageAlive"] = df["activeTimes"] / df["duration"]

    # fix datetime columns
    df["timeStart"] = (pd.to_datetime(df["timeStart"]) + pd.DateOffset(hours=6)).apply(
        lambda x: x.replace(tzinfo=None)
    )
    df["timeEnd"] = (pd.to_datetime(df["timeEnd"]) + pd.DateOffset(hours=6)).apply(
        lambda x: x.replace(tzinfo=None)
    )
    df.rename(columns=_RENAME_KEYS, inplace=True)
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
