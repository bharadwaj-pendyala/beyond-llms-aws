# Beyond LLMs: an outreach agent on AWS

Demo code for the talk "Beyond LLMs: Decision Models for Smarter AI Agents" (AWS User Group DFW).

An agent follows up with people who visited a conference booth, on behalf of an account executive (AE). The agent writes the email. Jev decides whether it should go out.

```
booth lead ─▶ do-not-contact? ─▶ Jev: what do they want? ─▶ agent writes draft ─▶ Jev: does it promise anything? ─▶ send, or wait for the AE
               (code rule)         (choice + probabilities)    (Strands agent)         (yes/no probability)            (code owns the threshold)
```

| Step | Runs on | Kind |
| --- | --- | --- |
| Do-not-contact check | Lambda + DynamoDB | Code. A hard rule is an `if`, not a model call. |
| What do they want? | Jev | Decide. `meeting`, `pricing`, `info` or `unclear`, with a probability for each option. |
| Write the draft | Strands agent: Claude on the Anthropic API, or Amazon Bedrock | Generate. Two tools: `lookup_account` and `recent_activity`. |
| Does it promise anything? | Jev | Decide. Probability that the draft promises a discount, date or feature. |
| Send or ask the AE | `src/policy.py` + Step Functions | Code. One `route()` function. Step Functions branches on its label. |
| AE approval | Step Functions `waitForTaskToken` + SES | A person. The workflow pauses until the AE clicks a link. |

The thresholds live in one place, [src/policy.py](src/policy.py). The state machine has no numbers in it.

## Run it locally first

You need Python 3.13+, [uv](https://docs.astral.sh/uv/), a TypeSafe API key, and an Anthropic API key or AWS credentials that can call Bedrock. No deployment is needed. The CRM reads `seed/crm.json`.

```bash
cp .env.example .env          # add TYPESAFE_API_KEY and ANTHROPIC_API_KEY

make test
make local                    # all five leads
make local LEADS="L-2"        # one lead
make reroute T=0.9 LOCAL=1    # re-route the last run at a new threshold, with no model calls
```

Every live call is saved to `.cache/`. If the network fails, the scripts replay the last saved answer and print `(offline, replaying ...)`.

## Deploy it

You also need the [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) and an email address you can read. It plays the account executive.

```bash
make deploy    # first time asks for AeEmail, CustomerEmail and ModelId. Answers go to samconfig.toml.
make setup     # stores the Jev key in SSM, starts SES email verification, seeds the CRM table
```

Click the verification link that AWS sends to `AeEmail`. Then run:

```bash
make run              # one Step Functions execution per lead. Prints a console link for each.
make logs             # follow the Lambda logs
make approve LEAD=L-2 # approve from the terminal if the email link is slow
make reroute T=0.9    # re-route the deployed runs at a new threshold
```

The seed leads have fictional addresses. Every follow-up goes to `CustomerEmail` instead, and the subject shows which lead it was for. The default is `success@simulator.amazonses.com`, the SES mailbox simulator. It accepts mail in sandbox mode and delivers it nowhere. The AE gets a blind copy of every follow-up and every approval request.

## The five leads

| Lead | Note says | Expected path |
| --- | --- | --- |
| L-1 | Wants Team plan pricing before a budget review | Jev is sure, draft is clean, email sent |
| L-2 | Asks to beat a vendor's price and when SSO ships | Jev splits pricing and meeting, so the AE approves the draft |
| L-3 | Grabbed a sticker | Jev gives `unclear` a real chance, so no email |
| L-4 | Wants a call, but the contact opted out | Blocked by the do-not-contact rule. Jev is never asked. |
| L-5 | Wants a call with a solutions engineer | Jev is sure, email sent |

Jev's confidence can change a little between runs. Run the demo once before you present and check the paths.

## Configure

- `ModelProvider` (default `anthropic`): `anthropic` uses Claude through the Anthropic API with `ANTHROPIC_API_KEY`. `bedrock` uses `ModelId` on Amazon Bedrock. New AWS accounts can start with every Bedrock quota at 0. If calls fail with `Too many tokens per day`, use `anthropic` until AWS raises the quota.
- `AnthropicModel` (default `claude-opus-5-5`).
- `ModelId` (default `us.amazon.nova-lite-v1:0`): any Bedrock model or inference profile that supports tool use.
- `SURE_ENOUGH`, `LIKELY_NOTHING`, `LIKELY_PROMISE` in [src/policy.py](src/policy.py).
- The agent's instructions are `SYSTEM_PROMPT` in [src/agent.py](src/agent.py).
- The Jev questions are in [src/jev.py](src/jev.py).

## Color your own agent

```bash
make color                    # the sample outreach steps
make color FILE=my-steps.txt  # your steps, one per line
```

Jev labels each step as decide, generate or code.

## Cost and cleanup

At demo scale, Lambda, Step Functions, DynamoDB and SES usage should cost a few cents or less. Bedrock bills per token. Jev bills separately. Set an AWS Budgets alert before you start.

```bash
make teardown   # deletes the SSM parameter, then the stack. The SES identity stays.
```
