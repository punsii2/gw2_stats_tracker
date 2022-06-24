<script context="module" lang="ts">
	export const prerender = true;
</script>

<script lang="ts">
	import LogTable from '$lib/LogTable.svelte';
	/*
	 * JSON DATA:
	 * JSON -> Players[i]
	 *  - statsAll
	 *  - dpsAll
	 *  - support
	 *  - extHealingStats
	 *    - outgoingHealing
	 *
	 */
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="dps.report stats aggregation" />
</svelte:head>

<section>
	<LogTable />
</section>

<style>
	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		flex: 1;
	}
</style>
