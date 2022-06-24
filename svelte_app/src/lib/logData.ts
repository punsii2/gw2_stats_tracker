import { readable } from 'svelte/store';

export function initialValue() {
	return {
		logs: new Map()
	};
}

export function makeLogDataStore(args: any) {
	let initial = initialValue();
	let store = readable(initial, makeSubscribe(initial, args));
	return store;
}

function unsubscribe() {
	// Nothing to do here
}

function makeSubscribe(data: any, _args: any) {
	return (set: any) => {
		fetchLogs(data, set);
		return unsubscribe;
	};
}

async function fetchLogs(data: any, set: any) {
	try {
		const response = await fetch(
			'https://dps.report/getUploads?userToken='
		);

		if (response.ok) {
			const logs = await response.json();
			const logData = genericLogData();
			for (const { id, url } of logs) {
				data.logs.set(id, { id, logData });
				fetchLogData(data, set, url);
			}
			set(data);
		} else {
			const text = response.text();
			throw new Error(text);
		}
	} catch (error) {
		data.set.error = error;
		set(data);
	}
}

async function fetchLogData(data: any, set: any, url: any) {
	try {
		const response = await fetch(url);
		if (response.ok) {
			const log = await response.json();

			let logMetaData = data.users.get(log.id);
			if (logMetaData) {
				const logData = log.permalink;
				data.logs.set(logMetaData.id, { ...logMetaData, logData });
				set(data);
			}
		}
	} catch (error) {}
}

function genericLogData() {
	return `{
"eliteInsightsVersion": "2.44.2.0",
"triggerID": 1,
"fightName": "World vs World - Edge of the Mists",
"fightIcon": "https://wiki.guildwars2.com/images/3/35/WvW_Rank_up.png",
"arcVersion": "EVTC20220525",
"gW2Build": 130382,
"language": "English",
"languageID": 0,
"recordedBy": "Dirty Punsi",
"timeStart": "2022-06-22 15:24:20 -04",
"timeEnd": "2022-06-22 15:25:33 -04",
"timeStartStd": "2022-06-22 15:24:20 -04:00",
"timeEndStd": "2022-06-22 15:25:33 -04:00",
"duration": "01m 13s 250ms",
"success": true,
"isCM": false,
"targets": [
{
	"id": 1,
	"finalHealth": 0,
	"healthPercentBurned": 100,
	"firstAware": 0,
	"lastAware": 73250,
	"buffs": [],
	"enemyPlayer": false,
	"breakbarPercents": [],
	"name": "Enemy Players",
	"totalHealth": -1,
	"condition": 0,
	"concentration": 0,
	"healing": 0,
	"toughness": 0,
	"hitboxHeight": 0,
	"hitboxWidth": 0,
	"instanceID": 32962,
	"isFake": true,
	"dpsAll": [
	{
		"dps": 10777,
		"damage": 789397,
		"condiDps": 902,
		"condiDamage": 66106,
		"powerDps": 9874,
		"powerDamage": 723291,
		"breakbarDamage": 0,
		"actorDps": 10777,
		"actorDamage": 789397,
		"actorCondiDps": 902,
		"actorCondiDamage": 66106,
		"actorPowerDps": 9874,
		"actorPowerDamage": 723291,
		"actorBreakbarDamage": 0
	}
	],
	"statsAll": [
	{
		"wasted": 0,
		"timeWasted": 0,
		"saved": 0,
		"timeSaved": 0,
		"stackDist": 0,
		"distToCom": 0,
		"avgBoons": 0,
		"avgActiveBoons": 0,
		"avgConditions": 0,
		"avgActiveConditions": 0,
		"swapCount": 0,
		"totalDamageCount": 2552,
		"directDamageCount": 1635,
		"connectedDirectDamageCount": 1155,
		"connectedDamageCount": 2020,
		"critableDirectDamageCount": 1142,
		"criticalRate": 664,
		"criticalDmg": 592530,
		"flankingRate": 607,
		"againstMovingRate": 1560,
		"glanceRate": 16,
		"missed": 21,
		"evaded": 267,
		"blocked": 147,
		"interrupts": 11,
		"invulned": 97,
		"killed": 8,
		"downed": 2
	}
	],
	"defenses": [
	{
		"damageTaken": 1440233,
		"breakbarDamageTaken": 0,
		"blockedCount": 160,
		"evadedCount": 369,
		"missedCount": 80,
		"dodgeCount": 0,
		"invulnedCount": 187,
		"damageBarrier": 99638,
		"interruptedCount": 20,
		"downCount": 0,
		"downDuration": 0,
		"deadCount": 0,
		"deadDuration": 0,
		"dcCount": 0,
		"dcDuration": 0
	}
	]}]}`;
}
