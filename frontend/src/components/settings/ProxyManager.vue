<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
      🌐 Прокси серверы
    </h2>

    <div v-if="error" class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded">
      {{ error }}
    </div>

    <!-- Статистика -->
    <div class="grid grid-cols-3 gap-4 mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Всего</div>
      </div>
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
        <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Активных</div>
      </div>
      <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 text-center">
        <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ stats.working }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Рабочих</div>
      </div>
    </div>

    <!-- Кнопка добавления -->
    <div class="mb-4">
      <button
        @click="showAddForm = true"
        class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
      >
        + Добавить прокси
      </button>
    </div>

    <!-- Список прокси -->
    <div class="space-y-3">
      <div 
        v-for="proxy in proxies" 
        :key="proxy.id"
        class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-750"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <h3 class="font-bold text-gray-900 dark:text-white">{{ proxy.name }}</h3>
              <span 
                v-if="proxy.is_working === true"
                class="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs rounded"
              >
                ✓ Рабочий
              </span>
              <span 
                v-else-if="proxy.is_working === false"
                class="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs rounded"
              >
                ✗ Не работает
              </span>
              <span 
                v-else
                class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded"
              >
                ? Не проверен
              </span>
            </div>
            
            <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <div>
                <span class="font-medium">Подключение:</span>
                <code class="ml-2 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">
                  {{ proxy.protocol }}://{{ proxy.host }}:{{ proxy.port }}
                </code>
              </div>
              <div v-if="proxy.username">
                <span class="font-medium">Логин:</span> {{ proxy.username }}
              </div>
              <div v-if="proxy.country">
                <span class="font-medium">Страна:</span> {{ proxy.country }}
              </div>
              <div>
                <span class="font-medium">Тип:</span> {{ getUsageTypeLabel(proxy.usage_type) }}
              </div>
              <div v-if="proxy.description" class="text-gray-500 dark:text-gray-500">
                {{ proxy.description }}
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-2">
            <button
              @click="testProxy(proxy.id)"
              :disabled="isTesting"
              class="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white text-sm rounded transition"
            >
              {{ isTestingProxy === proxy.id ? '⏳ Тест...' : '🧪 Тест' }}
            </button>
            <button
              @click="editProxy(proxy)"
              class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition"
            >
              ✏️
            </button>
            <button
              @click="deleteProxy(proxy.id)"
              class="px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition"
            >
              ✕
            </button>
          </div>
        </div>
      </div>

      <div v-if="proxies.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8">
        Нет прокси серверов. Добавьте первый прокси!
      </div>
    </div>

    <!-- Форма добавления/редактирования -->
    <div v-if="showAddForm || editingProxy" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <h3 class="text-xl font-bold mb-4 text-gray-800 dark:text-white">
            {{ editingProxy ? 'Редактировать прокси' : 'Добавить прокси' }}
          </h3>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Название *
              </label>
              <input 
                v-model="formData.name"
                type="text"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Описание
              </label>
              <textarea 
                v-model="formData.description"
                rows="2"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Хост *
                </label>
                <input 
                  v-model="formData.host"
                  type="text"
                  required
                  placeholder="proxy.example.com"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Порт *
                </label>
                <input 
                  v-model.number="formData.port"
                  type="number"
                  required
                  min="1"
                  max="65535"
                  placeholder="8080"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Логин
                </label>
                <input 
                  v-model="formData.username"
                  type="text"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Пароль
                </label>
                <input 
                  v-model="formData.password"
                  type="text"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Протокол
                </label>
                <select 
                  v-model="formData.protocol"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="http">HTTP</option>
                  <option value="https">HTTPS</option>
                  <option value="socks5">SOCKS5</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Тип использования
                </label>
                <select
                  v-model="formData.usage_type"
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="security">Безопасность</option>
                  <option value="general">Общее</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Страна
              </label>
              <input 
                v-model="formData.country"
                type="text"
                placeholder="US, RU, etc."
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div v-if="formError" class="p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded">
              {{ formError }}
            </div>
          </div>

          <div class="flex gap-3 mt-6">
            <button
              @click="submitForm"
              :disabled="isSubmitting"
              class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
            >
              {{ isSubmitting ? '⏳ Сохранение...' : 'Сохранить' }}
            </button>
            <button
              @click="closeForm"
              class="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              Отмена
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

const proxies = computed(() => settingsStore.proxies)
const error = computed(() => settingsStore.error)
const loading = computed(() => settingsStore.loading)
const isTesting = ref(false)
const isTestingProxy = ref(null)
const showAddForm = ref(false)
const editingProxy = ref(null)
const isSubmitting = ref(false)
const formError = ref(null)

const stats = computed(() => ({
  total: proxies.value.length,
  active: proxies.value.filter(p => p.is_active).length,
  working: proxies.value.filter(p => p.is_working === true).length,
}))

const formData = ref({
  name: '',
  description: '',
  host: '',
  port: 8080,
  username: '',
  password: '',
  protocol: 'http',
  usage_type: 'security',
  country: '',
})

const loadProxies = async () => {
  await settingsStore.loadProxies()
}

const testProxy = async (proxyId) => {
  isTesting.value = true
  isTestingProxy.value = proxyId
  try {
    const result = await settingsStore.testProxy(proxyId)
    if (result) {
      alert(result.is_working ? '✅ Прокси работает!' : `❌ Прокси не работает: ${result.error}`)
      await loadProxies()
    }
  } finally {
    isTesting.value = false
    isTestingProxy.value = null
  }
}

const editProxy = (proxy) => {
  editingProxy.value = proxy
  formData.value = {
    name: proxy.name,
    description: proxy.description || '',
    host: proxy.host,
    port: proxy.port,
    username: proxy.username || '',
    password: proxy.password || '',
    protocol: proxy.protocol,
    usage_type: proxy.usage_type,
    country: proxy.country || '',
  }
  showAddForm.value = true
}

const submitForm = async () => {
  isSubmitting.value = true
  formError.value = null
  
  try {
    if (editingProxy.value) {
      await settingsStore.updateProxy(editingProxy.value.id, formData.value)
    } else {
      await settingsStore.addProxy(formData.value)
    }
    await loadProxies()
    closeForm()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    isSubmitting.value = false
  }
}

const closeForm = () => {
  showAddForm.value = false
  editingProxy.value = null
  formData.value = {
    name: '',
    description: '',
    host: '',
    port: 8080,
    username: '',
    password: '',
    protocol: 'http',
    usage_type: 'security',
    country: '',
  }
  formError.value = null
}

const getUsageTypeLabel = (type) => {
  const labels = {
    security: '🔒 Безопасность',
    general: '🌐 Общее',
  }
  return labels[type] || type
}

onMounted(() => {
  loadProxies()
})
</script>
