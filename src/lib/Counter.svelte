<script lang="ts">
	async function fetch_data() {
		let response = await fetch(
			'https://dps.report/getJson&permalink=https://wvw.report/cs9W-20220622-215131_wvw'
		);
		let data = await response.json();
		return data;
	}
	const promise = fetch_data();
</script>

<div>
	{#await promise}
		<p>Loading...</p>
	{:then data}
		<p>{data}</p>
	{:catch error}
		<p style="color:red">{error.message}</p>
	{/await}
</div>

<style>
	.counter {
		display: flex;
		border-top: 1px solid rgba(0, 0, 0, 0.1);
		border-bottom: 1px solid rgba(0, 0, 0, 0.1);
		margin: 1rem 0;
	}

	.counter button {
		width: 2em;
		padding: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 0;
		background-color: transparent;
		touch-action: manipulation;
		color: var(--text-color);
		font-size: 2rem;
	}

	.counter button:hover {
		background-color: var(--secondary-color);
	}

	svg {
		width: 25%;
		height: 25%;
	}

	path {
		vector-effect: non-scaling-stroke;
		stroke-width: 2px;
		stroke: var(--text-color);
	}

	.counter-viewport {
		width: 8em;
		height: 4em;
		overflow: hidden;
		text-align: center;
		position: relative;
	}

	.counter-viewport strong {
		position: absolute;
		display: flex;
		width: 100%;
		height: 100%;
		font-weight: 400;
		color: var(--accent-color);
		font-size: 4rem;
		align-items: center;
		justify-content: center;
	}

	.counter-digits {
		position: absolute;
		width: 100%;
		height: 100%;
	}

	.hidden {
		top: -100%;
		user-select: none;
	}
</style>
