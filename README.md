# Beyond LLMs: decision models for smarter AI agents

Talk deck and demo code from "Beyond LLMs: Decision Models for Smarter AI Agents" at AWS User Group DFW, Frisco, Nov 19, 2026.

Most steps in an agent pick from a short list. They don't need to write prose. A decision model answers them with typed answers and probabilities, and your code decides when to trust them.

- [`demo/`](demo/): an outreach agent on AWS. Step Functions runs the workflow, a Strands agent writes the email, Jev decides before and after it, and one Python function owns the threshold. Start with [demo/README.md](demo/README.md).
- [`deck/`](deck/): the slides as one HTML file. Open `deck/index.html` in a browser. Press `N` for speaker notes. [`deck/architecture.svg`](deck/architecture.svg) is the architecture diagram.

The deck is also at [bharad.dev/talks](https://bharad.dev/talks).
