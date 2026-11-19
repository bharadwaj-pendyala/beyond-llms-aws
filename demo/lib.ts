import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'

export type Triage = {
  department: string
  confidence: number
  urgency: number
  wantsRefund: number
}

// Responses are saved to .cache/ so the demo still runs when the venue Wi-Fi does not.
export async function cached<T>(key: string, fetchFresh: () => Promise<T>): Promise<T> {
  const file = `.cache/${key}.json`
  try {
    const fresh = await fetchFresh()
    mkdirSync('.cache', { recursive: true })
    writeFileSync(file, JSON.stringify(fresh, null, 2))
    return fresh
  } catch (error) {
    if (!existsSync(file)) throw error
    console.log(`  (offline, replaying ${file})`)
    return JSON.parse(readFileSync(file, 'utf8'))
  }
}

export async function postJson(url: string, apiKey: string | undefined, body: unknown) {
  if (!apiKey) throw new Error(`No API key for ${url}`)
  const res = await fetch(url, {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${url} returned ${res.status}: ${await res.text()}`)
  return res.json()
}

export async function timed<T>(work: () => Promise<T>): Promise<[T, number]> {
  const startedAt = performance.now()
  const value = await work()
  return [value, Math.round(performance.now() - startedAt)]
}

export function logTriage(who: string, id: string, triage: Triage, ms: number) {
  const pct = (n: number) => `${Math.round(n * 100)}%`.padStart(4)
  console.log(
    `[${who}] ${id}  ${triage.department.padEnd(9)} ${pct(triage.confidence)}  ` +
      `urgency ${triage.urgency.toFixed(1)}  refund ${pct(triage.wantsRefund)}  ${String(ms).padStart(6)}ms`
  )
}
