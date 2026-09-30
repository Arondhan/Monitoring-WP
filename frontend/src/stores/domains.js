import { defineStore } from 'pinia'
import { domainsApi, dashboardApi } from './api'

export const useDomainsStore = defineStore('domains', {
  state: () => ({
    domains: [],
    total: 0,
    loading: false,
    error: null,
    filters: {
      status: null,
      sortBy: 'created_at',
      sortOrder: 'desc',
    },
    // WordPress-фильтры (мониторинг)
    wordpressFilter: '',  // '', 'wordpress', 'fresh', 'warning', 'stale'
    wordpressStats: {
      total: 0,
      fresh: 0,
      warning: 0,
      stale: 0,
      no_posts: 0,
    },
  }),

  getters: {
    filteredDomains: (state) => {
      let result = [...state.domains]

      // WordPress фильтр
      if (state.wordpressFilter === 'wordpress') {
        result = result.filter(d => d.is_wordpress)
      } else if (state.wordpressFilter === 'fresh') {
        result = result.filter(d => d.wordpress_post_status === 'fresh')
      } else if (state.wordpressFilter === 'warning') {
        result = result.filter(d => d.wordpress_post_status === 'warning')
      } else if (state.wordpressFilter === 'stale') {
        result = result.filter(d => d.wordpress_post_status === 'stale')
      }

      // Сортировка
      const { sortBy, sortOrder } = state.filters
      result.sort((a, b) => {
        let aVal = a[sortBy]
        let bVal = b[sortBy]

        if (sortBy === 'status') {
          const statusOrder = { DOWN: 0, SSL_ERROR: 1, SLOW: 2, PENDING: 3, UP: 4 }
          aVal = statusOrder[a.last_status] ?? 5
          bVal = statusOrder[b.last_status] ?? 5
        }

        if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
        if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
        return 0
      })

      return result
    },

    statusCounts: (state) => {
      return state.domains.reduce((acc, domain) => {
        const status = domain.last_status?.toLowerCase()
        if (status === 'up') acc.up++
        else if (status === 'down') acc.down++
        else if (status === 'slow') acc.slow++
        else if (status === 'ssl_error') acc.sslError++
        else if (status === 'pending') acc.pending++
        return acc
      }, { up: 0, down: 0, slow: 0, sslError: 0, pending: 0 })
    },

    overallUptime: (state) => {
      if (state.domains.length === 0) return 100
      const sum = state.domains.reduce((acc, d) => acc + (d.uptime_percentage_24h || 0), 0)
      return Math.round(sum / state.domains.length)
    },

    // WordPress статистика (вычисляется из данных доменов)
    computedWordPressStats: (state) => {
      const stats = { total: 0, fresh: 0, warning: 0, stale: 0, no_posts: 0 }

      state.domains.forEach(domain => {
        if (domain.is_wordpress) {
          stats.total++

          if (!domain.last_post_date) {
            stats.no_posts++
          } else if (domain.wordpress_post_status === 'fresh') {
            stats.fresh++
          } else if (domain.wordpress_post_status === 'warning') {
            stats.warning++
          } else if (domain.wordpress_post_status === 'stale') {
            stats.stale++
          }
        }
      })

      return stats
    },

    // Есть ли WordPress домены
    hasWordPressDomains: (state) => {
      return state.domains.some(d => d.is_wordpress)
    },
  },

  actions: {
    async fetchDomains() {
      this.loading = true
      this.error = null
      try {
        const params = {
          sort_by: this.filters.sortBy,
          sort_order: this.filters.sortOrder,
        }
        if (this.filters.status) {
          params.status = this.filters.status
        }
        const data = await domainsApi.getDomains(params)

        const newDomainsMap = new Map(data.items.map(d => [d.id, d]))

        for (const [id, newDomain] of newDomainsMap) {
          const existingDomain = this.domains.find(d => d.id === id)
          if (existingDomain) {
            Object.assign(existingDomain, newDomain)
          } else {
            this.domains.push(newDomain)
          }
        }

        this.domains = this.domains.filter(d => newDomainsMap.has(d.id))

        this.total = data.total
      } catch (err) {
        this.error = err.message
        console.error('Failed to fetch domains:', err)
      } finally {
        this.loading = false
      }
    },

    async addDomain(domainData) {
      return await domainsApi.createDomain(domainData)
    },

    async updateDomain(id, domainData) {
      return await domainsApi.updateDomain(id, domainData)
    },

    async removeDomain(id) {
      await domainsApi.deleteDomain(id)
      this.domains = this.domains.filter(d => d.id !== id)
    },

    setFilter(key, value) {
      this.filters[key] = value
      this.fetchDomains()
    },

    async refreshDomain(id) {
      try {
        const domain = await domainsApi.getDomain(id)
        const index = this.domains.findIndex(d => d.id === id)
        if (index !== -1) {
          this.domains[index] = domain
        }
      } catch (err) {
        console.error('Failed to refresh domain:', err)
      }
    },

    async checkWordPress(id) {
      this.loading = true
      this.error = null
      try {
        const result = await domainsApi.checkWordPress(id)
        const index = this.domains.findIndex(d => d.id === id)
        if (index !== -1) {
          this.domains[index] = { ...this.domains[index], ...result }
        }
        return result
      } catch (err) {
        this.error = err.message
        console.error('Failed to check WordPress:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    // Установить WordPress фильтр
    setWordPressFilter(filter) {
      this.wordpressFilter = filter
      this.fetchDomains()
    },

    // Загрузить статистику WordPress
    async fetchWordPressStats() {
      try {
        const stats = await domainsApi.getWordPressStats()
        this.wordpressStats = stats
      } catch (err) {
        console.error('Failed to fetch WordPress stats:', err)
      }
    },
  },
})

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    summary: null,
    loading: false,
  }),

  actions: {
    async fetchSummary() {
      this.loading = true
      try {
        this.summary = await dashboardApi.getSummary()
      } catch (err) {
        console.error('Failed to fetch dashboard summary:', err)
      } finally {
        this.loading = false
      }
    },
  },
})
