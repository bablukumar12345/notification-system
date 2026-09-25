import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'
import Toast from '../components/Toast.jsx'

export default function Login({ onAuth }) {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const data = await api.login(form)
      onAuth(data)
    } catch (err) {
      setError(
        err.message === 'Failed to fetch'
          ? 'Cannot reach the backend. Start the Django server and check VITE_API_BASE.'
          : err.message
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page auth-wrap">
      <div className="card">
        <h1>Sign in</h1>
        <p className="muted small">Signing in fires the Login trigger, so the notification arrives right away.</p>
        <Toast message={error} kind="bad" onClose={() => setError('')} />
        <form onSubmit={submit}>
          <div className="field">
            <label htmlFor="u">Username</label>
            <input id="u" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          </div>
          <div className="field">
            <label htmlFor="p">Password</label>
            <input id="p" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          </div>
          <button type="submit" disabled={busy} style={{ width: '100%' }}>
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <p className="small muted" style={{ marginTop: 14 }}>
          New here? <Link to="/register">Create account</Link>
        </p>
      </div>
    </div>
  )
}
