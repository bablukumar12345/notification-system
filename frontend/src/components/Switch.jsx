export default function Switch({ checked, onChange, label }) {
  return (
    <label className="switch">
      <input type="checkbox" checked={!!checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="track" />
      <span>{label || (checked ? 'On' : 'Off')}</span>
    </label>
  )
}
