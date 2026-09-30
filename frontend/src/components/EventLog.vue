<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
    <div class="p-6 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Журнал событий</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">История проверок и инцидентов</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="p-6 flex justify-center">
      <svg class="animate-spin h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Empty State -->
    <div v-else-if="events.length === 0" class="p-6 text-center text-gray-500 dark:text-gray-400">
      Нет событий
    </div>

    <!-- Events Table -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Время
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Статус
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Время ответа
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              HTTP код
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Детали
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="event in events" :key="event.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
              {{ formatTimestamp(event.timestamp) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusClass(event.status)">
                {{ event.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm" :class="getResponseTimeColor(event.response_time_ms)">
              {{ event.response_time_ms ? `${event.response_time_ms} мс` : '—' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
              {{ event.status_code || '—' }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400 max-w-md truncate">
              {{ event.error_message || (event.ssl_days_remaining !== null && event.ssl_days_remaining !== undefined ? `SSL истекает через ${event.ssl_days_remaining} дн.` : 'OK') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Load More -->
    <div v-if="hasMore" class="p-4 border-t border-gray-200 dark:border-gray-700 text-center">
      <button
        @click="$emit('loadMore')"
        class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm font-medium"
      >
        Загрузить ещё
      </button>
    </div>
  </div>
</template>

<script setup>
import { format } from 'date-fns'

const props = defineProps({
  events: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  hasMore: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['loadMore'])

function formatTimestamp(timestamp) {
  try {
    return format(new Date(timestamp), 'MMM d, yyyy HH:mm:ss')
  } catch {
    return timestamp
  }
}

function getStatusClass(status) {
  const classes = {
    UP: 'bg-green-100 text-green-800',
    SLOW: 'bg-yellow-100 text-yellow-800',
    DOWN: 'bg-red-100 text-red-800',
    SSL_ERROR: 'bg-orange-100 text-orange-800',
    SSL_WARNING: 'bg-yellow-100 text-yellow-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

function getResponseTimeColor(responseTime) {
  if (responseTime == null) return 'text-gray-400'
  if (responseTime >= 1500) return 'text-yellow-600'
  if (responseTime >= 1000) return 'text-orange-600'
  return 'text-green-600'
}
</script>
