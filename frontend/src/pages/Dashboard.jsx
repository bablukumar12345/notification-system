import { useState } from 'react'
import { api, setSession } from '../api/client.js'
import PushSubscribe from '../components/PushSubscribe.jsx'
import Toast from '../components/Toast.jsx'

const DEMO_TRIGGERS = [
  { code: 'order_placed', label: 'Place a demo order' },
  { code: 'password_reset', label: 'Request password reset' },
]

export default function Dashboard({ user, setUser }) {
  const [phone, setPhone] = useState(user.phone || '')
  const [email, setEmail] = useState(user.email || '')
  const [toast, setToast] = useState(null)
  const [busy, setBusy] = useState('')

  async function saveContact(e) {
    e.preventDefault()
    setBusy('save')
    try {
      const updated = await api.updateMe({ phone, email })
      setUser(updated)
      setSession(null, updated)
      setToast({ kind: 'ok', text: 'Contact details saved.' })
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    } finally {
      setBusy('')
    }
  }

  async function fire(code, label) {
    setBusy(code)
    try {
      const res = await api.fireTrigger(code)
      const lines = res.results.map((r) => `${r.channel}: ${r.ok ? 'sent' : r.detail}`).join(' · ')
      setToast({ kind: 'ok', text: `${label} fired — ${lines}` })
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    } finally {
      setBusy('')
    }
  }

  return (
    <div className="page">
      <div className="page-head">
        <h1>Hi {user.first_name || user.username}</h1>
        <p className="muted">
          This is the normal user site. Whatever you do here is what fires the triggers on the backend.
        </p>
      </div>

      {toast && <Toast message={toast.text} kind={toast.kind} onClose={() => setToast(null)} />}

      <div className="card">
        <h2>Where your notifications go</h2>
        <form onSubmit={saveContact} className="grid-2">
          <div className="field">
            <label htmlFor="em">Email</label>
            <input id="em" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="ph">WhatsApp number (country code, no plus sign)</label>
            <input id="ph" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="919876543210" />
          </div>
          <div style={{ alignSelf: 'end', marginBottom: 14 }}>
            <button type="submit" disabled={busy === 'save'}>
              {busy === 'save' ? 'Saving…' : 'Save changes'}
            </button>
          </div>
        </form>
      </div>

      <PushSubscribe />

      <div className="card">
        <h2>Do something on the site</h2>
        <p className="muted small">
          Login and logout fire on their own. The buttons below fire the other triggers for a demo.
        </p>
        <div className="row">
          {DEMO_TRIGGERS.map((t) => (
            <button key={t.code} className="ghost" disabled={busy === t.code} onClick={() => fire(t.code, t.label)}>
              {busy === t.code ? 'Sending…' : t.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
