<script lang="ts">
	import LogTableEntry from './LogTableEntry.svelte';
	import { writable } from 'svelte/store';
	export const logStore = writable({
		list: undefined,
		data: {},
		loading: false
	});

	export let userToken = '';

	async function loadLogList(userToken: string) {
		const baseUrl = 'https://dps.report/getUploads';
		let url = baseUrl + '?userToken=' + userToken;

		$logStore.loading = true;
		const response = await fetch(url);
		const list = await response.json();
		$logStore.list = list;
		$logStore.loading = false;
	}
</script>

<div class="fetch-input">
	<input bind:value={userToken} placeholder="userToken" size="38" />
	<button on:click={loadLogList(userToken)}> Fetch </button>
</div>
<table style="width:100%">
	<tr>
		<th> URL </th>
		<th> Timestamp </th>
		<th> Duration </th>
		<th> Loaded </th>
	</tr>
	{#if $logStore.loading}
		<tr> Loading Data... </tr>
	{:else if $logStore.list !== undefined}
		{console.log($logStore)}
		{#each $logStore.list.uploads as log}
			<LogTableEntry id={log.id} permalink={log.permalink} />
		{/each}
	{/if}
</table>

<style>
	th {
		text-align: left;
	}
	.fetch-input {
		display: inline;
	}
</style>
