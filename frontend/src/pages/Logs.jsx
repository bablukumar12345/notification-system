import { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import Toast from '../components/Toast.jsx'

const LABEL = { whatsapp: 'WhatsApp', email: 'Email', webpush: 'Web Push' }

export default function Logs() {
  const [logs, setLogs] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    try {
      setLogs(await api.logs())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="page">
      <div className="page-head">
        <h1>Delivery log</h1>
        <p className="muted">Every attempt is recorded here: which trigger ran, on which channel, and what was sent.</p>
      </div>

      <Toast message={error} kind="bad" onClose={() => setError('')} />

      <div className="row" style={{ marginBottom: 14 }}>
        <button className="ghost" onClick={load}>Refresh</button>
      </div>

      {loading ? (
        <p className="muted">Loading…</p>
      ) : logs.length === 0 ? (
        <div className="card">
          <h2>Nothing sent yet</h2>
          <p className="muted">Fire a trigger or send a test from a template and the entry will appear here.</p>
        </div>
      ) : (
        <div className="table-wrap">
          <table className="logs">
            <thead>
              <tr>
                <th>Time</th>
                <th>Trigger</th>
                <th>Channel</th>
                <th>To</th>
                <th>Message</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>
                    {log.trigger_code}
                    {log.is_test && <span className="badge off" style={{ marginLeft: 6 }}>test</span>}
                  </td>
                  <td>
                    <span className={`ch-dot ch-${log.channel}`} />
                    {LABEL[log.channel] || log.channel}
                  </td>
                  <td>{log.recipient || '—'}</td>
                  <td style={{ maxWidth: 260 }}>
                    {log.rendered_subject && <strong>{log.rendered_subject}<br /></strong>}
                    <span className="muted">{log.rendered_body?.slice(0, 80)}</span>
                  </td>
                  <td>
                    <span className={`badge ${log.status === 'sent' ? 'ok' : 'bad'}`}>{log.status}</span>
                    {log.status !== 'sent' && (
                      <div className="small muted">{log.provider_response?.slice(0, 90)}</div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
