<template>
  <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div class="text-sm text-gray-500 dark:text-gray-400">Всего WordPress</div>
      <div class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
        {{ stats.total }}
      </div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-green-200 dark:border-green-800 p-4">
      <div class="text-sm text-gray-500 dark:text-gray-400">🟢 Свежие</div>
      <div class="mt-1 text-2xl font-bold text-green-600 dark:text-green-400">
        {{ stats.fresh }}
      </div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">&lt; 7 дней</div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-yellow-200 dark:border-yellow-800 p-4">
      <div class="text-sm text-gray-500 dark:text-gray-400">🟡 Внимание</div>
      <div class="mt-1 text-2xl font-bold text-yellow-600 dark:text-yellow-400">
        {{ stats.warning }}
      </div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">7-30 дней</div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-red-200 dark:border-red-800 p-4">
      <div class="text-sm text-gray-500 dark:text-gray-400">🔴 Устаревшие</div>
      <div class="mt-1 text-2xl font-bold text-red-600 dark:text-red-400">
        {{ stats.stale }}
      </div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">&gt; 30 дней</div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div class="text-sm text-gray-500 dark:text-gray-400">Без постов</div>
      <div class="mt-1 text-2xl font-bold text-gray-600 dark:text-gray-400">
        {{ stats.no_posts }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    required: true,
  },
})
</script>
