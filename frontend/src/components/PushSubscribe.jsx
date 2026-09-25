import { useEffect, useState } from 'react'
import { api } from '../api/client.js'

const APP_ID = import.meta.env.VITE_ONESIGNAL_APP_ID || ''

/**
 * Subscribes the browser through OneSignal and stores the subscription id on the backend.
 * Web push only works on HTTPS or on localhost.
 */
export default function PushSubscribe() {
  const [state, setState] = useState('idle') // idle | ready | subscribed | error
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!APP_ID) {
      setState('error')
      setMessage('VITE_ONESIGNAL_APP_ID is not set in the frontend .env file.')
      return
    }
    window.OneSignalDeferred = window.OneSignalDeferred || []
    window.OneSignalDeferred.push(async (OneSignal) => {
      try {
        await OneSignal.init({ appId: APP_ID, allowLocalhostAsSecureOrigin: true })
        const id = OneSignal.User?.PushSubscription?.id
        if (id) {
          await saveId(id)
        } else {
          setState('ready')
        }
        OneSignal.User.PushSubscription.addEventListener('change', (event) => {
          const newId = event?.current?.id
          if (newId) saveId(newId)
        })
      } catch (err) {
        setState('error')
        setMessage(String(err.message || err))
      }
    })
  }, [])

  async function saveId(playerId) {
    try {
      await api.subscribePush(playerId)
      setState('subscribed')
      setMessage(`Subscribed. ID: ${playerId.slice(0, 10)}…`)
    } catch (err) {
      setState('error')
      setMessage(err.message)
    }
  }

  async function subscribe() {
    setMessage('')
    window.OneSignalDeferred.push(async (OneSignal) => {
      try {
        await OneSignal.Notifications.requestPermission()
        const id = OneSignal.User?.PushSubscription?.id
        if (id) await saveId(id)
        else setMessage('Permission granted. The subscription id takes a moment, press the button once more.')
      } catch (err) {
        setState('error')
        setMessage(String(err.message || err))
      }
    })
  }

  return (
    <div className="card">
      <h2>Browser notifications</h2>
      <p className="muted small">
        This browser has to subscribe once before web push can reach it. After you allow notifications, the
        subscription is saved on the backend.
      </p>
      <div className="row">
        <button onClick={subscribe} disabled={state === 'subscribed'}>
          {state === 'subscribed' ? 'Subscribed' : 'Turn on browser notifications'}
        </button>
        {state === 'subscribed' && <span className="badge ok">Active</span>}
        {state === 'error' && <span className="badge bad">Problem</span>}
      </div>
      {message && <p className="small muted" style={{ marginTop: 10, marginBottom: 0 }}>{message}</p>}
    </div>
  )
}
