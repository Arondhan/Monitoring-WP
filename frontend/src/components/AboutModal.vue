<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <!-- Background backdrop -->
    <div 
      class="fixed inset-0 bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-80 transition-opacity"
      @click="$emit('update:modelValue', false)"
    ></div>

    <!-- Modal panel -->
    <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
      <div 
        class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-800 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl"
        @click.stop
      >
        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 px-4 pb-4 pt-5 sm:p-6 sm:pb-4 border-b dark:border-gray-700">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <h3 class="text-xl font-bold text-gray-900 dark:text-white" id="modal-title">
                О проекте
              </h3>
            </div>
            <button
              @click="$emit('update:modelValue', false)"
              class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="px-4 py-5 sm:p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          <!-- Что это -->
          <div>
            <h4 class="font-semibold text-gray-900 dark:text-white flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Что это такое?
            </h4>
            <p class="mt-2 text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
              <strong>Uptimer</strong> — это система мониторинга, которая автоматически проверяет доступность ваших веб-сайтов. 
              Представьте, что у вас есть несколько сайтов, и вы хотите знать, если какой-то из них перестанет работать. 
              Этот сервис каждые несколько минут «стучится» на ваши сайты и проверяет, отвечают ли они.
            </p>
          </div>

          <!-- Как работает -->
          <div>
            <h4 class="font-semibold text-gray-900 dark:text-white flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              Как это работает?
            </h4>
            <ul class="mt-2 text-gray-600 dark:text-gray-300 text-sm space-y-1">
              <li class="flex items-start">
                <span class="text-primary-600 mr-2">•</span>
                <span>Вы добавляете адрес сайта (например, https://mysite.com)</span>
              </li>
              <li class="flex items-start">
                <span class="text-primary-600 mr-2">•</span>
                <span>Система каждые N минут проверяет, доступен ли сайт</span>
              </li>
              <li class="flex items-start">
                <span class="text-primary-600 mr-2">•</span>
                <span>Измеряет скорость ответа (время загрузки)</span>
              </li>
              <li class="flex items-start">
                <span class="text-primary-600 mr-2">•</span>
                <span>Проверяет SSL-сертификат (замочек в браузере)</span>
              </li>
              <li class="flex items-start">
                <span class="text-primary-600 mr-2">•</span>
                <span>Сохраняет историю всех проверок</span>
              </li>
            </ul>
          </div>

          <!-- Статусы -->
          <div>
            <h4 class="font-semibold text-gray-900 dark:text-white flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Что означают статусы?
            </h4>
            <div class="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              <div class="flex items-center">
                <span class="w-3 h-3 rounded-full bg-status-up mr-2"></span>
                <span class="text-gray-600 dark:text-gray-300"><strong>UP</strong> — сайт работает нормально</span>
              </div>
              <div class="flex items-center">
                <span class="w-3 h-3 rounded-full bg-status-slow mr-2"></span>
                <span class="text-gray-600 dark:text-gray-300"><strong>SLOW</strong> — сайт работает, но медленно</span>
              </div>
              <div class="flex items-center">
                <span class="w-3 h-3 rounded-full bg-status-down mr-2"></span>
                <span class="text-gray-600 dark:text-gray-300"><strong>DOWN</strong> — сайт не доступен</span>
              </div>
              <div class="flex items-center">
                <span class="w-3 h-3 rounded-full bg-status-sslError mr-2"></span>
                <span class="text-gray-600 dark:text-gray-300"><strong>SSL</strong> — проблема с сертификатом</span>
              </div>
              <div class="flex items-center">
                <span class="w-3 h-3 rounded-full bg-status-pending mr-2"></span>
                <span class="text-gray-600 dark:text-gray-300"><strong>PENDING</strong> — ещё не проверен</span>
              </div>
            </div>
          </div>

          <!-- Технологии -->
          <div>
            <h4 class="font-semibold text-gray-900 dark:text-white flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
              </svg>
              На чём сделано?
            </h4>
            <div class="mt-2 text-gray-600 dark:text-gray-300 text-sm">
              <p class="mb-2"><strong>Backend (серверная часть):</strong></p>
              <ul class="ml-4 space-y-1 text-xs">
                <li>• <span class="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded">Python</span> + <span class="bg-green-100 dark:bg-green-900 px-2 py-0.5 rounded">FastAPI</span> — быстрый веб-фреймворк</li>
                <li>• <span class="bg-blue-100 dark:bg-blue-900 px-2 py-0.5 rounded">PostgreSQL</span> — база данных для хранения информации</li>
                <li>• <span class="bg-orange-100 dark:bg-orange-900 px-2 py-0.5 rounded">Redis</span> + <span class="bg-yellow-100 dark:bg-yellow-900 px-2 py-0.5 rounded">Celery</span> — фоновые задачи для проверок</li>
              </ul>
              <p class="mt-3 mb-2"><strong>Frontend (то, что вы видите):</strong></p>
              <ul class="ml-4 space-y-1 text-xs">
                <li>• <span class="bg-green-100 dark:bg-green-900 px-2 py-0.5 rounded">Vue 3</span> — современный JavaScript-фреймворк</li>
                <li>• <span class="bg-purple-100 dark:bg-purple-900 px-2 py-0.5 rounded">TailwindCSS</span> — красивые стили</li>
                <li>• <span class="bg-red-100 dark:bg-red-900 px-2 py-0.5 rounded">Chart.js</span> — графики и статистика</li>
              </ul>
            </div>
          </div>

          <!-- Зачем это нужно -->
          <div class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
            <h4 class="font-semibold text-gray-900 dark:text-white flex items-center">
              <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
              </svg>
              Зачем это нужно?
            </h4>
            <p class="mt-2 text-gray-600 dark:text-gray-300 text-sm">
                Вся суть в том, что PBN-сетка работает и дает результат только тогда, когда сайты доступны. 
                Дешевые хостинги периодически падают, базы данных отваливаются, и если вовремя этого не заметить — вы просто теряете ссылочный вес и сливаете бюджет впустую.
                Uptimer забирает эту головную боль на себя. Вы один раз добавляете в него свои сайты, и система 24/7 следит за их состоянием.
                Как только любой донор ложится или выдает ошибку, вы сразу получаете уведомление. 
                Больше никаких долгих ручных проверок: вы моментально узнаете о проблеме, быстро возвращаете сайт в строй
            </p>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
          <button
            type="button"
            @click="$emit('update:modelValue', false)"
            class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 sm:ml-3 sm:w-auto"
          >
            Понятно
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
})

defineEmits(['update:modelValue'])
</script>
