<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { flyAndScale } from '$lib/utils/transitions';
	import { getContext } from 'svelte';

	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import Pencil from '$lib/components/icons/Pencil.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Tags from '$lib/components/chat/Tags.svelte';
	import Share from '$lib/components/icons/Share.svelte';
	import ArchiveBox from '$lib/components/icons/ArchiveBox.svelte';
	import DocumentArrowUpSolid from '$lib/components/icons/DocumentArrowUpSolid.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import GlobeAltSolid from '$lib/components/icons/GlobeAltSolid.svelte';
	import { config } from '$lib/stores';
	import { switchState } from '$lib/stores';

	const i18n = getContext('i18n');
	let show = false;

	export let onClose: Function;

	function toggleState(event: CustomEvent<{ currentTarget: EventTarget & HTMLDivElement; originalEvent: MouseEvent; }>) {
		switchState.update(current => (current + 1) % 3); // Cycles through 0, 1, 2
	}

	console.log(switchState);
</script>

<Dropdown
	bind:show
	on:change={(e) => {
		if (e.detail === false) {
			onClose();
		}
	}}
>
	<Tooltip content={$i18n.t('RAG')}>
		<slot />
	</Tooltip>

	<div slot="content">
		<DropdownMenu.Content
			class="w-full max-w-[190px] rounded-xl px-1 py-1  border-gray-300/30 dark:border-gray-700/50 z-50 bg-white dark:bg-gray-850 dark:text-white shadow"
			sideOffset={15}
			alignOffset={-8}
			side="top"
			align="start"
			transition={flyAndScale}
		>
			<DropdownMenu.Item
				class="flex gap-2 items-center px-3 py-2 text-sm font-medium cursor-pointer rounded-xl"
				on:click={toggleState}
			>
				<DocumentArrowUpSolid />
					<div class="flex items-center">{$i18n.t('Switch State')}</div>
					<div class="ml-auto">
						<!-- Display the current state -->
						{$switchState}
					</div>
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</div>
</Dropdown>
