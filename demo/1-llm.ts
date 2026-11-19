import { execFile } from 'node:child_process'
import { promisify } from 'node:util'

import { cached, logTriage, timed } from './lib.ts'
import type { Triage } from './lib.ts'
import { DEPARTMENTS, URGENCY, WANTS_REFUND } from './questions.ts'
import { tickets } from './tickets.ts'

const run = promisify(execFile)

function promptFor(ticket: string) {
  return `Triage this support ticket. Reply with JSON only, like
{"department": "...", "confidence": 0.0, "urgency": 0, "wantsRefund": 0.0}

department: one of ${JSON.stringify(DEPARTMENTS)}
confidence: how sure you are of the department, 0 to 1
urgency: 0, 1 or 2, meaning ${JSON.stringify(URGENCY)}
wantsRefund: ${WANTS_REFUND} 0 to 1

Ticket: ${ticket}`
}

// The model returns a string. We have to find the JSON in it and hope the fields are right.
function parseTriage(reply: string): Triage {
  const json = reply.match(/\{[\s\S]*\}/)?.[0]
  if (!json) throw new Error(`No JSON in reply: ${reply}`)
  return JSON.parse(json)
}

for (const ticket of tickets) {
  const [reply, ms] = await timed(() =>
    cached(`llm-${ticket.id}`, async () => {
      const { stdout } = await run('claude', ['-p', promptFor(ticket.text), '--model', 'haiku'])
      return stdout
    })
  )
  logTriage('llm', ticket.id, parseTriage(reply), ms)
}
