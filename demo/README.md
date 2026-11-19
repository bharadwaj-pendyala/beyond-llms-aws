# Beyond LLMs: decision models demo

Demo code for the talk "Beyond LLMs: Decision Models for Smarter AI Agents" (AWS User Group DFW, Nov 19, 2026).

Two demos and one tool:

1. **Support ticket triage.** The same three questions, asked two ways: a general LLM, then Jev.
2. **jev-router.** A Claude Code mod that asks Jev which model fits each task and switches to it. It lives in its own repo: [bharadwaj-pendyala/jev-router](https://github.com/bharadwaj-pendyala/jev-router).
3. **color.** Give it your agent's steps. Jev labels each one as decide, generate, or code.

## Run it

Node 23.6 or newer. No dependencies.

```bash
export TYPESAFE_API_KEY=...   # https://console.typesafe.ai/keys
npm run llm     # 1-llm.ts: claude -p with Haiku, parse JSON out of a string
npm run jev     # 2-jev.ts: typed answers from Jev
npm run route   # 4-route.ts: act on confident answers, send the rest to a person
npm run color   # color.ts: label the sample agent steps
npm run color -- my-steps.txt   # or your own, one step per line
```

Triage responses are saved to `.cache/`. If the network fails, each triage step replays the last saved response.

The `llm` timing includes `claude -p` startup, so it is not a pure model latency number.

Jev's confidence can change a little between runs. In testing, ticket T-1047 came back between 41% and 68%.
