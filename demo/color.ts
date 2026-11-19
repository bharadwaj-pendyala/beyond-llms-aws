import { readFileSync } from 'node:fs'

import { postJson } from './lib.ts'

const KINDS = {
  decide: 'The answer is one item from a short list you could write down today, such as a team, yes or no, or a level.',
  generate: 'The answer is new text, such as a reply, a summary, or code.',
  code: 'Plain code can do it with no model, such as a lookup, a calculation, or an API call.',
}

const SAMPLE_STEPS = [
  'Pick which team owns the ticket',
  'Decide if the ticket is urgent',
  'Check if the customer wants money back',
  'Pick the next tool to call',
  'Look up the order in the database',
  'Decide if the charge was a duplicate',
  'Write the reply to the customer',
]

async function colorStep(step: string) {
  const { answers } = await postJson(
    'https://api.typesafe.ai/v1/systemone',
    process.env.TYPESAFE_API_KEY,
    {
      model: 'jev-latest',
      state: { step },
      questions: {
        kind: {
          type: 'choice',
          instructions: 'An AI agent runs this `step`. What kind of work is it?',
          criteria: KINDS,
        },
      },
    }
  )
  return { kind: answers.kind.choice, confidence: answers.kind.confidence }
}

const file = process.argv[2]
const steps = file ? readFileSync(file, 'utf8').split('\n').filter(Boolean) : SAMPLE_STEPS

const results = await Promise.all(steps.map(colorStep))
results.forEach(({ kind, confidence }, i) => {
  console.log(`[color] ${kind.toUpperCase().padEnd(8)} ${`${Math.round(confidence * 100)}%`.padStart(4)}  ${steps[i]}`)
})

const decisions = results.filter((r) => r.kind === 'decide').length
console.log(`\n${decisions} of ${steps.length} steps are decisions.`)
