import { useEffect, useState } from 'react'
import { CHANNELS, api } from '../api/client.js'
import Switch from '../components/Switch.jsx'
import TemplateModal from '../components/TemplateModal.jsx'
import Toast from '../components/Toast.jsx'

export default function AdminNotifications() {
  const [triggers, setTriggers] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState(null)
  const [editing, setEditing] = useState(null) // { trigger, channel, template }
  const [newTrigger, setNewTrigger] = useState({ code: '', name: '', description: '' })
  const [showAdd, setShowAdd] = useState(false)

  async function load() {
    setLoading(true)
    try {
      setTriggers(await api.triggers())
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function toggleTemplate(template, value) {
    try {
      await api.toggleTemplate(template.id, value)
      setTriggers((prev) =>
        prev.map((t) => ({
          ...t,
          channels: Object.fromEntries(
            Object.entries(t.channels).map(([k, v]) =>
              v && v.id === template.id ? [k, { ...v, is_enabled: value }] : [k, v]
            )
          ),
        }))
      )
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    }
  }

  async function fireRow(trigger) {
    try {
      const res = await api.fireTriggerById(trigger.id)
      const lines = res.results.map((r) => `${r.channel}: ${r.ok ? 'sent' : r.detail}`).join(' · ')
      setToast({ kind: 'ok', text: `${trigger.name} fired — ${lines}` })
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    }
  }

  async function addTrigger(e) {
    e.preventDefault()
    try {
      await api.createTrigger(newTrigger)
      setNewTrigger({ code: '', name: '', description: '' })
      setShowAdd(false)
      setToast({ kind: 'ok', text: 'Trigger added.' })
      load()
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    }
  }

  async function removeTrigger(trigger) {
    if (!confirm(`Delete "${trigger.name}" and all of its templates?`)) return
    try {
      await api.deleteTrigger(trigger.id)
      load()
    } catch (err) {
      setToast({ kind: 'bad', text: err.message })
    }
  }

  return (
    <div className="page">
      <div className="page-head">
        <h1>Notification settings</h1>
        <p className="muted">
          Every row is a trigger and every column is a channel. Open a cell to write the message, use the toggle to turn a
          channel on or off, and send a test to check it. You never have to open WhatsApp, Postmark or OneSignal.
        </p>
      </div>

      {toast && <Toast message={toast.text} kind={toast.kind} onClose={() => setToast(null)} />}

      <div className="row" style={{ marginBottom: 14 }}>
        <button onClick={() => setShowAdd(!showAdd)}>{showAdd ? 'Cancel' : 'Add trigger'}</button>
        <button className="ghost" onClick={load}>
          Refresh
        </button>
      </div>

      {showAdd && (
        <form className="card" onSubmit={addTrigger}>
          <h2>New trigger</h2>
          <div className="grid-2">
            <div className="field">
              <label htmlFor="nc">Code (the backend fires the trigger by this name)</label>
              <input
                id="nc"
                value={newTrigger.code}
                onChange={(e) => setNewTrigger({ ...newTrigger, code: e.target.value })}
                placeholder="cart_abandoned"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="nn">Display name</label>
              <input
                id="nn"
                value={newTrigger.name}
                onChange={(e) => setNewTrigger({ ...newTrigger, name: e.target.value })}
                placeholder="Cart abandoned"
                required
              />
            </div>
          </div>
          <div className="field">
            <label htmlFor="nd">When does it fire?</label>
            <input
              id="nd"
              value={newTrigger.description}
              onChange={(e) => setNewTrigger({ ...newTrigger, description: e.target.value })}
              placeholder="User left items in the cart"
            />
          </div>
          <button type="submit">Save trigger</button>
        </form>
      )}

      {loading ? (
        <p className="muted">Loading triggers…</p>
      ) : triggers.length === 0 ? (
        <div className="card">
          <h2>No triggers yet</h2>
          <p className="muted">Select Add trigger to create your first one, such as Login.</p>
        </div>
      ) : (
        <div className="table-wrap">
          <table className="matrix">
            <thead>
              <tr>
                <th>Trigger</th>
                {CHANNELS.map((c) => (
                  <th key={c.key}>
                    <span className={`ch-dot ch-${c.key}`} />
                    {c.label}
                  </th>
                ))}
                <th />
              </tr>
            </thead>
            <tbody>
              {triggers.map((trigger) => (
                <tr key={trigger.id}>
                  <td className="trigger-cell">
                    <strong>{trigger.name}</strong>
                    <code>{trigger.code}</code>
                    {trigger.description && <div className="small muted">{trigger.description}</div>}
                  </td>

                  {CHANNELS.map((c) => {
                    const template = trigger.channels[c.key]
                    return (
                      <td key={c.key}>
                        <div className="cell">
                          {template ? (
                            <>
                              <div className="cell-preview">
                                {(template.subject || template.title) && (
                                  <span className="subject">{template.subject || template.title}</span>
                                )}
                                {template.body?.slice(0, 90) || '(template name only)'}
                                {template.body?.length > 90 ? '…' : ''}
                              </div>
                              <div className="cell-actions">
                                <button
                                  className="tiny ghost"
                                  onClick={() => setEditing({ trigger, channel: c.key, template })}
                                >
                                  Edit
                                </button>
                                <Switch
                                  checked={template.is_enabled}
                                  onChange={(v) => toggleTemplate(template, v)}
                                />
                              </div>
                            </>
                          ) : (
                            <>
                              <span className="cell-empty">No template</span>
                              <button
                                className="tiny"
                                onClick={() => setEditing({ trigger, channel: c.key, template: null })}
                              >
                                Create template
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    )
                  })}

                  <td>
                    <div className="cell-actions">
                      <button className="tiny ghost" onClick={() => fireRow(trigger)}>
                        Fire now
                      </button>
                      <button className="tiny ghost" onClick={() => removeTrigger(trigger)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <TemplateModal
          trigger={editing.trigger}
          channel={editing.channel}
          template={editing.template}
          onClose={() => setEditing(null)}
          onSaved={(saved) => {
            setEditing(saved ? { ...editing, template: saved } : null)
            load()
          }}
        />
      )}
    </div>
  )
}
