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
    <main style={{ maxWidth: 720, margin: '2rem auto', padding: '0 1rem' }}>
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
        <p style={{ marginTop: '0.75rem', color: '#555' }}>
          Running detection on each frame. This usually takes about a minute.
        </p>
      )}

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {data?.video_url && (
        <video
          key={data.video_url}
          src={data.video_url}
          controls
          style={{ marginTop: '1rem', width: '100%' }}
        />
      )}
    </main>
  )
}

export default App
