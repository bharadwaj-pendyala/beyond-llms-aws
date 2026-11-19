import { askJev } from './2-jev.ts'
import { cached } from './lib.ts'
import { tickets } from './tickets.ts'

const SURE_ENOUGH = 0.8

for (const ticket of tickets) {
  const triage = await cached(`jev-${ticket.id}`, () => askJev(ticket.text))

  if (triage.confidence < SURE_ENOUGH) {
    console.log(`[route] ${ticket.id}  → human queue (only ${Math.round(triage.confidence * 100)}% sure)`)
    continue
  }

  const queue = triage.urgency > 1.5 ? `${triage.department}-urgent` : triage.department
  const refund = triage.wantsRefund > 0.5 ? ', refund check' : ''
  console.log(`[route] ${ticket.id}  → ${queue}${refund}`)
}
