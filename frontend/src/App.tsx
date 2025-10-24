import React, { useEffect, useMemo, useState } from 'react'
import 'katex/dist/katex.min.css'
import katex from 'katex'

type Choice = { id: string; text: string; media?: { id: string; signed_url: string; ttl_s: number; alt: string }[] }

type ServePayload = {
  version: string
  session_id: string
  item: {
    id: string
    type: 'mcq' | string
    content: { html: string }
    media?: { id: string; signed_url: string; ttl_s: number; alt: string }[]
    title?: string
    steps?: { step_id: string; prompt: { html: string }; choices: Choice[]; serve?: { choice_order?: string[] } }[]
  }
  choices?: Choice[]
  serve: { id?: string; seed: string; choice_order?: string[]; watermark: string }
}

type Progress = {
  session_id: string | null
  by_type: Record<string, { attempts: number; correct: number; accuracy: number }>
  overall: { attempts: number; correct: number; accuracy: number }
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
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null)
  const [csrf, setCsrf] = useState<string | null>(null)
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0)
  const [cooldownMs, setCooldownMs] = useState<number>(0)
  const [cooldownTimer, setCooldownTimer] = useState<number | null>(null)
  const [explanationHtml, setExplanationHtml] = useState<string | null>(null)
  const [progress, setProgress] = useState<Progress | null>(null)

  useEffect(() => {
    // Ensure session and obtain CSRF token
    fetch('http://localhost:8000/api/session', { method: 'POST', credentials: 'include' })
      .then(r => r.json())
      .then(j => setCsrf(j.csrf_token))
      .catch(() => {})

    // Fetch next item
    fetch('http://localhost:8000/api/item/next', { credentials: 'include' })
      .then(r => r.json())
      .then(setData)
      .catch(err => console.error(err))

    // Fetch progress
    const fetchProgress = () => {
      fetch('http://localhost:8000/api/progress', { credentials: 'include' })
        .then(r => r.json())
        .then(setProgress)
        .catch(() => {})
    }
    fetchProgress()
    const id = window.setInterval(fetchProgress, 2000)
    return () => window.clearInterval(id)
  }, [])

  const orderedChoices: Choice[] = useMemo(() => {
    if (!data) return []
    // Multi-step
    if (data.item.steps && data.item.steps.length > 0) {
      const step = data.item.steps[currentStepIndex] ?? data.item.steps[0]
      const map = new Map(step.choices.map(c => [c.id, c]))
      const order = step.serve?.choice_order ?? step.choices.map(c => c.id)
      return order.map(id => map.get(id)!).filter(Boolean)
    }
    // Single-step
    const choices = data.choices ?? []
    const map = new Map(choices.map(c => [c.id, c]))
    const order = data.serve.choice_order ?? choices.map(c => c.id)
    return order.map(id => map.get(id)!).filter(Boolean)
  }, [data, currentStepIndex])

  async function onSubmit() {
    if (!data || !selected || !csrf) return
    const stepId = data.item.steps && data.item.steps.length > 0
      ? (data.item.steps[currentStepIndex]?.step_id ?? data.item.steps[0].step_id)
      : 'step_1'
    const body = { session_id: data.session_id, item_id: data.item.id, step_id: stepId, choice_id: selected, serve_id: data.serve.id }
    const res = await fetch('http://localhost:8000/api/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf },
      credentials: 'include',
      body: JSON.stringify(body)
    })
    if (res.status === 429) {
      // Prefer X-RateLimit-Reset (epoch seconds), else Retry-After seconds
      const resetEpoch = parseInt(res.headers.get('X-RateLimit-Reset') || '0', 10)
      let endAt = resetEpoch > 0 ? (resetEpoch * 1000) : (Date.now() + parseInt(res.headers.get('Retry-After') || '10', 10) * 1000)
      // Add small buffer to avoid boundary re-trigger
      endAt += 1500
      setCooldownMs(Math.max(0, endAt - Date.now()))
      if (cooldownTimer) window.clearInterval(cooldownTimer)
      const id = window.setInterval(() => {
        const remaining = Math.max(0, endAt - Date.now())
        setCooldownMs(remaining)
        if (remaining <= 0) {
          window.clearInterval(id)
          setCooldownTimer(null)
        }
      }, 250)
      setCooldownTimer(id)
      return
    }
    const json = await res.json()
    if (res.status === 403 && json?.code === 'csrf_required') {
      setResult('Security check failed. Refresh the page to get a new session and try again.')
      setIsCorrect(null)
      setExplanationHtml(null)
      return
    }
    setIsCorrect(Boolean(json.correct))
    setResult(json.correct ? 'Correct' : 'Incorrect')
    setExplanationHtml(json.explanation?.html ?? null)
    if (json.next_step && data.item.steps && data.item.steps.length > 0) {
      setCurrentStepIndex(idx => Math.min(idx + 1, data.item.steps!.length - 1))
      setSelected(null)
    }
  }

  if (!data) return <div className="p-6">Loading…</div>

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <header className="text-xl font-semibold">Practice</header>
      <section>
        <MathText html={data.item.content.html} />
      </section>
      {data.item.media && data.item.media.length > 0 && (
        <section className="space-y-2">
          {data.item.media.map(m => (
            <figure key={m.id} className="border rounded p-2">
              <img src={m.signed_url} alt={m.alt} className="max-w-full" />
              {m.alt && <figcaption className="text-xs opacity-70 mt-1">{m.alt}</figcaption>}
            </figure>
          ))}
        </section>
      )}
      <section className="space-y-2">
        {data.item.steps && data.item.steps.length > 0 && (
          <div className="text-sm opacity-70">Step {currentStepIndex + 1} of {data.item.steps.length}</div>
        )}
        {orderedChoices.map(ch => (
          <label key={ch.id} className="flex items-center gap-2">
            <input type="radio" name="choice" value={ch.id} onChange={() => setSelected(ch.id)} />
            <span>{ch.text}</span>
            {ch.media && ch.media.length > 0 && (
              <span className="flex items-center gap-2">
                {ch.media.map(m => (
                  <img key={m.id} src={m.signed_url} alt={m.alt} className="h-10 w-auto" />
                ))}
              </span>
            )}
          </label>
        ))}
      </section>
      <button onClick={onSubmit} disabled={!selected || cooldownMs > 0} className="px-3 py-2 rounded bg-gray-800 text-white disabled:opacity-50">Check answer</button>
      {cooldownMs > 0 && (
        <div className="text-xs text-red-600">Too many requests. Try again in {Math.ceil(cooldownMs/1000)}s.</div>
      )}
      {isCorrect !== null && (
        <div className={`text-sm border rounded px-3 py-2 ${isCorrect ? 'bg-green-100 text-green-800 border-green-200' : 'bg-red-100 text-red-800 border-red-200'}`}>
          {isCorrect ? 'Correct' : 'Incorrect'}
        </div>
      )}
      {explanationHtml && (
        <section className="mt-2 p-3 border rounded">
          <div className="font-medium mb-1">Explanation</div>
          <MathText html={explanationHtml} />
        </section>
      )}
      {progress && (
        <aside className="mt-4 p-3 border rounded text-sm">
          <div className="font-medium mb-1">Progress (this session)</div>
          <div className="space-y-1">
            {Object.entries(progress.by_type).map(([type, s]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="opacity-80">{type}</span>
                <span>{s.correct}/{s.attempts} ({Math.round(s.accuracy * 100)}%)</span>
              </div>
            ))}
            <div className="flex items-center justify-between border-t pt-1 mt-1">
              <span className="opacity-80">Overall</span>
              <span>{progress.overall.correct}/{progress.overall.attempts} ({Math.round(progress.overall.accuracy * 100)}%)</span>
            </div>
          </div>
        </aside>
      )}
      <footer className="text-xs opacity-70">{data.serve.watermark}</footer>
    </div>
  )
}
