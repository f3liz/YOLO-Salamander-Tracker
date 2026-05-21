import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [data, setData] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) return
    setSubmitting(true)
    setError(null)
    setData(null)
    try {
      const form = new FormData()
      form.append('video', file)
      const res = await fetch('http://localhost:8000/track', {
        method: 'POST',
        body: form,
      })
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
      setData(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="app">
      <h1>Salamander Tracker</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit" disabled={!file || submitting}>
          {submitting ? 'Processing…' : 'Upload'}
        </button>
      </form>

      {submitting && (
        <p className="status">
          Running detection on each frame. This usually takes about a minute.
        </p>
      )}

      {error && <p className="error">{error}</p>}

      {data?.video_url && (
        <div className="results">
          <video key={data.video_url} src={data.video_url} controls />
          <table className="tracks-table">
            <thead>
              <tr>
                <th>Track ID</th>
                <th>Label</th>
                <th>Time on screen (s)</th>
              </tr>
            </thead>
            <tbody>
              {data.tracks?.map((t) => (
                <tr key={t.track_id}>
                  <td>{t.track_id}</td>
                  <td>{t.label}</td>
                  <td>{t.time_on_screen_s}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}

export default App
