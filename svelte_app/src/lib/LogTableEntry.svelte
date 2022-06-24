<script lang="ts">
	import moment from 'moment';
	//import { logData } from './logData.js';

	export let id: string;
	export let permalink: string;
	const baseUrl = 'https://dps.report/getJson';
	let fetchUrl = baseUrl + '?id=' + id;
	let dataPromise = {};
	let isLoaded = false;

	dataPromise = getData();
	async function getData() {
		const response = await fetch(fetchUrl);
		return await response.json();
	}

	//const appenToLogData = (log: object) => {
	//	if (id in $logData) {
	//		$logData[id] = log;
	//	}
	//	console.log(log);
	//	console.log($logData);
	//};

	const dateRegex = /[0-9]{8}-[0-9]{6}$/;
</script>

<!--
    ID
    Duration
    Loaded
-->

{#await dataPromise}
	<tr>
		<td><a href={permalink}>{permalink}</a></td>
		<td> {moment(id.match(dateRegex), 'YYYYMMDD-hhmmss').format('DD.MM.YY hh:mm:ss')} </td>
		<td> - </td>
		<td> ❌ </td>
	</tr>
{:then log}
	<tr>
		<td><a href={permalink}>{permalink}</a></td>
		<td> {moment(id.match(dateRegex), 'YYYYMMDD-hhmmss').format('DD.MM.YY hh:mm:ss')} </td>
		<td> {log} </td>
		<td> ✅ </td>
	</tr>
	<!--<p>{JSON.stringify(logData, null, 2)}</p>-->
{:catch someError}
	<tr>
		<td>ERROR</td>
		<td><p>{someError.message}</p></td>
		<td />
	</tr>
{/await}
