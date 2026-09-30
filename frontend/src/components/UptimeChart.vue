<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Время ответа и аптайм</h2>

      <!-- Period Selector -->
      <div class="flex gap-2">
        <button
          v-for="period in periods"
          :key="period.value"
          @click="$emit('update:period', period.value)"
          class="px-3 py-1.5 text-sm rounded-md transition-colors"
          :class="modelValue === period.value
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="h-80">
      <Line
        v-if="chartData && chartOptions"
        :data="chartData"
        :options="chartOptions"
      />
      <div v-else class="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
        Нет данных
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  checks: {
    type: Array,
    default: () => [],
  },
  period: {
    type: String,
    default: '24h',
  },
})

const emit = defineEmits(['update:period'])

const periods = [
  { value: '1h', label: '1Ч' },
  { value: '6h', label: '6Ч' },
  { value: '24h', label: '24Ч' },
  { value: '7d', label: '7Д' },
  { value: '30d', label: '30Д' },
]

// Форматирование данных для графика
const chartData = computed(() => {
  if (!props.checks || props.checks.length === 0) {
    return null
  }

  const labels = props.checks.map(check => {
    const date = new Date(check.timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  const responseTimeData = props.checks.map(check => check.response_time_ms)
  
  // Данные для фона (uptime/down time)
  const backgroundColor = props.checks.map(check => {
    if (check.status === 'UP') return 'rgba(34, 197, 94, 0.1)'
    if (check.status === 'SLOW') return 'rgba(234, 179, 8, 0.1)'
    return 'rgba(239, 68, 68, 0.1)'
  })

  const borderColor = props.checks.map(check => {
    if (check.status === 'UP') return 'rgb(34, 197, 94)'
    if (check.status === 'SLOW') return 'rgb(234, 179, 8)'
    return 'rgb(239, 68, 68)'
  })

  return {
    labels,
    datasets: [
      {
        label: 'Время ответа (мс)',
        data: responseTimeData,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: (context) => {
          const index = context.dataIndex
          const check = props.checks[index]
          if (check.status === 'DOWN' || check.status === 'SSL_ERROR') return 6
          if (check.status === 'SLOW') return 4
          return 3
        },
        pointBackgroundColor: (context) => {
          const index = context.dataIndex
          const check = props.checks[index]
          if (check.status === 'DOWN' || check.status === 'SSL_ERROR') return 'rgb(239, 68, 68)'
          if (check.status === 'SLOW') return 'rgb(234, 179, 8)'
          return 'rgb(34, 197, 94)'
        },
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const check = props.checks[context.dataIndex]
          return [
            `Время: ${check.response_time_ms || '—'} мс`,
            `Статус: ${check.status}`,
            `Код: ${check.status_code || '—'}`,
          ]
        },
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Время ответа (мс)',
      },
    },
    x: {
      ticks: {
        maxTicksLimit: 10,
      },
    },
  },
}
</script>
