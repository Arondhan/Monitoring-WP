<template>
  <button
    @click="$emit('update:modelValue', !modelValue)"
    :class="[
      modelValue ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600',
      'relative inline-flex h-6 w-11 items-center rounded-full transition-colors'
    ]"
    type="button"
  >
    <span
      :class="[
        modelValue ? 'translate-x-6' : 'translate-x-1',
        'inline-block h-4 w-4 transform rounded-full bg-white transition-transform'
      ]"
    />
  </button>
</template>

<script>
export default {
  name: 'ToggleSwitch',
  props: {
    modelValue: Boolean
  },
  emits: ['update:modelValue'],
}
</script>
