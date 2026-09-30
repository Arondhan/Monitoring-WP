<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div class="flex items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Панель мониторинга</h1>
        </div>
        <button
          @click="refreshData"
          :disabled="domainsStore.loading"
          class="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md disabled:opacity-50"
          title="Обновить данные"
        >
          <svg class="w-5 h-5" :class="{'animate-spin': domainsStore.loading}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>
      <button
        @click="showAddModal = true"
        class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        Добавить домен
      </button>
    </div>

    <!-- Summary Cards -->
    <SummaryCards
      :total-domains="domainsStore.total"
      :status-counts="domainsStore.statusCounts"
      :overall-uptime="domainsStore.overallUptime"
      class="mb-6"
    />

    <!-- WordPress Summary Cards -->
    <WordPressSummaryCards
      v-if="domainsStore.hasWordPressDomains"
      :stats="domainsStore.computedWordPressStats"
      class="mb-6"
    />

    <!-- Filter Bar -->
    <div class="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <FilterBar
        :active-filter="activeFilter"
        :sort-by="sortBy"
        :sort-order="sortOrder"
        :status-counts="domainsStore.statusCounts"
        :wordpress-filter="domainsStore.wordpressFilter"
        :wordpress-stats="domainsStore.computedWordPressStats"
        :show-wordpress-filter="domainsStore.hasWordPressDomains"
        @filter="handleFilter"
        @sort="handleSort"
        @sort-order="handleSortOrder"
        @wordpress-filter="handleWordPressFilter"
      />
    </div>

    <!-- Loading State -->
    <div v-if="domainsStore.loading" class="mt-6 flex justify-center">
      <svg class="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Error State -->
    <div v-else-if="domainsStore.error" class="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
      <p class="text-red-800 dark:text-red-400">{{ domainsStore.error }}</p>
      <button
        @click="refreshData"
        class="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 font-medium"
      >
        Попробовать снова
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="domainsStore.domains.length === 0" class="mt-6 text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">Нет доменов</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Начните с добавления домена для мониторинга.</p>
      <button
        @click="showAddModal = true"
        class="mt-4 inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
      >
        Добавить домен
      </button>
    </div>

    <!-- Domains Grid -->
    <div v-else class="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <DomainCard
        v-for="domain in domainsStore.filteredDomains"
        :key="domain.id"
        :domain="domain"
        :is-checking="checkingDomains.has(domain.id)"
        @click="navigateToDomain(domain.id)"
        @edit="openEditModal(domain)"
        @check-wordpress="handleCheckWordPress"
      />
    </div>

    <!-- Add/Edit Domain Modal -->
    <AddDomainModal
      v-model="showAddModal"
      :is-edit="isEditModal"
      :domain="selectedDomain"
      @submit="handleSaveDomain"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDomainsStore } from '../stores/domains'
import DomainCard from '../components/DomainCard.vue'
import FilterBar from '../components/FilterBar.vue'
import SummaryCards from '../components/SummaryCards.vue'
import WordPressSummaryCards from '../components/WordPressSummaryCards.vue'
import AddDomainModal from '../components/AddDomainModal.vue'

const router = useRouter()
const domainsStore = useDomainsStore()

const showAddModal = ref(false)
const isEditModal = ref(false)
const selectedDomain = ref(null)
const activeFilter = ref('')
const sortBy = ref('created_at')
const sortOrder = ref('desc')
const checkingDomains = ref(new Set())

onMounted(async () => {
  await domainsStore.fetchDomains()
})

function openEditModal(domain) {
  selectedDomain.value = domain
  isEditModal.value = true
  showAddModal.value = true
}

function handleFilter(status) {
  activeFilter.value = status
  domainsStore.setFilter('status', status || null)
}

function handleSort(field) {
  sortBy.value = field
  domainsStore.setFilter('sortBy', field)
}

function handleSortOrder(order) {
  sortOrder.value = order
  domainsStore.setFilter('sortOrder', order)
}

async function handleSaveDomain(domainData) {
  if (isEditModal.value && selectedDomain.value) {
    await domainsStore.updateDomain(selectedDomain.value.id, domainData)
  } else {
    await domainsStore.addDomain(domainData)
  }
  await domainsStore.fetchDomains()
  showAddModal.value = false
  selectedDomain.value = null
  isEditModal.value = false
}

function navigateToDomain(domainId) {
  router.push(`/domain/${domainId}`)
}

async function refreshData() {
  await domainsStore.fetchDomains()
}

async function handleWordPressFilter(filter) {
  domainsStore.setWordPressFilter(filter)
}

async function handleCheckWordPress(domainId) {
  checkingDomains.value.add(domainId)
  try {
    await domainsStore.checkWordPress(domainId)
    setTimeout(() => {
      domainsStore.fetchDomains()
    }, 2000)
  } catch (error) {
    console.error('Failed to check WordPress:', error)
  } finally {
    checkingDomains.value.delete(domainId)
  }
}
</script>
