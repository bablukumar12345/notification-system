import { useEffect, useState } from 'react'
import { NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api, clearSession, getToken, getUser, setSession } from './api/client.js'
import AdminNotifications from './pages/AdminNotifications.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Login from './pages/Login.jsx'
import Logs from './pages/Logs.jsx'
import Register from './pages/Register.jsx'

export default function App() {
  const [user, setUser] = useState(getUser())
  const navigate = useNavigate()

  useEffect(() => {
    if (getToken() && !user) {
      api.me().then(setUser).catch(() => clearSession())
    }
  }, [])

  function handleAuth(payload) {
    setSession(payload.token, payload.user)
    setUser(payload.user)
    navigate(payload.user.is_admin ? '/admin' : '/dashboard')
  }

  async function handleLogout() {
    try {
      await api.logout()
    } catch {
      /* the token may already be invalid */
    }
    clearSession()
    setUser(null)
    navigate('/login')
  }

  const loggedIn = !!user

  return (
    <>
      <header className="topbar">
        <span className="brand">Notification Console</span>

        {loggedIn && (
          <nav>
            <NavLink to="/dashboard">My account</NavLink>
            {user.is_admin && <NavLink to="/admin">Notification settings</NavLink>}
            {user.is_admin && <NavLink to="/logs">Delivery log</NavLink>}
          </nav>
        )}

        <span className="spacer" />

        {loggedIn ? (
          <div className="row">
            <span className="small topbar-user">
              {user.username}
              {user.is_admin ? ' · admin' : ''}
            </span>
            <button className="tiny outline-light" onClick={handleLogout}>
              Sign out
            </button>
          </div>
        ) : (
          <nav className="auth-nav">
            <NavLink to="/login">Sign in</NavLink>
            <NavLink to="/register" className="cta">
              Create account
            </NavLink>
          </nav>
        )}
      </header>

      <Routes>
        <Route path="/" element={<Navigate to={loggedIn ? '/dashboard' : '/login'} replace />} />
        <Route path="/login" element={loggedIn ? <Navigate to="/dashboard" replace /> : <Login onAuth={handleAuth} />} />
        <Route path="/register" element={loggedIn ? <Navigate to="/dashboard" replace /> : <Register onAuth={handleAuth} />} />
        <Route path="/dashboard" element={loggedIn ? <Dashboard user={user} setUser={setUser} /> : <Navigate to="/login" replace />} />
        <Route path="/admin" element={loggedIn && user.is_admin ? <AdminNotifications /> : <Navigate to="/login" replace />} />
        <Route path="/logs" element={loggedIn && user.is_admin ? <Logs /> : <Navigate to="/login" replace />} />
        <Route path="*" element={<div className="page">Page not found.</div>} />
      </Routes>
    </>
  )
}
