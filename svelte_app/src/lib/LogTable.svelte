<script>
	import { onDestroy } from 'svelte';
	import { initialValue, makeLogDataStore } from './logData';
	import LogTableEntry from './LogTableEntry.svelte';

	let someProp = 'something';
	let store = makeLogDataStore(someProp);
	let unsubscribe;
	let logs = initialValue();

	onDestroy(() => {
		if (unsubscribe) {
			unsubscribe();
			unsubscribe = null;
		}
	});

	function updateLogs(data) {
		logs = data;
	}

	function handleClick() {
		if (!unsubscribe) {
			unsubscribe = store.subscribe(updateLogs);
		}
	}

	export let userToken = '';
	let logsPromise = fetchLogs(userToken);
	//console.log(typeof logsPromise);

	async function fetchLogs(userToken) {
		const baseUrl = 'https://dps.report/getUploads';
		let url = baseUrl + '?userToken=' + userToken;
		const response = await fetch(url);
		return await response.json();
	}

	//<!--<table style="width:100%">
	//	<tr>
	//		<th> URL </th>
	//		<th> Timestamp </th>
	//		<th> Duration </th>
	//		<th> Loaded </th>
	//	</tr>
	//	<!-- Use with fetchLogs()
	//	{#await dataPromise}
	//		<p>Loading...</p>
	//	{:then data}
	//		<p>{JSON.stringify(data, null, 2)}</p>
	//	{:catch someError}
	//		<p>{someError.message}</p>
	//	{/await}
	//	{#await logsPromise}
	//		<tr>
	//			<td> - </td>
	//			<td> - </td>
	//			<td> - </td>
	//			<td> - </td>
	//		</tr>
	//	{:then logs}
	//		<!--<p>{JSON.stringify(logs.uploads, null, 2)}</p>-->
	//		<!--{#each { length: 10 } as _, i}
	//			<LogTableEntry logID={logs.uploads[i].id} />
	//		{/each}
	//		{#if !Object.hasOwn(logs, 'uploads')}
	//			<tr>
	//				<td> - </td>
	//				<td> - </td>
	//				<td> - </td>
	//				<td> - </td>
	//			</tr>
	//		{:else}
	//			{#each logs.uploads as log}
	//				<LogTableEntry id={log.id} permalink={log.permalink} />
	//			{/each}
	//		{/if}
	//	{:catch someError}
	//		<tr>
	//			<td />
	//			<td>ERROR</td>
	//			<td><p>{someError.message}</p></td>
	//			<td />
	//		</tr>
	//	{/await}
	//</table>-->
</script>

<div class="fetch-input">
	<input bind:value={userToken} placeholder="userToken" size="38" />
	<button on:click={handleClick} disabled={!!unsubscribe}> Fetch </button>
</div>

{#each [...logs.logs.entries()] as [id, logMetaData]}
	<h3>{id}</h3>
	<p>{logMetaData.logData}</p>
{/each}

<style>
	th {
		text-align: left;
	}
	.fetch-input {
		display: inline;
	}
</style>
