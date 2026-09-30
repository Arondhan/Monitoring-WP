<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
    <h2 class="text-2xl font-bold mb-4 text-gray-800 dark:text-white">
      🔒 Белый список ссылок
    </h2>
    <p class="text-gray-600 dark:text-gray-400 mb-6">
      Домены в белом списке не будут помечаться как подозрительные при проверке безопасности
    </p>

    <div v-if="error" class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded">
      {{ error }}
    </div>

    <!-- Статистика -->
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ whitelist.length }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Доменов в списке</div>
      </div>
      <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
        <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ activeCount }}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Активных</div>
      </div>
    </div>

    <!-- Форма добавления -->
    <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
      <h3 class="font-medium text-gray-900 dark:text-white mb-3">Добавить домен</h3>
      <div class="flex gap-3">
        <input
          v-model="newDomain"
          @keyup.enter="addDomain"
          type="text"
          placeholder="example.com"
          class="flex-1 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
        <button
          @click="addDomain"
          :disabled="!newDomain.trim()"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition"
        >
          Добавить
        </button>
      </div>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
        💡 Поддерживаются поддомены: example.com, *.example.com, sub.example.com
      </p>
    </div>

    <!-- Список доменов -->
    <div class="space-y-2">
      <div
        v-for="(domain, index) in whitelist"
        :key="index"
        class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-750"
      >
        <div class="flex items-center gap-3">
          <span
            :class="domain.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'"
            class="px-2 py-1 rounded text-xs"
          >
            {{ domain.is_active ? '✓ Активен' : '⏸️ Отключен' }}
          </span>
          <code class="text-gray-900 dark:text-white">{{ domain.domain }}</code>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="toggleDomain(index)"
            class="px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-900/20 rounded"
          >
            {{ domain.is_active ? 'Отключить' : 'Включить' }}
          </button>
          <button
            @click="removeDomain(index)"
            class="px-2 py-1 text-xs text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded"
          >
            ✕
          </button>
        </div>
      </div>

      <div v-if="whitelist.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8">
        Белый список пуст. Добавьте первый домен!
      </div>
    </div>

    <!-- Кнопка сохранения -->
    <div class="mt-6 flex justify-end gap-3">
      <button
        @click="resetToDefaults"
        class="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
      >
        Сбросить к стандартным
      </button>
      <button
        @click="saveWhitelist"
        :disabled="isSaving"
        class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition"
      >
        {{ isSaving ? '⏳ Сохранение...' : '💾 Сохранить' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

const whitelist = ref([])
const newDomain = ref('')
const isSaving = ref(false)
const error = ref(null)

const activeCount = computed(() => whitelist.value.filter(d => d.is_active).length)

// Стандартные домены по умолчанию
const defaultWhitelist = [
  { domain: 'example.com', is_active: true },
  { domain: '*.example.com', is_active: true },
]

const loadWhitelist = async () => {
  try {
    const saved = await settingsStore.getSettingValue('security.whitelist', null)
    if (saved && Array.isArray(saved)) {
      whitelist.value = saved
    } else {
      whitelist.value = [...defaultWhitelist]
    }
  } catch (err) {
    error.value = 'Ошибка загрузки белого списка'
    console.error(err)
  }
}

const addDomain = () => {
  const domain = newDomain.value.trim()
  if (!domain) return

  // Проверка формата домена
  const domainRegex = /^(\*\.)?[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$/
  if (!domainRegex.test(domain)) {
    error.value = 'Неверный формат домена'
    return
  }

  // Проверка на дубликат
  if (whitelist.value.some(d => d.domain === domain)) {
    error.value = 'Этот домен уже в списке'
    return
  }

  whitelist.value.push({ domain, is_active: true })
  newDomain.value = ''
  error.value = null
}

const removeDomain = (index) => {
  whitelist.value.splice(index, 1)
}

const toggleDomain = (index) => {
  whitelist.value[index].is_active = !whitelist.value[index].is_active
}

const saveWhitelist = async () => {
  isSaving.value = true
  error.value = null
  try {
    await settingsStore.setSettingValue(
      'security.whitelist',
      JSON.stringify(whitelist.value),
      'json',
      'Белый список доменов для проверки безопасности'
    )
    alert('✅ Белый список сохранен!')
  } catch (err) {
    error.value = 'Ошибка сохранения белого списка'
    console.error(err)
  } finally {
    isSaving.value = false
  }
}

const resetToDefaults = () => {
  if (confirm('Сбросить к стандартным доменам?')) {
    whitelist.value = [...defaultWhitelist]
  }
}

onMounted(() => {
  loadWhitelist()
})
</script>
