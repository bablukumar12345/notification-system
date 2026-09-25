import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'
import Toast from '../components/Toast.jsx'

export default function Register({ onAuth }) {
  const [form, setForm] = useState({ username: '', first_name: '', email: '', phone: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function set(key) {
    return (e) => setForm({ ...form, [key]: e.target.value })
  }

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const data = await api.register(form)
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
        <h1>Create account</h1>
        <p className="muted small">
          For WhatsApp tests, use the number you added to the Meta sandbox recipient list, with the country code and no
          plus sign. Example: 919876543210.
        </p>
        <Toast message={error} kind="bad" onClose={() => setError('')} />
        <form onSubmit={submit}>
          <div className="field">
            <label htmlFor="un">Username</label>
            <input id="un" value={form.username} onChange={set('username')} required />
          </div>
          <div className="field">
            <label htmlFor="fn">First name</label>
            <input id="fn" value={form.first_name} onChange={set('first_name')} />
          </div>
          <div className="field">
            <label htmlFor="em">Email</label>
            <input id="em" type="email" value={form.email} onChange={set('email')} required />
          </div>
          <div className="field">
            <label htmlFor="ph">WhatsApp number</label>
            <input id="ph" value={form.phone} onChange={set('phone')} placeholder="919876543210" />
          </div>
          <div className="field">
            <label htmlFor="pw">Password</label>
            <input id="pw" type="password" value={form.password} onChange={set('password')} required minLength={6} />
          </div>
          <button type="submit" disabled={busy} style={{ width: '100%' }}>
            {busy ? 'Creating…' : 'Create account'}
          </button>
        </form>
        <p className="small muted" style={{ marginTop: 14 }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
