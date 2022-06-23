<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let userToken;

	const dispatch = createEventDispatcher();

	function fetchTokenEvent() {
		dispatch('token');
	}
</script>

<form on:submit={fetchTokenEvent}>
	<label for="userToken">userToken:</label>
	<input type="text" id="userToken" name="userToken"/>
	<input type="submit" value="Fetch" />
</form>
