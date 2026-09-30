<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto">
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-800 dark:text-white">
          ⚙️ Настройки
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
          Управление прокси и настройками приложения
        </p>
      </div>

      <div class="mb-6 border-b border-gray-200 dark:border-gray-700">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            {{ tab.icon }} {{ tab.name }}
          </button>
        </nav>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Загрузка...</p>
      </div>

      <div v-else>
        <ProxyManager v-if="activeTab === 'proxies'" />

        <WhiteListManager v-if="activeTab === 'whitelist'" />

        <div v-if="activeTab === 'security'" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
            🔒 Настройки безопасности
          </h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">Использовать прокси</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Проверять домены через прокси для обнаружения эксплойтов
                </p>
              </div>
              <toggle-switch v-model="securitySettings.proxy_enabled" />
            </div>

            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">Детектирование вредоносных ссылок</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Проверка HTML на наличие подозрительных ссылок
                </p>
              </div>
              <toggle-switch v-model="securitySettings.detect_malicious_links" />
            </div>

            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">Детектирование редиректов</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Обнаружение неожиданных редиректов
                </p>
              </div>
              <toggle-switch v-model="securitySettings.detect_redirects" />
            </div>

            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-white">Детектирование iframe</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Обнаружение встроенных iframe (возможный кликджекинг)
                </p>
              </div>
              <toggle-switch v-model="securitySettings.detect_iframes" />
            </div>

            <div class="pt-4">
              <button
                @click="saveSecuritySettings"
                class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition"
              >
                Сохранить настройки
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import ProxyManager from '@/components/settings/ProxyManager.vue'
import ToggleSwitch from '@/components/ui/ToggleSwitch.vue'
import WhiteListManager from '@/components/settings/WhiteListManager.vue'

const settingsStore = useSettingsStore()

const activeTab = ref('proxies')
const loading = ref(false)

const tabs = [
  { id: 'proxies', name: 'Прокси', icon: '🌐' },
  { id: 'whitelist', name: 'Белый список', icon: '🔒' },
  { id: 'security', name: 'Безопасность', icon: '🛡️' },
]

const securitySettings = ref({
  proxy_enabled: false,
  default_proxy_id: null,
  check_interval_seconds: 300,
  detect_malicious_links: true,
  detect_redirects: true,
  detect_iframes: true,
})

const loadDashboard = async () => {
  loading.value = true
  await settingsStore.loadDashboard()
  loading.value = false
}

const loadSettings = async () => {
  const security = await settingsStore.loadSecuritySettings()
  if (security) securitySettings.value = security
}

const saveSecuritySettings = async () => {
  try {
    await settingsStore.updateSecuritySettings(securitySettings.value)
    alert('✅ Настройки безопасности сохранены!')
  } catch (err) {
    alert('❌ Ошибка сохранения настроек')
  }
}

onMounted(() => {
  loadDashboard()
  loadSettings()
})
</script>
