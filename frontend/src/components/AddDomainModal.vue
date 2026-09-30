<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 overflow-y-auto">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" @click="$emit('update:modelValue', false)"></div>

    <!-- Modal -->
    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6 transform transition-all">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">{{ isEdit ? 'Редактировать домен' : 'Добавить новый домен' }}</h3>
          <button @click="$emit('update:modelValue', false)" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <!-- Domain Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Название
              </label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                required
                placeholder="Мой сайт"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <!-- URL -->
            <div>
              <label for="url" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                URL сайта
              </label>
              <input
                id="url"
                v-model="formData.url"
                type="url"
                required
                placeholder="https://example.com"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <!-- Check Interval -->
            <div>
              <label for="interval" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Интервал проверки
              </label>

              <!-- Quick presets -->
              <div class="flex flex-wrap gap-2 mb-2">
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 60"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  1 мин
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 300"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  5 мин
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 900"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  15 мин
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 1800"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  30 мин
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 3600"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  1 час
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 43200"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  12 часов
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 86400"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  1 день
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 172800"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  2 дня
                </button>
                <button
                  type="button"
                  @click="formData.check_interval_seconds = 604800"
                  class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md transition-colors"
                >
                  1 неделя
                </button>
              </div>

              <input
                id="interval"
                v-model.number="formData.check_interval_seconds"
                type="number"
                min="30"
                max="604800"
                step="60"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              />
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Интервал проверки (от 30 секунд до 7 дней)</p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p class="text-sm text-red-800 dark:text-red-400">{{ error }}</p>
          </div>

          <!-- Actions -->
          <div class="mt-6 flex gap-3">
            <button
              type="button"
              @click="$emit('update:modelValue', false)"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              Отмена
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ loading ? 'Добавление...' : 'Добавить домен' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  isEdit: Boolean,
  domain: Object,
})

const emit = defineEmits(['update:modelValue', 'submit'])

const loading = ref(false)
const error = ref(null)

const formData = reactive({
  name: '',
  url: '',
  check_interval_seconds: 60,
})

// Reset form when modal opens
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.isEdit && props.domain) {
      formData.name = props.domain.name
      formData.url = props.domain.url
      formData.check_interval_seconds = props.domain.check_interval_seconds
    } else {
      formData.name = ''
      formData.url = ''
      formData.check_interval_seconds = 60
    }
    error.value = null
  }
})

async function handleSubmit() {
  loading.value = true
  error.value = null

  try {
    await emit('submit', { ...formData })
    emit('update:modelValue', false)
  } catch (err) {
    error.value = err.message || 'Не удалось сохранить домен'
  } finally {
    loading.value = false
  }
}
</script>
