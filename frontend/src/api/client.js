const BASE = (import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000').replace(/\/$/, '')

export function getToken() {
  return localStorage.getItem('token') || ''
}

export function setSession(token, user) {
  if (token) localStorage.setItem('token', token)
  if (user) localStorage.setItem('user', JSON.stringify(user))
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    return null
  }
}

export function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (auth && token) headers.Authorization = `Token ${token}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  let data = null
  const text = await res.text()
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = { detail: text.slice(0, 300) }
    }
  }

  if (!res.ok) {
    const message =
      data?.detail ||
      (data && typeof data === 'object'
        ? Object.entries(data)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join(' · ')
        : `Request failed (${res.status})`)
    throw new Error(message)
  }
  return data
}

export const api = {
  // auth
  register: (payload) => request('/api/auth/register/', { method: 'POST', body: payload, auth: false }),
  login: (payload) => request('/api/auth/login/', { method: 'POST', body: payload, auth: false }),
  logout: () => request('/api/auth/logout/', { method: 'POST' }),
  me: () => request('/api/auth/me/'),
  updateMe: (payload) => request('/api/auth/me/', { method: 'PATCH', body: payload }),

  // admin
  triggers: () => request('/api/triggers/'),
  createTrigger: (payload) => request('/api/triggers/', { method: 'POST', body: payload }),
  updateTrigger: (id, payload) => request(`/api/triggers/${id}/`, { method: 'PATCH', body: payload }),
  deleteTrigger: (id) => request(`/api/triggers/${id}/`, { method: 'DELETE' }),
  fireTriggerById: (id) => request(`/api/triggers/${id}/fire/`, { method: 'POST' }),

  createTemplate: (payload) => request('/api/templates/', { method: 'POST', body: payload }),
  updateTemplate: (id, payload) => request(`/api/templates/${id}/`, { method: 'PATCH', body: payload }),
  deleteTemplate: (id) => request(`/api/templates/${id}/`, { method: 'DELETE' }),
  toggleTemplate: (id, isEnabled) =>
    request(`/api/templates/${id}/toggle/`, { method: 'POST', body: { is_enabled: isEnabled } }),
  testSend: (id, payload) => request(`/api/templates/${id}/test-send/`, { method: 'POST', body: payload }),

  logs: () => request('/api/logs/'),

  // user site
  subscribePush: (playerId) => request('/api/push/subscribe/', { method: 'POST', body: { player_id: playerId } }),
  fireTrigger: (code, variables) =>
    request(`/api/triggers-fire/${code}/`, { method: 'POST', body: { variables: variables || {} } }),
}

export const CHANNELS = [
  { key: 'whatsapp', label: 'WhatsApp' },
  { key: 'email', label: 'Email' },
  { key: 'webpush', label: 'Web Push' },
]
