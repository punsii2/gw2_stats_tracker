import json
import requests

relevantKeysList = [
    "id",
    "permalink",
    "uploadTime",
    "encounterTime",
    #"players", XXX Name conflict
]

relevantKeysData = [
    "timeStart",
    "timeEnd",
    "duration",
    "players",
]

relevantKeysDataPlayers = [
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

response = requests.get(
    "https://dps.report/getUploads?userToken=")
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

logsData = {}
i = 0
for log in uploads:
    i += 1
    if i > 3:
        break
    response = requests.get(
        f"https://dps.report/getJson?id={log['id']}")
    response.raise_for_status()
    data = response.json()
    for key in list(data.keys()):
        if key not in relevantKeysData:
            del data[key]

    for player in data['players']:
        for key in list(player.keys()):
            if key not in relevantKeysDataPlayers:
                del player[key]

    for key in relevantKeysList:
        data[key] = log[key]

    logsData[log['id']] = data

#log1 = logsData[uploads[0]['id']]
#keys1 = log1.keys()
# for key1 in keys1:
#    keyType1 = type(log1[key1])
#    print(f"{key1=}: {keyType1=}")
#    if isinstance(log1[key1], dict):
#        keys2 = log1[key1].keys()
#        for key2 in keys2:
#            keyType2 = type(log1[key1][key2])
#            print(f"    {key2=}: {keyType2=}")
#
#
#player1 = log1['players'][0]
#keys1 = player1.keys()
# for key1 in keys1:
#    keyType1 = type(player1[key1])
#    print(f"{key1=}: {keyType1=}")
#    if isinstance(player1[key1], dict):
#        keys2 = player1[key1].keys()
#        for key2 in keys2:
#            keyType2 = type(player1[key1][key2])
#            print(f"    {key2=}: {keyType2=}")

print(json.dumps(logsData[uploads[1]['id']], indent=2))
