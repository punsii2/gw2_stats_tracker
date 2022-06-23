<script lang="ts">
	import LogTableEntry from './LogTableEntry.svelte';

	export let userToken: string = '';

	const baseUrl = 'https://dps.report/getUploads';
	let url = baseUrl + '?userToken=' + userToken;
	let logsPromise = fetchLogs();

	async function fetchLogs() {
		const response = await fetch(url);
		return await response.json();
	}
</script>

<input bind:value={userToken} placeholder="userToken" size="38" />
<button on:click={fetchLogs}> Fetch </button>
<table style="width:100%">
	<tr>
		<th> URL </th>
		<th> Timestamp </th>
		<th> Duration </th>
		<th> Loaded </th>
	</tr>
	<!-- Use with fetchLogs()
	{#await dataPromise}
		<p>Loading...</p>
	{:then data}
		<p>{JSON.stringify(data, null, 2)}</p>
	{:catch someError}
		<p>{someError.message}</p>
	{/await}-->
	{#await logsPromise}
		<tr>
			<td> 0 </td>
			<td> - </td>
			<td> - </td>
		</tr>
	{:then logs}
		<!--<p>{JSON.stringify(logs.uploads, null, 2)}</p>-->
		<!--{#each { length: 10 } as _, i}
			<LogTableEntry logID={logs.uploads[i].id} />
		{/each}-->
		{#each logs.uploads as log}
			<LogTableEntry id={log.id} permalink={log.permalink} />
		{/each}
	{:catch someError}
		<tr>
			<td>ERROR</td>
			<td><p>{someError.message}</p></td>
			<td />
		</tr>
	{/await}
</table>
