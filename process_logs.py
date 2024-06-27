from typing import List

import pandas as pd

from color_lib import spec_color_map

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
    "buffUptimesActive",
    "groupBuffsActive",
    "consumables",
    "activeTimes",
    "extHealingStats",
    "extBarrierStats",
    "name",
    # "healing", XXX -> always 0 or 10
    "dpsAll",
    "statsAll",
    # "outgoingHealing" XXX does not show up anymore?
]

_BOON_GENERATION_GROUP_KEY_TABLE = {
    717: "Protection(groupGeneration/s)",
    718: "Regeneration(groupGeneration/s)",
    719: "Switftness(groupGeneration/s)",
    725: "Fury(groupGeneration/s)",
    726: "Vigor(groupGeneration/s)",
    740: "Might(groupGeneration/s)",
    743: "Aegis(groupGeneration/s)",
    873: "Resolution(groupGeneration/s)",
    1122: "Stability(groupGeneration/s)",
    1187: "Quickness(groupGeneration/s)",
    5974: "Superspeed(groupGeneration/s)",
    10332: "ChaosAura(groupGeneration/s)",
    26980: "Resistance(groupGeneration/s)",
    30328: "Alacrity(groupGeneration/s)",
    # 10269 / 13017 -> Stealth
}

_BOON_UPTIME_KEY_TABLE = {
    717: "Protection(uptime%)",
    718: "Regeneration(uptime%)",
    719: "Switftness(uptime%)",
    725: "Fury(uptime%)",
    726: "Vigor(uptime%)",
    740: "Might(uptime%)",
    743: "Aegis(uptime%)",
    873: "Resolution(uptime%)",
    1122: "Stability(uptime%)",
    1187: "Quickness(uptime%)",
    5974: "Superspeed(uptime%)",
    10332: "ChaosAura(uptime%)",
    26980: "Resistance(uptime%)",
    30328: "Alacrity(uptime%)",
}
BOON_KEYS = sorted(
    list(_BOON_GENERATION_GROUP_KEY_TABLE.values())
    + list(_BOON_UPTIME_KEY_TABLE.values())
) + ["Bufffood(uptime%)"]

# These are keys where i dont see a scenario in which they would
# contain relevant information that another key would not also contain.
_DROP_KEYS = [
    "damage",  # -> dps
    "condiDamage",  # -> condiDps
    "powerDamage",  # -> powerDps
    "breakbarDamage",  # -> always 0
    "avgBoons",  # -> avgActiveBoons
    "avgConditions",  # -> avgActiveConditions
    "actorDps",  # -> almost the same as dps
    "againstMovingRate",  # --> always 0
    "againstDownedCount",  # -> not relevant
    "againstDownedDamage",  # -> not relevant
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
    "stackDist",  # ->  XXX was NaN sometimes, see below
    "wasted",  # -> don't know what it means
    "saved",  # -> don't know what it means
    "timeWasted",  # -> don't know what it means
    "timeSaved",  # -> don't know what it means
]

