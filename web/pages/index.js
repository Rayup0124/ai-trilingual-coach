import { useEffect, useState } from 'react'

function formatMYDate(date = new Date()) {
  // convert to Malaysia time (UTC+8) and return YYYY-MM-DD
  const utc = date.getTime() + date.getTimezoneOffset() * 60000
  const malayTime = new Date(utc + 8 * 3600000)
  const y = malayTime.getFullYear()
  const m = String(malayTime.getMonth() + 1).padStart(2, '0')
  const d = String(malayTime.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export default function Home() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const date = formatMYDate()
    const owner = 'Rayup0124'
    const repo = 'ai-trilingual-coach'
    const url = `https://raw.githubusercontent.com/${owner}/${repo}/main/data/${date}.json`

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch lesson JSON: ${res.status}`)
        return res.json()
      })
      .then((j) => {
        setData(j)
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="page"><h2>Loading today's lesson...</h2></div>
  if (error) return <div className="page"><h3>Error</h3><pre>{error}</pre></div>

  const { theme, vocabulary_focus = [], practice_scenarios = {}, quiz_toggle = [] } = data

  return (
    <div className="page">
      <header>
        <h1>📚 {new Date().toLocaleDateString()} - {theme}</h1>
      </header>

      <section className="vocab">
        <h2>🎯 Key Vocabulary</h2>
        <ul>
          {vocabulary_focus.map((v, i) => {
            const e = v.expressions || {}
            return (
              <li key={i}>
                <strong>{v.concept}</strong>
                <div className="expr">
                  <span className="en">{e.en}</span>
                  <span className="cn">{e.cn}</span>
                  <span className="bm">{e.bm_formal} / {e.bm_casual}</span>
                </div>
              </li>
            )
          })}
        </ul>
      </section>

      <section className="scenarios">
        <h2>📖 Practice Scenarios</h2>
        {Object.keys(practice_scenarios).map((k) => {
          const sc = practice_scenarios[k]
          return (
            <article key={k}>
              <h3>{k}</h3>
              <p>{sc.scenario}</p>
              {sc.key_phrases && (
                <ul>
                  {sc.key_phrases.map((p, idx) => <li key={idx}>{p}</li>)}
                </ul>
              )}
            </article>
          )
        })}
      </section>

      <section className="quiz">
        <h2>❓ Quiz</h2>
        {quiz_toggle.map((q, i) => (
          <details key={i}>
            <summary>{q.question}</summary>
            <div className="answer">{q.answer}</div>
          </details>
        ))}
      </section>

      <footer>
        <small>Generated automatically — AI Trilingual Coach</small>
      </footer>
    </div>
  )
}


