<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow cursor-pointer"
       @click="$emit('click')">
    <div class="flex items-start justify-between">
      <div class="flex items-center space-x-3 flex-1 min-w-0">
        <div class="relative">
          <div class="w-3 h-3 rounded-full" :class="statusColorClass"></div>
          <div v-if="isChecking" class="absolute inset-0 w-3 h-3 rounded-full animate-ping opacity-75"
               :class="statusColorClass"></div>
        </div>

        <div class="flex-1 min-w-0">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white truncate">{{ domain.name }}</h3>
          <a :href="domain.url" target="_blank" class="text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 truncate block">
            {{ domain.url }}
          </a>
        </div>
      </div>

      <div class="flex items-center space-x-2">
        <button
          @click.stop="$emit('edit')"
          class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          title="Редактировать"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
        </button>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="statusBadgeClass">
          {{ statusText }}
        </span>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="mt-4 grid grid-cols-3 gap-4">
      <div>
        <div class="text-xs text-gray-500 dark:text-gray-400">Время ответа</div>
        <div class="mt-1 text-sm font-medium" :class="responseTimeColor">
          {{ responseTimeText }}
        </div>
      </div>
      <div>
        <div class="text-xs text-gray-500 dark:text-gray-400">Аптайм (24ч)</div>
        <div class="mt-1 text-sm font-medium" :class="uptimeColor">
          {{ domain.uptime_percentage_24h }}%
        </div>
      </div>
      <div>
        <div class="text-xs text-gray-500 dark:text-gray-400">Последняя проверка</div>
        <div class="mt-1 text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ lastCheckedText }}
        </div>
      </div>
    </div>

    <!-- Uptime Bar -->
    <div class="mt-3">
      <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
        <span>Аптайм за 7 дней</span>
        <span>{{ domain.uptime_percentage_7d }}%</span>
      </div>
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div class="h-2 rounded-full transition-all duration-500"
             :class="uptimeBarColor"
             :style="{ width: domain.uptime_percentage_7d + '%' }"></div>
      </div>
    </div>

    <!-- WordPress Status -->
    <div v-if="domain.is_wordpress" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12.042 0C5.414 0 .021 5.376.021 11.98c0 5.288 3.439 9.787 8.199 11.373-.11-.937-.227-2.482.025-3.566.203-.873 1.316-5.567 1.316-5.567s-.335-.67-.335-1.659c0-1.552.9-2.704 2.023-2.704.953 0 1.413.716 1.413 1.572 0 .958-.61 2.392-.924 3.72-.263 1.113.557 2.02 1.654 2.02 1.984 0 3.514-2.09 3.514-5.105 0-2.67-1.922-4.537-4.668-4.537-3.185 0-5.056 2.388-5.056 4.857 0 .963.371 1.995.834 2.557a.34.34 0 01.078.323c-.086.357-.279 1.113-.316 1.27-.05.21-.166.254-.383.154-1.422-.662-2.31-2.736-2.31-4.408 0-3.59 2.61-6.887 7.526-6.887 3.948 0 7.018 2.815 7.018 6.576 0 3.926-2.471 7.083-5.903 7.083-1.15 0-2.23-.598-2.602-1.304 0 0-.57 2.166-.708 2.704-.256.986-.948 2.213-1.413 2.968A11.934 11.934 0 0012 23.979c6.627 0 12.021-5.376 12.021-11.98C24.063 5.376 18.67 0 12.042 0z"/>
          </svg>
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">WordPress</span>
        </div>
        <div class="flex items-center space-x-1">
          <span v-if="wordpressPostStatus" class="w-2 h-2 rounded-full" :class="wordpressPostStatus.color"></span>
          <span class="text-xs" :class="wordpressPostStatus ? wordpressPostStatus.textClass : 'text-gray-500'">
            {{ wordpressPostStatus ? wordpressPostStatus.text : 'Нет данных' }}
          </span>
        </div>
      </div>
      <div v-if="domain.last_post_date" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
        Последний пост: {{ wordpressPostAgeText }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatDistanceToNow } from 'date-fns'

const props = defineProps({
  domain: {
    type: Object,
    required: true,
  },
  isChecking: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['click'])

const statusConfig = {
  UP: { color: 'bg-status-up', badge: 'bg-green-100 text-green-800', text: 'OK' },
  SLOW: { color: 'bg-status-slow', badge: 'bg-yellow-100 text-yellow-800', text: 'Медленно' },
  DOWN: { color: 'bg-status-down', badge: 'bg-red-100 text-red-800', text: 'Недоступен' },
  SSL_ERROR: { color: 'bg-status-sslError', badge: 'bg-orange-100 text-orange-800', text: 'Ошибка SSL' },
  PENDING: { color: 'bg-status-pending', badge: 'bg-gray-100 text-gray-800', text: 'Проверка...' },
}

const status = computed(() => props.domain.last_status || 'PENDING')
const config = computed(() => statusConfig[status.value] || statusConfig.PENDING)

const statusColorClass = computed(() => `${config.value.color} ${status.value === 'DOWN' || status.value === 'SSL_ERROR' ? 'status-pulse-down' : ''}`)
const statusBadgeClass = computed(() => config.value.badge)
const statusText = computed(() => config.value.text)

const responseTimeText = computed(() => {
  if (props.domain.last_response_time_ms == null) return '—'
  return `${props.domain.last_response_time_ms} мс`
})

const responseTimeColor = computed(() => {
  if (props.domain.last_response_time_ms == null) return 'text-gray-400'
  if (props.domain.last_response_time_ms >= 1500) return 'text-status-slow'
  if (props.domain.last_response_time_ms >= 1000) return 'text-yellow-600'
  return 'text-status-up'
})

const uptimeColor = computed(() => {
  const uptime = props.domain.uptime_percentage_24h
  if (uptime >= 99) return 'text-status-up'
  if (uptime >= 95) return 'text-status-slow'
  return 'text-status-down'
})

const uptimeBarColor = computed(() => {
  const uptime = props.domain.uptime_percentage_7d
  if (uptime >= 99) return 'bg-status-up'
  if (uptime >= 95) return 'bg-status-slow'
  return 'bg-status-down'
})

const lastCheckedText = computed(() => {
  if (!props.domain.last_checked_at) return 'Никогда'
  try {
    return formatDistanceToNow(new Date(props.domain.last_checked_at), { addSuffix: true })
  } catch {
    return 'Недавно'
  }
})

// WordPress вычисляемые свойства
const wordpressPostStatus = computed(() => {
  if (!props.domain.is_wordpress) return null

  if (!props.domain.last_post_date) {
    return null
  }

  const status = props.domain.wordpress_post_status
  if (status === 'fresh') {
    return { color: 'bg-green-500', text: 'Свежий', textClass: 'text-green-600 dark:text-green-400' }
  } else if (status === 'warning') {
    return { color: 'bg-yellow-500', text: 'Внимание', textClass: 'text-yellow-600 dark:text-yellow-400' }
  } else if (status === 'stale') {
    return { color: 'bg-red-500', text: 'Устарел', textClass: 'text-red-600 dark:text-red-400' }
  }
  return null
})

const wordpressPostAgeText = computed(() => {
  if (!props.domain.last_post_date) return 'Нет данных'
  try {
    return formatDistanceToNow(new Date(props.domain.last_post_date), { addSuffix: true })
  } catch {
    return 'Недавно'
  }
})
</script>