# Values that need to be divided by the active time (how long the player actually participated)
_DIVIDE_BY_TIME_KEYS = [
    "resurrects",
    "resurrectTime",
    "condiCleanse",
    "condiCleanseSelf",
    "boonStrips",
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
_INTERMEDIATE_KEYS = [
    "duration",
    "hasCommanderTag",
    "group",
    "activeTimes",
    "timeEnd",
]

RENAME_KEYS = {
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
    "avgActiveBoons": "ActiveBoons(avg)",
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
    "downContribution": "DownContributionDamage(/s)",
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

    df["activeTimes"] = df["activeTimes"].apply(lambda x: x[0] / 1000)

    # create a separate column for each stat
    for column in ["dpsAll", "support", "statsAll"]:
        df = explode_apply(df, column)

    # Same idea for the boons, but we have a more complicated data structure to begin with:
    # "groupBuffsActive": [
    #   {
    #     "id": 1187,
    #     "buffData": [{
    #       "generation": 12.87,
    #       "overstack": 12.87,
    #       "wasterd": 0.0,
    #       ...
    #      }]
    #   },
    #   {....}
    # ]
    EMPTY_BOON_MAP = {k: 0 for k in _BOON_GENERATION_GROUP_KEY_TABLE.keys()}
    df = pd.concat(
        [
            df.drop(columns=["groupBuffsActive"]),
            df["groupBuffsActive"]
            .map(
                lambda cell_value: (
                    EMPTY_BOON_MAP
                    if not isinstance(cell_value, List)
                    else EMPTY_BOON_MAP
                    | {
                        e["id"]: e["buffData"][0]["generation"]
                        for e in cell_value
                        if e["id"] in _BOON_GENERATION_GROUP_KEY_TABLE.keys()
                    }
                )
            )
            .apply(pd.Series),
        ],
        axis=1,
    )
    df.rename(columns=_BOON_GENERATION_GROUP_KEY_TABLE, inplace=True)

    EMPTY_BOON_MAP = {k: 0 for k in _BOON_UPTIME_KEY_TABLE.keys()}
    df = pd.concat(
        [
            df.drop(columns=["buffUptimesActive"]),
            df["buffUptimesActive"]
            .map(
                lambda cell_value: (
                    EMPTY_BOON_MAP
                    if not isinstance(cell_value, List)
                    else EMPTY_BOON_MAP
                    | {
                        e["id"]: e["buffData"][0]["uptime"]
                        for e in cell_value
                        if e["id"] in _BOON_UPTIME_KEY_TABLE.keys()
                    }
                )
            )
            .apply(pd.Series),
        ],
        axis=1,
    )
    df.rename(columns=_BOON_UPTIME_KEY_TABLE, inplace=True)

    # Reinforced armor: 9283
    # Malnourished: 46587
    # Diminished: 46668
    filtered_buffs = [9283, 46587, 46668]
    df["consumables"] = df["consumables"].map(
        lambda cell_value: (
            [e["duration"] for e in cell_value if e["id"] not in filtered_buffs]
            if hasattr(cell_value, "__len__")
            else []
        )
    )
    df["Bufffood(uptime%)"] = (
        df["consumables"]
        .map(lambda e: e[0] if len(e) > 0 else 0)
        .div(1000)
        .div(df["activeTimes"])
        .clip(0, 1)
        + df["consumables"]
        .map(lambda e: e[1] if len(e) > 1 else 0)
        .div(1000)
        .div(df["activeTimes"])
        .clip(0, 1)
    ).div(2)
    df = df.drop(columns=["consumables"])

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
    df["distToCom"] = df["distToCom"].clip(0, 1500)
    # XXX stackDist is sometimes NaN? Check again in the future...
    # if df["stackDist"].dtype != np.float64:
    #    df["stackDist"] = df["stackDist"].clip(-5, 2500)
    if "skillCastUptime" in df:
        df["skillCastUptime"] = df["skillCastUptime"].clip(5, 95)
    if "skillCastUptimeNoAA" in df:
        df["skillCastUptimeNoAA"] = df["skillCastUptimeNoAA"].clip(5, 95)

    # absolute values are way less accurate than values per second, so transform some of them
    for key in _DIVIDE_BY_TIME_KEYS:
        if key not in df:
            continue
        df[key] = df[key] / df["activeTimes"]
    for key in list(_BOON_UPTIME_KEY_TABLE.values()) + list(
        _BOON_GENERATION_GROUP_KEY_TABLE.values()
    ):
        df[key] = df[key] / df["activeTimes"]
    for key in list(_BOON_UPTIME_KEY_TABLE.values()):
        df[key] = df[key].clip(0, 1)

    # add "percentage alive" as it is more understandable than "activeTimes" and fix the "duration" for that
    df["duration"] = pd.to_timedelta(df["duration"]).dt.total_seconds()
    df["percentageAlive"] = df["activeTimes"] / df["duration"]

    # fix datetime columns
    for key in ["timeStart", "timeEnd"]:
        df[key] = pd.to_datetime(
            df[key].apply(lambda t: t[:-4]), format="%Y-%m-%d %H:%M:%S"
        ) + pd.Timedelta(hours=5)

    # remove keys that were only needed for calculations
    df = df.drop(columns=_INTERMEDIATE_KEYS, errors="ignore")

    # rename for better UX
    df.rename(columns=RENAME_KEYS, inplace=True)
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
