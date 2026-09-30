<template>
  <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:flex-wrap">
    <div class="flex items-center gap-2">
      <span class="text-sm text-gray-600 dark:text-gray-400">Статус:</span>
      <div class="flex gap-1 flex-wrap">
        <button
          v-for="option in statusOptions"
          :key="option.value"
          @click="$emit('filter', option.value)"
          class="px-3 py-1.5 text-sm rounded-md transition-colors"
          :class="activeFilter === option.value
            ? 'bg-primary-600 text-white'
            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border dark:border-gray-600'"
        >
          {{ option.label }}
          <span v-if="option.count !== undefined" class="ml-1.5 text-xs opacity-75">
            ({{ option.count }})
          </span>
        </button>
      </div>
    </div>

    <!-- WordPress фильтр -->
    <div v-if="showWordpressFilter" class="flex items-center gap-2 flex-wrap">
      <span class="text-sm text-gray-600 dark:text-gray-400">WordPress:</span>
      <div class="flex gap-1 flex-wrap">
        <button
          v-for="option in wordpressOptions"
          :key="option.value"
          @click="$emit('wordpress-filter', option.value)"
          class="px-3 py-1.5 text-sm rounded-md transition-colors flex items-center gap-1"
          :class="wordpressFilter === option.value
            ? 'bg-primary-600 text-white'
            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border dark:border-gray-600'"
        >
          <span v-if="option.icon">{{ option.icon }}</span>
          {{ option.label }}
          <span v-if="option.count !== undefined" class="ml-1 text-xs opacity-75">
            ({{ option.count }})
          </span>
        </button>
      </div>
    </div>

    <div class="flex items-center gap-2 sm:ml-auto">
      <span class="text-sm text-gray-600 dark:text-gray-400">Сортировка:</span>
      <select
        :value="sortBy"
        @input="$emit('sort', $event.target.value)"
        class="px-3 py-1.5 text-sm border dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:ring-primary-500 focus:border-primary-500"
      >
        <option value="created_at">Дата добавления</option>
        <option value="status">Статус</option>
        <option value="name">Название</option>
        <option value="last_response_time_ms">Время ответа</option>
        <option value="uptime_percentage_24h">Аптайм</option>
      </select>

      <button
        @click="$emit('sortOrder', sortOrder === 'desc' ? 'asc' : 'desc')"
        class="p-1.5 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
        :title="sortOrder === 'desc' ? 'По убыванию' : 'По возрастанию'"
      >
        <svg v-if="sortOrder === 'desc'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { watchEffect } from 'vue'

const props = defineProps({
  activeFilter: {
    type: String,
    default: '',
  },
  sortBy: {
    type: String,
    default: 'created_at',
  },
  sortOrder: {
    type: String,
    default: 'desc',
  },
  statusCounts: {
    type: Object,
    default: () => ({ up: 0, down: 0, slow: 0, sslError: 0, pending: 0 }),
  },
  wordpressFilter: {
    type: String,
    default: '',
  },
  wordpressStats: {
    type: Object,
    default: () => ({ total: 0, fresh: 0, warning: 0, stale: 0, no_posts: 0 }),
  },
  showWordpressFilter: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['filter', 'sort', 'sortOrder', 'wordpress-filter'])

const statusOptions = [
  { value: '', label: 'Все', count: undefined },
  { value: 'UP', label: 'OK', count: undefined },
  { value: 'DOWN', label: 'Недоступен', count: undefined },
  { value: 'SLOW', label: 'Медленно', count: undefined },
  { value: 'SSL_ERROR', label: 'Ошибка SSL', count: undefined },
  { value: 'PENDING', label: 'Проверка', count: undefined },
]

const wordpressOptions = [
  { value: '', label: 'Все', count: undefined, icon: '' },
  { value: 'wordpress', label: 'WordPress', count: undefined, icon: '🔵' },
  { value: 'fresh', label: 'Свежие', count: undefined, icon: '🟢' },
  { value: 'warning', label: 'Внимание', count: undefined, icon: '🟡' },
  { value: 'stale', label: 'Устаревшие', count: undefined, icon: '🔴' },
]

const updateCounts = () => {
  statusOptions.forEach(opt => {
    if (opt.value === '') {
      opt.count = undefined
    } else {
      const key = opt.value.toLowerCase()
      opt.count = props.statusCounts[key] || 0
    }
  })

  wordpressOptions.forEach(opt => {
    if (opt.value === '' || opt.value === 'wordpress') {
      opt.count = opt.value === 'wordpress' ? props.wordpressStats.total : undefined
    } else {
      opt.count = props.wordpressStats[opt.value] || 0
    }
  })
}

watchEffect(() => {
  updateCounts()
})
</script>
