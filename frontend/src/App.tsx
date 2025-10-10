import React, { useEffect, useMemo, useState } from 'react'
import 'katex/dist/katex.min.css'
import katex from 'katex'

type Choice = { id: string; text: string }

type ServePayload = {
  version: string
  session_id: string
  item: { id: string; type: 'mcq'; content: { html: string } }
  choices: Choice[]
  serve: { seed: string; choice_order: string[]; watermark: string }
}

function MathText({ html }: { html: string }) {
  const __html = useMemo(() => {
    // Render inline math; keep plain HTML otherwise
    // We rely on KaTeX auto-render patterns minimally by manual split
    return html.replace(/\\\((.*?)\\\)/g, (_, expr) => katex.renderToString(expr, { throwOnError: false }))
  }, [html])
  return <div dangerouslySetInnerHTML={{ __html }} />
}

export default function App() {
  const [data, setData] = useState<ServePayload | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [result, setResult] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/item/next', { credentials: 'include' })
      .then(r => r.json())
      .then(setData)
      .catch(err => console.error(err))
  }, [])

  const orderedChoices: Choice[] = useMemo(() => {
    if (!data) return []
    const map = new Map(data.choices.map(c => [c.id, c]))
    return data.serve.choice_order.map(id => map.get(id)!).filter(Boolean)
  }, [data])

  async function onSubmit() {
    if (!data || !selected) return
    const body = { session_id: data.session_id, item_id: data.item.id, step_id: 'step_1', choice_id: selected }
    const res = await fetch('http://localhost:8000/api/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body)
    })
    const json = await res.json()
    setResult(json.correct ? 'Correct' : 'Incorrect')
  }

  if (!data) return <div className="p-6">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <header className="text-xl font-semibold">Practice</header>
      <section>
        <MathText html={data.item.content.html} />
      </section>
      <section className="space-y-2">
        {orderedChoices.map(ch => (
          <label key={ch.id} className="flex items-center gap-2">
            <input type="radio" name="choice" value={ch.id} onChange={() => setSelected(ch.id)} />
            <span>{ch.text}</span>
          </label>
        ))}
      </section>
      <button onClick={onSubmit} className="px-3 py-2 rounded bg-gray-800 text-white">Check</button>
      {result && <div className="text-sm">{result}</div>}
      <footer className="text-xs opacity-70">{data.serve.watermark}</footer>
    </div>
  )
}
