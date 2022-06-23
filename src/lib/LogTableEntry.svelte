<script lang="ts">
	export let path: string;
	let dataPromise = {};
	let isLoaded = false;

	async function getData() {
		const response = await fetch(path);
		return await response.json();
	}

	function matchDate(url: string) {
		const dateRegex = /[0-9]{8}$/;
		return url.match(dateRegex);
	}
</script>

<!--
    Date
    URL
    Loaded
-->
{#await dataPromise}
	<tr>
		<td />
		<td />
		<td />
	</tr>
{:then data}
	<p>{JSON.stringify(data, null, 2)}</p>
	<tr>
		<td>{matchDate(path)}</td>
		<td />
		<td />
	</tr>
{:catch someError}
	<tr>
		<td>ERROR</td>
		<td><p>{someError.message}</p></td>
		<td />
	</tr>
{/await}
