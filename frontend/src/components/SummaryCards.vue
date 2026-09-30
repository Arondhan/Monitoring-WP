<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <!-- Total Domains -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div class="flex items-center">
        <div class="flex-shrink-0 p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
          <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
          </svg>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Всего доменов</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ totalDomains }}</p>
        </div>
      </div>
    </div>

    <!-- Healthy -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div class="flex items-center">
        <div class="flex-shrink-0 p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
          <svg class="w-6 h-6 text-status-up" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Исправны</p>
          <p class="text-2xl font-bold text-status-up">{{ healthyCount }}</p>
        </div>
      </div>
    </div>

    <!-- Issues -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div class="flex items-center">
        <div class="flex-shrink-0 p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
          <svg class="w-6 h-6 text-status-down" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Проблемы</p>
          <p class="text-2xl font-bold text-status-down">{{ issuesCount }}</p>
        </div>
      </div>
    </div>

    <!-- Overall Uptime -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div class="flex items-center">
        <div class="flex-shrink-0 p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <div class="ml-4">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Аптайм (24ч)</p>
          <p class="text-2xl font-bold" :class="uptimeColor">{{ overallUptime }}%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  totalDomains: {
    type: Number,
    default: 0,
  },
  statusCounts: {
    type: Object,
    default: () => ({ up: 0, down: 0, slow: 0, sslError: 0, pending: 0 }),
  },
  overallUptime: {
    type: Number,
    default: 100,
  },
})

const healthyCount = computed(() => props.statusCounts.up)
const issuesCount = computed(() => {
  return props.statusCounts.down + props.statusCounts.sslError
})

const uptimeColor = computed(() => {
  if (props.overallUptime >= 99) return 'text-status-up'
  if (props.overallUptime >= 95) return 'text-status-slow'
  return 'text-status-down'
})
</script>
