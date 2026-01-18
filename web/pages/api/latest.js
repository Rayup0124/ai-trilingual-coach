export default async function handler(req, res) {
  const owner = 'Rayup0124'
  const repo = 'ai-trilingual-coach'
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/data`
  try {
    const r = await fetch(url, { headers: { 'User-Agent': 'ai-trilingual-coach' } })
    if (!r.ok) {
      return res.status(r.status).json({ error: 'Failed to list data directory' })
    }
    const items = await r.json()
    // items is array with name and path
    const files = items.filter(i => i.type === 'file' && i.name.endsWith('.json')).map(i => i.name)
    files.sort().reverse()
    return res.json({ latest: files[0] || null, files })
  } catch (e) {
    return res.status(500).json({ error: e.message })
  }
}


