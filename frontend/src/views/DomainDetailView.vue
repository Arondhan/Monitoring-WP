<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-red-600 dark:text-red-400">{{ error }}</p>
      <button
        @click="$router.push('/')"
        class="mt-4 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
      >
        ← На панель мониторинга
      </button>
    </div>

    <!-- Content -->
    <div v-else-if="domain" class="py-6">
      <!-- Back Button -->
      <div class="mb-4">
        <button
          @click="$router.push('/')"
          class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          На панель мониторинга
        </button>
      </div>

      <!-- Header Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div class="flex items-start space-x-4">
            <div class="relative mt-1">
              <div class="w-4 h-4 rounded-full" :class="statusIndicatorClass"></div>
            </div>

            <div>
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ domain.name }}</h1>
              <a :href="domain.url" target="_blank" rel="noopener noreferrer"
                 class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center mt-1">
                {{ domain.url }}
                <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
              </a>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
                Интервал проверки: каждые {{ checkIntervalText }}
              </p>
            </div>
          </div>

          <span class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium self-start"
                :class="statusBadgeClass">
            <span class="w-2 h-2 mr-2 rounded-full" :class="statusDotClass"></span>
            {{ statusText }}
          </span>
        </div>

        <!-- Stats Grid -->
        <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div class="text-sm text-gray-500 dark:text-gray-400">Время ответа</div>
            <div class="mt-1 text-2xl font-bold" :class="responseTimeColor">
              {{ domain.last_response_time_ms ?? '—' }}
              <span class="text-sm font-normal text-gray-500 dark:text-gray-400">мс</span>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div class="text-sm text-gray-500 dark:text-gray-400">Аптайм (24ч)</div>
            <div class="mt-1 text-2xl font-bold" :class="uptime24hColor">
              {{ domain.uptime_percentage_24h }}%
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div class="text-sm text-gray-500 dark:text-gray-400">Аптайм (7д)</div>
            <div class="mt-1 text-2xl font-bold" :class="uptime7dColor">
              {{ domain.uptime_percentage_7d }}%
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div class="text-sm text-gray-500 dark:text-gray-400">Последняя проверка</div>
            <div class="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
              {{ lastCheckedText }}
            </div>
          </div>
        </div>

        <!-- SSL Info -->
        <div v-if="latestCheck && latestCheck.ssl_days_remaining !== null"
             class="mt-4 p-4 rounded-lg"
             :class="sslAlertClass">
          <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
            </svg>
            <span class="font-medium text-gray-900 dark:text-white">
              SSL сертификат истекает через {{ latestCheck.ssl_days_remaining }} дн.
              <span v-if="latestCheck.ssl_expires_at" class="text-sm opacity-75">
                ({{ sslExpiryDate }})
              </span>
            </span>
          </div>
        </div>

        <!-- WordPress Info -->
        <div v-if="domain.is_wordpress"
             class="mt-4 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.042 0C5.414 0 .021 5.376.021 11.98c0 5.288 3.439 9.787 8.199 11.373-.11-.937-.227-2.482.025-3.566.203-.873 1.316-5.567 1.316-5.567s-.335-.67-.335-1.659c0-1.552.9-2.704 2.023-2.704.953 0 1.413.716 1.413 1.572 0 .958-.61 2.392-.924 3.72-.263 1.113.557 2.02 1.654 2.02 1.984 0 3.514-2.09 3.514-5.105 0-2.67-1.922-4.537-4.668-4.537-3.185 0-5.056 2.388-5.056 4.857 0 .963.371 1.995.834 2.557a.34.34 0 01.078.323c-.086.357-.279 1.113-.316 1.27-.05.21-.166.254-.383.154-1.422-.662-2.31-2.736-2.31-4.408 0-3.59 2.61-6.887 7.526-6.887 3.948 0 7.018 2.815 7.018 6.576 0 3.926-2.471 7.083-5.903 7.083-1.15 0-2.23-.598-2.602-1.304 0 0-.57 2.166-.708 2.704-.256.986-.948 2.213-1.413 2.968A11.934 11.934 0 0012 23.979c6.627 0 12.021-5.376 12.021-11.98C24.063 5.376 18.67 0 12.042 0z"/>
                </svg>
                <h3 class="text-lg font-semibold text-green-800 dark:text-green-200">WordPress сайт</h3>
              </div>

              <div class="mt-4 space-y-3">
                <div v-if="domain.last_post_date">
                  <div class="text-sm text-green-700 dark:text-green-300 mb-1">
                    📄 Последний пост
                  </div>
                  <div class="flex items-center space-x-2">
                    <span
                      class="w-2 h-2 rounded-full"
                      :class="wordpressPostAgeColor"
                    ></span>
                    <span class="font-medium text-gray-900 dark:text-white">
                      {{ formatPostDate(domain.last_post_date) }}
                    </span>
                    <span class="text-sm text-gray-500 dark:text-gray-400">
                      ({{ wordpressPostAgeText }})
                    </span>
                  </div>
                  <div v-if="domain.last_post_title" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    {{ domain.last_post_title }}
                  </div>
                </div>

                <div v-else class="text-gray-600 dark:text-gray-400">
                  Нет информации о последних постах
                </div>

                <div class="text-xs text-green-600 dark:text-green-400">
                  Последняя проверка WordPress: {{ wordpressLastCheckedText }}
                </div>
              </div>
            </div>

            <button
              @click="checkWordPress"
              :disabled="checkingWordPress"
              class="ml-4 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-md text-sm font-medium transition-colors"
            >
              <svg v-if="!checkingWordPress" class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <svg v-else class="animate-spin w-4 h-4 mr-2 inline" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ checkingWordPress ? 'Проверка...' : 'Обновить' }}
            </button>
          </div>
        </div>

        <!-- WordPress Content Info -->
        <div v-if="domain.is_wordpress" class="mt-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">📄 Контент страницы</h3>
            <button @click="loadContent" :disabled="contentLoading"
                    class="px-3 py-1.5 text-sm bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50">
              🔄 Обновить
            </button>
          </div>

          <div class="space-y-6">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <h4 class="font-semibold mb-3 text-gray-900 dark:text-white">🏷️ Meta информация</h4>

              <div v-if="content?.meta_title" class="mb-4">
                <div class="flex items-center justify-between mb-1">
                  <div class="text-xs text-gray-500 dark:text-gray-400">Meta Title:</div>
                  <div class="text-xs" :class="content.meta_title_length > 60 ? 'text-yellow-600 dark:text-yellow-400' : 'text-green-600 dark:text-green-400'">
                    {{ content.meta_title_length }} симв.
                    <span v-if="content.meta_title_length > 60" class="ml-1">⚠️</span>
                    <span v-else-if="content.meta_title_length < 30" class="ml-1">ℹ️</span>
                  </div>
                </div>
                <div class="text-sm text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 p-2 rounded">
                  {{ content.meta_title }}
                </div>
              </div>

              <div v-if="content?.meta_description" class="mb-3">
                <div class="flex items-center justify-between mb-1">
                  <div class="text-xs text-gray-500 dark:text-gray-400">Meta Description:</div>
                  <div class="text-xs" :class="getContentLengthClass(content.meta_description_length)">
                    {{ content.meta_description_length }} симв.
                    <span v-if="content.meta_description_length > 160" class="ml-1">⚠️</span>
                    <span v-else-if="content.meta_description_length < 120" class="ml-1">ℹ️</span>
                    <span v-else class="ml-1">✅</span>
                  </div>
                </div>
                <div class="text-sm text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 p-2 rounded">
                  {{ content.meta_description }}
                </div>
              </div>

              <div v-if="!content?.meta_title && !content?.meta_description"
                   class="text-sm text-gray-500 dark:text-gray-400">
                Нет данных
              </div>
            </div>

            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <h4 class="font-semibold mb-3 text-gray-900 dark:text-white">📝 Заголовки</h4>

              <div v-if="content?.h1" class="mb-4">
                <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">H1:</div>
                <div class="text-base font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 p-3 rounded">
                  {{ content.h1 }}
                </div>
              </div>

              <div v-if="content?.h2 && content.h2.length > 0">
                <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  H2 ({{ content.h2.length }}):
                </div>
                <ul class="space-y-2">
                  <li v-for="(h2, index) in content.h2" :key="index"
                      class="text-sm text-gray-900 dark:text-white pl-4 border-l-4 border-gray-300 dark:border-gray-600">
                    {{ h2 }}
                  </li>
                </ul>
              </div>

              <div v-if="!content?.h1 && (!content?.h2 || content.h2.length === 0)"
                   class="text-sm text-gray-500 dark:text-gray-400">
                Нет данных
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="mt-6 flex gap-3">
          <button
            @click="refreshCheck"
            :disabled="refreshing"
            class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            <svg v-if="!refreshing" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ refreshing ? 'Проверка...' : 'Проверить сейчас' }}
          </button>

          <button
            @click="showDeleteConfirm = true"
            class="inline-flex items-center px-4 py-2 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-400 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            Удалить
          </button>
        </div>
      </div>

      <!-- Uptime Chart -->
      <div class="mt-6">
        <UptimeChart
          v-model:period="chartPeriod"
          :checks="checks"
        />
      </div>

      <!-- Event Log -->
      <div class="mt-6">
        <EventLog
          :events="checks"
          :loading="checksLoading"
          :has-more="false"
        />
      </div>

      <!-- Incidents Section -->
      <div v-if="incidents.length > 0" class="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Последние инциденты</h2>
        <div class="space-y-3">
          <div v-for="incident in incidents" :key="incident.id"
               class="p-4 rounded-lg border"
               :class="incident.is_resolved ? 'bg-gray-50 dark:bg-gray-700' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="incident.is_resolved ? 'bg-gray-100 dark:bg-gray-600 text-gray-800 dark:text-gray-200' : 'bg-red-100 dark:bg-red-800 text-red-800 dark:text-red-200'">
                  {{ incident.is_resolved ? 'Resolved' : 'Active' }}
                </span>
                <span class="font-medium text-gray-900 dark:text-white">{{ formatReason(incident.reason) }}</span>
              </div>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ formatIncidentTime(incident) }}
              </span>
            </div>
            <p v-if="incident.error_details" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {{ incident.error_details }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="fixed inset-0 bg-black bg-opacity-50" @click="showDeleteConfirm = false"></div>
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Удалить домен?</h3>
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            Вы уверены, что хотите удалить "{{ domain?.name }}"? Это действие нельзя отменить, и вся история проверок будет потеряна.
          </p>
          <div class="flex gap-3">
            <button
              @click="showDeleteConfirm = false"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Отмена
            </button>
            <button
              @click="handleDelete"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { formatDistanceToNow, format } from 'date-fns'
import { domainsApi } from '../stores/api'
import UptimeChart from '../components/UptimeChart.vue'
import EventLog from '../components/EventLog.vue'

const route = useRoute()
const router = useRouter()

const domain = ref(null)
const checks = ref([])
const incidents = ref([])
const loading = ref(true)
const error = ref(null)
const checksLoading = ref(false)
const refreshing = ref(false)
const chartPeriod = ref('24h')
const showDeleteConfirm = ref(false)
const checkingWordPress = ref(false)

const latestCheck = computed(() => checks.value[0])

const statusConfig = {
  UP: { indicator: 'bg-status-up', badge: 'bg-green-100 text-green-800', dot: 'bg-status-up', text: 'OK' },
  SLOW: { indicator: 'bg-status-slow', badge: 'bg-yellow-100 text-yellow-800', dot: 'bg-status-slow', text: 'Медленно' },
  DOWN: { indicator: 'bg-status-down', badge: 'bg-red-100 text-red-800', dot: 'bg-status-down', text: 'Недоступен' },
  SSL_ERROR: { indicator: 'bg-status-sslError', badge: 'bg-orange-100 text-orange-800', dot: 'bg-status-sslError', text: 'Ошибка SSL' },
  PENDING: { indicator: 'bg-status-pending', badge: 'bg-gray-100 text-gray-800', dot: 'bg-status-pending', text: 'Проверка...' },
}

const status = computed(() => domain.value?.last_status || 'PENDING')
const config = computed(() => statusConfig[status.value] || statusConfig.PENDING)

const statusIndicatorClass = computed(() => config.value.indicator)
const statusBadgeClass = computed(() => config.value.badge)
const statusDotClass = computed(() => config.value.dot)
const statusText = computed(() => config.value.text)

const responseTimeColor = computed(() => {
  const time = domain.value?.last_response_time_ms
  if (time == null) return 'text-gray-400'
  if (time >= 1500) return 'text-status-slow'
  if (time >= 1000) return 'text-orange-600'
  return 'text-status-up'
})

const uptime24hColor = computed(() => {
  const uptime = domain.value?.uptime_percentage_24h
  if (uptime >= 99) return 'text-status-up'
  if (uptime >= 95) return 'text-status-slow'
  return 'text-status-down'
})

const uptime7dColor = computed(() => {
  const uptime = domain.value?.uptime_percentage_7d
  if (uptime >= 99) return 'text-status-up'
  if (uptime >= 95) return 'text-status-slow'
  return 'text-status-down'
})

const lastCheckedText = computed(() => {
  if (!domain.value?.last_checked_at) return 'Никогда'
  try {
    return formatDistanceToNow(new Date(domain.value.last_checked_at), { addSuffix: true })
  } catch {
    return 'Недавно'
  }
})

const sslExpiryDate = computed(() => {
  if (!latestCheck.value?.ssl_expires_at) return ''
  try {
    return format(new Date(latestCheck.value.ssl_expires_at), 'MMM d, yyyy')
  } catch {
    return ''
  }
})

const checkIntervalText = computed(() => {
  const seconds = domain.value?.check_interval_seconds || 0
  if (seconds < 60) return `${seconds} сек`
  if (seconds < 3600) return `${Math.floor(seconds / 60)} мин`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} ч`
  return `${Math.floor(seconds / 86400)} дн`
})

const sslAlertClass = computed(() => {
  const days = latestCheck.value?.ssl_days_remaining
  if (days == null) return 'bg-gray-50 dark:bg-gray-700'
  if (days <= 0) return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
  if (days <= 14) return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
  return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
})

onMounted(async () => {
  await loadData()
  if (domain.value?.is_wordpress) {
    await loadContent()
  }
})

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const [domainData, checksData, incidentsData] = await Promise.all([
      domainsApi.getDomain(route.params.id),
      domainsApi.getChecks(route.params.id, { period: chartPeriod.value }),
      domainsApi.getIncidents(route.params.id, { limit: 10 }),
    ])
    domain.value = domainData
    checks.value = checksData.items || []
    incidents.value = incidentsData.items || []
  } catch (err) {
    error.value = 'Не удалось загрузить данные домена'
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function refreshCheck() {
  refreshing.value = true
  try {
    await domainsApi.triggerCheck(route.params.id)
    await new Promise(resolve => setTimeout(resolve, 2000))
    await loadData()
  } catch (err) {
    console.error('Failed to refresh check:', err)
  } finally {
    refreshing.value = false
  }
}

async function handleDelete() {
  try {
    await domainsApi.deleteDomain(route.params.id)
    router.push('/')
  } catch (err) {
    console.error('Failed to delete domain:', err)
  }
}

function formatReason(reason) {
  return reason.replace(/_/g, ' ')
}

function formatIncidentTime(incident) {
  try {
    if (incident.is_resolved && incident.end_time && incident.start_time) {
      const duration = incident.duration_seconds || Math.round((new Date(incident.end_time) - new Date(incident.start_time)) / 1000)
      const hours = Math.floor(duration / 3600)
      const mins = Math.floor((duration % 3600) / 60)
      return `${format(new Date(incident.start_time), 'MMM d, HH:mm')} - ${format(new Date(incident.end_time), 'HH:mm')} (${hours}h ${mins}m)`
    }
    return `Started ${formatDistanceToNow(new Date(incident.start_time), { addSuffix: true })}`
  } catch {
    return 'Unknown time'
  }
}

// WordPress вычисляемые свойства
const wordpressPostAgeDays = computed(() => {
  if (!domain.value?.last_post_date) return null

  const now = new Date()
  const postDate = new Date(domain.value.last_post_date)
  const diffMs = now - postDate
  return Math.floor(diffMs / (1000 * 60 * 60 * 24))
})

const wordpressPostAgeText = computed(() => {
  const days = wordpressPostAgeDays.value
  if (days === null) return 'Нет данных'
  if (days === 0) return 'Сегодня'
  if (days === 1) return 'Вчера'
  if (days < 7) return `${days} дн. назад`
  if (days < 30) return `${Math.floor(days / 7)} нед. назад`
  return `${Math.floor(days / 30)} мес. назад`
})

const wordpressPostAgeColor = computed(() => {
  const days = wordpressPostAgeDays.value
  if (days === null) return 'bg-gray-400'
  if (days < 7) return 'bg-green-500'
  if (days < 30) return 'bg-yellow-500'
  return 'bg-red-500'
})

const wordpressLastCheckedText = computed(() => {
  if (!domain.value?.last_post_checked_at) return 'Никогда'
  try {
    return formatDistanceToNow(new Date(domain.value.last_post_checked_at), { addSuffix: true })
  } catch {
    return 'Недавно'
  }
})

const formatPostDate = (dateString) => {
  if (!dateString) return 'Нет данных'
  try {
    const date = new Date(dateString)
    return format(date, 'd MMMM yyyy')
  } catch {
    return 'Нет данных'
  }
}

async function checkWordPress() {
  checkingWordPress.value = true
  try {
    await domainsApi.checkWordPress(route.params.id)
    await new Promise(resolve => setTimeout(resolve, 2000))
    await loadData()
  } catch (err) {
    console.error('Failed to check WordPress:', err)
  } finally {
    checkingWordPress.value = false
  }
}

const content = ref(null)
const contentLoading = ref(false)

async function loadContent() {
  if (!domain.value?.is_wordpress) return

  contentLoading.value = true
  try {
    content.value = await domainsApi.getDomainContent(route.params.id)
  } catch (err) {
    console.error('Failed to load content:', err)
    content.value = null
  } finally {
    contentLoading.value = false
  }
}

function getContentLengthClass(length) {
  if (!length) return 'text-gray-400'
  if (length > 160) return 'text-yellow-600 dark:text-yellow-400'
  if (length < 120) return 'text-orange-600 dark:text-orange-400'
  return 'text-green-600 dark:text-green-400'
}
</script>
