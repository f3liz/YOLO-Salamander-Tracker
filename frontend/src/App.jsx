import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [data, setData] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [percent, setPercent] = useState(0)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) return
    setSubmitting(true)
    setError(null)
    setData(null)
    setPercent(0)
    try {
      const form = new FormData()
      form.append('video', file)
      const res = await fetch('http://localhost:8000/track', {
        method: 'POST',
        body: form,
      })
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`)

      while (true) {
        await new Promise((r) => setTimeout(r, 1500))
        const pollRes = await fetch('http://localhost:8000/track')
        if (!pollRes.ok) throw new Error(`Poll failed: ${pollRes.status}`)
        const job = await pollRes.json()
        setPercent(job.percent ?? 0)
        if (job.status === 'done') {
          setData(job.result)
          break
        }
        if (job.status === 'error') {
          throw new Error(job.message || 'Processing failed')
        }
      }
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
        <div className="status">
          <p>Running detection on each frame. This usually takes about a minute.</p>
          <progress value={percent} max={100} />
          <span className="percent">{percent}%</span>
        </div>
      )}

      {error && <p className="error">{error}</p>}

      {data?.video_url && (
        <div className="results">
          <video key={data.video_url} src={data.video_url} controls />
          <div className="tables">
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
            <table className="tracks-table">
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Dwell Time (s)</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(data.region_dwell_times_seconds || {}).map(
                  ([region, time]) => (
                    <tr key={region}>
                      <td>
                        {region
                          .replace('_', ' ')
                          .replace(/\b\w/g, (char) => char.toUpperCase())}
                      </td>
                      <td>{time}</td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </main>
  )
}

export default App
