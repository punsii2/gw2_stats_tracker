<script lang="ts">
	import LogTableEntry from './LogTableEntry.svelte';

	export let userToken = '';
	const baseUrl = 'https://dps.report/getUpload';
	let url = baseUrl + '?userToken=' + userToken;

	async function fetchLogs() {
		const response = await fetch(url);
		return await response.json();
	}

	// XXX use fetchLogs() instead
	let logs = [
		{
			url: 'https://dps.report/getJson?permalink=https://wvw.report/duCJ-20220622-214727_wvw'
		}
	];
</script>

<input bind:value={userToken} placeholder="userToken" />
<button on:click={fetchLogs}> Fetch </button>
<table>
	<tr>
		<th> Date </th>
		<th> Url </th>
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
	{#each logs as log}
		<LogTableEntry path={log.url} />
	{/each}
</table>
