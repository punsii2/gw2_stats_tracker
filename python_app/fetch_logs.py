import concurrent.futures
import requests
import sys

RELEVANT_KEYS_LIST = [
    "id",
    "permalink",
    "uploadTime",
    "encounterTime",
    # "players", XXX Name conflict
]

RELEVANT_KEYS_DATA = [
    "timeStart",
    "timeEnd",
    "duration",
    "players",
]

RELEVANT_KEYS_DATA_PLAYERS = [
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


def fetch_log(id: str):
    return requests.get(f"https://dps.report/getJson?id={id}")


def filter_log_data(data: dict):
    for key in list(data.keys()):
        if key not in RELEVANT_KEYS_DATA:
            del data[key]

    for player in data['players']:
        for key in list(player.keys()):
            if key not in RELEVANT_KEYS_DATA_PLAYERS:
                del player[key]

    return data


def fetch_data(userToken: str):
    response = requests.get(
        f"https://dps.report/getUploads?userToken={userToken}")
    response.raise_for_status()
    logList = response.json()

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
        for key in RELEVANT_KEYS_LIST:
            logsData[log['id']]['metaData'][key] = log[key]

    # Merge all the promises
    for promise in logPromises:
        response = promise['logPromise'].result()
        response.raise_for_status()
        data = response.json()
        logsData[promise['id']]['data'] = filter_log_data(data)

    return logsData


if __name__ == "__main__":
    print(fetch_data(sys.argv[1]))
