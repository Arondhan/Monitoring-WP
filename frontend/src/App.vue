<template>
  <div id="app" class="min-h-screen">
    <nav class="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-2">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span class="text-xl font-bold text-gray-900 dark:text-white">Uptimer</span>
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link
              to="/settings"
              class="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm flex items-center space-x-1"
            >
              <span>⚙️ Настройки</span>
            </router-link>
            <button
              @click="showAboutModal = true"
              class="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm flex items-center space-x-1"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>О проекте</span>
            </button>
            <button
              @click="toggleTheme"
              class="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              :title="isDark ? 'Светлая тема' : 'Тёмная тема'"
            >
              <svg v-if="isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
              </svg>
            </button>
            <a href="http://localhost:8000/docs" target="_blank" class="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white text-sm hidden sm:inline">
              API Документация
            </a>
          </div>
        </div>
      </div>
    </nav>

    <main class="py-6">
      <router-view />
    </main>

    <!-- About Modal -->
    <AboutModal
      v-model="showAboutModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useThemeStore } from './stores/theme'
import AboutModal from './components/AboutModal.vue'

const themeStore = useThemeStore()
const showAboutModal = ref(false)

const isDark = ref(false)

onMounted(() => {
  themeStore.init()
  isDark.value = themeStore.isDark
})

function toggleTheme() {
  themeStore.toggle()
  isDark.value = themeStore.isDark
}
</script>
