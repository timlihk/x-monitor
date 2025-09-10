import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const termsApi = {
  getAll: () => api.get('/api/terms'),
  create: (term) => api.post('/api/terms', term),
  update: (id, term) => api.put(`/api/terms/${id}`, term),
  delete: (id) => api.delete(`/api/terms/${id}`),
}

export const resultsApi = {
  getAll: () => api.get('/api/results'),
  getById: (id) => api.get(`/api/results/${id}`),
}

export const runApi = {
  manual: (request) => api.post('/api/run', request),
}

export default api