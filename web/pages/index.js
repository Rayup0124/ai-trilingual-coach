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
  const [lang, setLang] = useState('en') // en | cn | bm
  const [learned, setLearned] = useState(new Set())
  const [loadedDate, setLoadedDate] = useState(null)

  useEffect(() => {
    const owner = 'Rayup0124'
    const repo = 'ai-trilingual-coach'

    // Try today's date first, then fallback up to 6 previous days
    const tryFetch = async () => {
      const today = new Date()
      for (let offset = 0; offset < 7; offset++) {
        const d = new Date(today)
        d.setDate(today.getDate() - offset)
        const dateStr = formatMYDate(d)
        const url = `https://raw.githubusercontent.com/${owner}/${repo}/main/data/${dateStr}.json`
        try {
          const res = await fetch(url)
          if (!res.ok) {
            // try previous day
            continue
          }
          const j = await res.json()
          setData(j)
          setLoading(false)
          // store which date we loaded
          setLoadedDate(dateStr)
          return
        } catch (e) {
          // continue to previous date
          continue
        }
      }

      // fallback: ask server for latest file name
      try {
        const r = await fetch('/api/latest')
        if (r.ok) {
          const info = await r.json()
          if (info && info.latest) {
            const url2 = `https://raw.githubusercontent.com/${owner}/${repo}/main/data/${info.latest}`
            const res2 = await fetch(url2)
            if (res2.ok) {
              const j2 = await res2.json()
              setData(j2)
              setLoading(false)
              setLoadedDate(info.latest.replace('.json', ''))
              return
            }
          }
        }
      } catch (er) {
        // ignore
      }

      setError('Failed to fetch lesson JSON: 404 (no recent data)')
      setLoading(false)
    }

    tryFetch()
  }, [])

  // load learned items from localStorage per date
  useEffect(() => {
    const date = formatMYDate()
    const key = `learned_${date}`
    try {
      const raw = localStorage.getItem(key)
      if (raw) {
        const arr = JSON.parse(raw)
        setLearned(new Set(arr))
      }
    } catch (e) {
      // ignore
    }
  }, [])

  const toggleLearned = (concept) => {
    const date = formatMYDate()
    const key = `learned_${date}`
    const next = new Set(learned)
    if (next.has(concept)) next.delete(concept)
    else next.add(concept)
    setLearned(next)
    try {
      localStorage.setItem(key, JSON.stringify(Array.from(next)))
    } catch (e) {}
  }

  const exportPDF = () => {
    window.print()
  }

  if (loading) return <div className="page"><h2>Loading today's lesson...</h2></div>
  if (error) return <div className="page"><h3>Error</h3><pre>{error}</pre></div>

  // defensive access to avoid runtime errors if data shape is unexpected
  const theme = (data && data.theme) || 'Daily Lesson'
  const vocabulary_focus = Array.isArray(data && data.vocabulary_focus) ? data.vocabulary_focus : []
  const practice_scenarios = (data && data.practice_scenarios) || {}
  const quiz_toggle = Array.isArray(data && data.quiz_toggle) ? data.quiz_toggle : []

  return (
    <div className="page">
      <header>
        <div className="header-row">
          <h1>📚 {loadedDate ? loadedDate : new Date().toLocaleDateString()} - {theme}</h1>
          <div className="controls">
            <div className="lang-switch">
              <button className={lang==='en'?'active':''} onClick={()=>setLang('en')}>EN</button>
              <button className={lang==='cn'?'active':''} onClick={()=>setLang('cn')}>中文</button>
              <button className={lang==='bm'?'active':''} onClick={()=>setLang('bm')}>BM</button>
            </div>
            <button className="export-btn" onClick={exportPDF}>Export / Print</button>
          </div>
        </div>
      </header>

      <section className="vocab">
        <h2>🎯 Key Vocabulary</h2>
        {loadedDate && loadedDate !== formatMYDate() && (
          <div style={{color:'#b33',marginBottom:8}}>Note: showing most recent available lesson ({loadedDate})</div>
        )}
        <ul>
          {vocabulary_focus.map((v, i) => {
            const e = v.expressions || {}
            const concept = v.concept || `item-${i}`
            const isLearned = learned.has(concept)
            return (
              <li key={i} className={isLearned ? 'learned' : ''}>
                <div className="vocab-row">
                  <strong>{v.concept}</strong>
                  <button className="learn-toggle" onClick={()=>toggleLearned(concept)}>{isLearned ? '✓ Learned' : 'Mark learned'}</button>
                </div>
                <div className="expr">
                  <span className="en" style={{display: lang==='en' ? 'inline' : 'none'}}>{e.en}</span>
                  <span className="cn" style={{display: lang==='cn' ? 'inline' : 'none'}}>{e.cn}</span>
                  <span className="bm" style={{display: lang==='bm' ? 'inline' : 'none'}}>{e.bm_formal || e.bm_casual}</span>
                  {/* show condensed multilingual line when all selected */}
                  <div className="multilang" style={{display: lang==='all' ? 'block' : 'none'}}>{e.en} · {e.cn} · {e.bm_formal || e.bm_casual}</div>
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


