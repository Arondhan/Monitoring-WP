/**
 * Pinia store для настроек приложения
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from './api'

export const useSettingsStore = defineStore('settings', () => {
  // State
  const proxies = ref([])
  const settings = ref({})
  const dashboard = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const activeProxies = computed(() => proxies.value.filter(p => p.is_active))
  const workingProxies = computed(() => proxies.value.filter(p => p.is_working === true))

  // Actions
  async function loadProxies(activeOnly = false, usageType = null) {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      if (activeOnly) params.append('active_only', 'true')
      if (usageType) params.append('usage_type', usageType)
      
      const response = await api.get(`/settings/proxies?${params}`)
      proxies.value = response.data.items
      return response.data
    } catch (err) {
      error.value = 'Ошибка загрузки прокси'
      console.error(err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function addProxy(proxyData) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/settings/proxies', proxyData)
      proxies.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка добавления прокси'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProxy(proxyId, proxyData) {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/settings/proxies/${proxyId}`, proxyData)
      const index = proxies.value.findIndex(p => p.id === proxyId)
      if (index !== -1) {
        proxies.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Ошибка обновления прокси'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteProxy(proxyId) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/settings/proxies/${proxyId}`)
      proxies.value = proxies.value.filter(p => p.id !== proxyId)
    } catch (err) {
      error.value = 'Ошибка удаления прокси'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function testProxy(proxyId, testUrl = 'https://www.google.com', timeout = 10) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/settings/proxies/${proxyId}/test`, {
        test_url: testUrl,
        timeout: timeout
      })
      return response.data
    } catch (err) {
      error.value = 'Ошибка тестирования прокси'
      console.error(err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function loadDashboard() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/settings/dashboard')
      dashboard.value = response.data
      return response.data
    } catch (err) {
      error.value = 'Ошибка загрузки дашборда настроек'
      console.error(err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function loadSecuritySettings() {
    try {
      const response = await api.get('/settings/security')
      return response.data
    } catch (err) {
      console.error(err)
      return null
    }
  }

  async function updateSecuritySettings(settingsData) {
    try {
      const response = await api.put('/settings/security', settingsData)
      return response.data
    } catch (err) {
      error.value = 'Ошибка обновления настроек безопасности'
      console.error(err)
      throw err
    }
  }

  async function getSettingValue(key, defaultValue = null) {
    try {
      const response = await api.get(`/settings/app/${key}`)
      return response.data.value
    } catch (err) {
      return defaultValue
    }
  }

  async function setSettingValue(key, value, valueType = 'string', description = null) {
    try {
      const params = new URLSearchParams()
      params.append('value', value)
      params.append('value_type', valueType)
      if (description) params.append('description', description)
      
      const response = await api.put(`/settings/app/${key}?${params}`)
      return response.data
    } catch (err) {
      error.value = 'Ошибка сохранения настройки'
      console.error(err)
      throw err
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    proxies,
    settings,
    dashboard,
    loading,
    error,
    // Getters
    activeProxies,
    workingProxies,
    // Actions
    loadProxies,
    addProxy,
    updateProxy,
    deleteProxy,
    testProxy,
    loadDashboard,
    loadSecuritySettings,
    updateSecuritySettings,
    getSettingValue,
    setSettingValue,
    clearError,
  }
})
