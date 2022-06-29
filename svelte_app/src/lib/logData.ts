import { writable } from 'svelte/store';

function createLogStore() {
	const { subscribe, set, update } = writable({
		list: undefined,
		data: {},
		loading: false
	});

	return {
		subscribe,
		addLog: (id: string, data: Object) => update(store = > store.data[id]=data),
		decrement: () => update(n => n - 1),
		reset: () => set(0)
	};
}

export const count = createCount();