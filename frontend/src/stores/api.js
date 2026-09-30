import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const domainsApi = {
  // Получить список доменов
  async getDomains(params = {}) {
    const response = await api.get('/domains', { params })
    return response.data
  },

  // Получить домен по ID
  async getDomain(id) {
    const response = await api.get(`/domains/${id}`)
    return response.data
  },

  // Создать домен
  async createDomain(data) {
    const response = await api.post('/domains', data)
    return response.data
  },

  // Обновить домен
  async updateDomain(id, data) {
    const response = await api.put(`/domains/${id}`, data)
    return response.data
  },

  // Удалить домен
  async deleteDomain(id) {
    await api.delete(`/domains/${id}`)
  },

  // Получить историю проверок
  async getChecks(id, params = {}) {
    const response = await api.get(`/domains/${id}/checks`, { params })
    return response.data
  },

  // Получить инциденты
  async getIncidents(id, params = {}) {
    const response = await api.get(`/domains/${id}/incidents`, { params })
    return response.data
  },

  // Получить статистику
  async getStats(id) {
    const response = await api.get(`/domains/${id}/stats`)
    return response.data
  },

  // Запустить проверку домена
  async triggerCheck(id) {
    const response = await api.post(`/domains/${id}/check`)
    return response.data
  },

  // Запустить проверку WordPress (мониторинг)
  async checkWordPress(id) {
    const response = await api.post(`/domains/${id}/wordpress/check`)
    return response.data
  },

  // Получить статистику WordPress
  async getWordPressStats() {
    const response = await api.get('/domains/wordpress/stats')
    return response.data
  },

  // Получить контент страницы (Meta + Заголовки)
  async getDomainContent(id) {
    const response = await api.get(`/domains/${id}/content`)
    return response.data
  },
}

export const dashboardApi = {
  async getSummary() {
    const response = await api.get('/dashboard')
    return response.data
  },
}

export default api
