import { cached, logTriage, postJson, timed } from './lib.ts'
import type { Triage } from './lib.ts'
import { DEPARTMENTS, URGENCY, WANTS_REFUND } from './questions.ts'
import { tickets } from './tickets.ts'

export async function askJev(ticket: string): Promise<Triage> {
  const { answers } = await postJson(
    'https://api.typesafe.ai/v1/systemone',
    process.env.TYPESAFE_API_KEY,
    {
      model: 'jev-latest',
      state: { ticket },
      questions: {
        department: {
          type: 'choice',
          instructions: 'Which team should handle this `ticket`?',
          criteria: DEPARTMENTS,
        },
        urgency: {
          type: 'score',
          instructions: 'How urgent is this `ticket`?',
          criteria: URGENCY,
        },
        wantsRefund: { type: 'noul', instructions: WANTS_REFUND },
      },
    }
  )

  return {
    department: answers.department.choice,
    confidence: answers.department.confidence,
    urgency: answers.urgency.score,
    wantsRefund: answers.wantsRefund.noul,
  }
}

if (import.meta.filename === process.argv[1]) {
  for (const ticket of tickets) {
    const [triage, ms] = await timed(() => cached(`jev-${ticket.id}`, () => askJev(ticket.text)))
    logTriage('jev', ticket.id, triage, ms)
  }
}
