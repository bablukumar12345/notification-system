export default function Toast({ message, kind = 'ok', onClose }) {
  if (!message) return null
  return (
    <div className={`alert ${kind}`} onClick={onClose} role="status">
      {message}
    </div>
  )
}
