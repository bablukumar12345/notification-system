import { useState } from 'react'
import { api } from '../api/client.js'
import Toast from './Toast.jsx'

const CHANNEL_LABEL = { whatsapp: 'WhatsApp', email: 'Email', webpush: 'Web Push' }

export default function TemplateModal({ trigger, channel, template, onClose, onSaved }) {
  const [form, setForm] = useState({
    subject: template?.subject || '',
    title: template?.title || '',
    body: template?.body || '',
    whatsapp_template_name: template?.whatsapp_template_name || '',
    whatsapp_language: template?.whatsapp_language || 'en_US',
    is_enabled: template ? template.is_enabled : true,
  })
  const [toast, setToast] = useState(null)
  const [busy, setBusy] = useState('')
  const [testTo, setTestTo] = useState('')

  function set(key) {
    return (e) => setForm({ ...form, [key]: e.target.value })
  }

  async function save() {
    setBusy('save')
    setToast(null)
    try {
      const payload = { ...form, trigger: trigger.id, channel }
      const saved = template
        ? await api.updateTemplate(template.id, payload)
        : await api.createTemplate(payload)
      onSaved(saved)
      setToast({ kind: 'ok', text: 'Template saved.' })
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    } finally {
      setBusy('')
    }
  }

  async function testSend() {
    if (!template) {
      setToast({ kind: 'bad', text: 'Save the template first, then send a test.' })
      return
    }
    setBusy('test')
    setToast(null)
    try {
      const payload = {}
      if (testTo && channel === 'whatsapp') payload.phone = testTo
      if (testTo && channel === 'email') payload.email = testTo
      if (testTo && channel === 'webpush') payload.player_id = testTo
      const res = await api.testSend(template.id, payload)
      setToast({ kind: 'ok', text: `Test sent to ${res.recipient || 'you'}.` })
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    } finally {
      setBusy('')
    }
  }

  async function remove() {
    if (!template) return onClose()
    if (!confirm('Delete this template?')) return
    setBusy('delete')
    try {
      await api.deleteTemplate(template.id)
      onSaved(null)
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
      setBusy('')
    }
  }

  const testPlaceholder = {
    whatsapp: 'Optional: 919876543210',
    email: 'Optional: you@example.com',
    webpush: 'Optional: OneSignal subscription id',
  }[channel]

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true">
        <div className="modal-head">
          <div>
            <h2>
              {CHANNEL_LABEL[channel]} · {trigger.name}
            </h2>
            <span className="small muted">Trigger code: {trigger.code}</span>
          </div>
          <button className="ghost tiny" onClick={onClose}>
            Close
          </button>
        </div>

        {toast && <Toast message={toast.text} kind={toast.kind} onClose={() => setToast(null)} />}

        {channel === 'email' && (
          <div className="field">
            <label htmlFor="subject">Subject</label>
            <input id="subject" value={form.subject} onChange={set('subject')} placeholder="You logged in successfully" />
          </div>
        )}

        {channel === 'webpush' && (
          <div className="field">
            <label htmlFor="title">Notification title</label>
            <input id="title" value={form.title} onChange={set('title')} placeholder="Welcome back!" />
          </div>
        )}

        {channel === 'whatsapp' && (
          <div className="grid-2">
            <div className="field">
              <label htmlFor="wtn">Approved template name (optional)</label>
              <input id="wtn" value={form.whatsapp_template_name} onChange={set('whatsapp_template_name')} placeholder="hello_world" />
            </div>
            <div className="field">
              <label htmlFor="wlang">Language code</label>
              <input id="wlang" value={form.whatsapp_language} onChange={set('whatsapp_language')} />
            </div>
          </div>
        )}

        <div className="field">
          <label htmlFor="body">Message</label>
          <textarea id="body" value={form.body} onChange={set('body')} placeholder="Welcome back, {{name}}!" />
        </div>

        <p className="var-hint">
          Variables: <code>{'{{name}}'}</code> <code>{'{{username}}'}</code> <code>{'{{email}}'}</code>{' '}
          <code>{'{{phone}}'}</code> <code>{'{{site}}'}</code> are replaced with real values when the message is sent.
        </p>

        <div className="field" style={{ marginTop: 14 }}>
          <label htmlFor="testto">Send a test to</label>
          <input id="testto" value={testTo} onChange={(e) => setTestTo(e.target.value)} placeholder={testPlaceholder} />
          <span className="small muted">Leave it empty to send to your own admin account.</span>
        </div>

        <div className="modal-foot">
          {template && (
            <button className="danger tiny" onClick={remove} disabled={busy === 'delete'}>
              Delete
            </button>
          )}
          <span style={{ flex: 1 }} />
          <button className="ghost" onClick={testSend} disabled={busy === 'test'}>
            {busy === 'test' ? 'Sending…' : 'Send test'}
          </button>
          <button onClick={save} disabled={busy === 'save'}>
            {busy === 'save' ? 'Saving…' : 'Save template'}
          </button>
        </div>
      </div>
    </div>
  )
}
