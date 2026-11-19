# beyond-llms-aws

Demo code from my talk "Beyond LLMs: Decision Models for Smarter AI Agents" at AWS User Group DFW, Nov 19, 2026. The slides are at [bharad.dev/talks](https://bharad.dev/talks).

Here's the agent. Someone stops by a conference booth, a rep types a one-line note, and the agent writes the follow-up email for the account executive (AE). The interesting part isn't the email. It's everything around it: most steps in this agent pick from a short list, and an LLM is the wrong tool for picking from a list.

So the agent asks [Jev](https://typesafe.ai), a decision model, two questions. One before the draft: what does this person want? One after: does the draft promise something we can't give? Jev answers from a fixed list, with a probability for every option, in a fifth of a second or less. Then one Python function decides what happens next. Not the model.

## How a lead moves

```
booth note
  → do-not-contact?          code. A hard rule is an if, not a model call.
  → what do they want?       Jev. meeting, pricing, info or unclear, each with a probability.
  → write the draft          Strands agent with two tools: lookup_account, recent_activity.
  → promises anything?       Jev. Probability that the draft promises a discount, date or feature.
  → send, ask the AE, or drop it
```

Step Functions runs those steps. Each one is a call to the same Lambda function, and every call writes a receipt to DynamoDB. When the code isn't sure, the state machine pauses on `waitForTaskToken` and emails the AE an approve link. Nothing moves until they click it.

The whole policy fits on one screen, in [src/policy.py](src/policy.py):

```python
def route(receipt, sure_enough=SURE_ENOUGH):
    intent = receipt['intent']
    unclear = intent['probabilities']['unclear']
    if intent['choice'] == 'unclear' or unclear >= LIKELY_NOTHING:
        return 'skip'
    if 'promises' not in receipt:
        return 'draft'
    if intent['confidence'] < sure_enough or receipt['promises'] >= LIKELY_PROMISE:
        return 'approve'
    return 'send'
```

Look at the first check. My first version skipped anything Jev was less than 50% sure about, and it dropped the best lead in the seed data. That lead asked about price *and* a call, so Jev split it 62/38. Split isn't the same as empty. Jev returns a probability for every option, so the rule now skips only when "unclear" has a real share, and sends a split lead to a person.

## The five seed leads

| Lead | The note | What happens |
| --- | --- | --- |
| L-1 | Wants Team plan pricing before a Q1 budget review | Jev is sure, the draft is clean, it's sent |
| L-2 | Can we beat their vendor's price, and does SSO ship before March? | Pricing 62%, meeting 38%. The AE approves it. |
| L-3 | Grabbed a sticker and a t-shirt | "Unclear" gets 43%. No email. |
| L-4 | Wants a call, but opted out of sales email | Blocked by the rule. Jev is never asked. |
| L-5 | Wants 30 minutes with a solutions engineer | Jev is sure, it's sent |

Those numbers come from my runs. Yours will move a little, because Jev's confidence varies between runs.

## Run it on your laptop first

You need Python 3.13+, [uv](https://docs.astral.sh/uv/), a [TypeSafe API key](https://console.typesafe.ai/keys) and an [Anthropic API key](https://console.anthropic.com). Nothing gets deployed. The CRM reads `seed/crm.json`.

```bash
cp .env.example .env     # then fill in both keys
make test
make local               # all five leads
make local LEADS="L-2"   # just one
make reroute T=0.45 LOCAL=1
```

`make reroute` is my favorite part. It reruns only the policy against the saved receipts, at whatever threshold you give it. No calls to Jev, no calls to the model. Drop the line to 0.45 and watch L-2 go out without anyone looking at it. Whether that's OK is a product call, and it's one constant in your code.

Every live call is cached in `.cache/`. If the network dies, the scripts replay the last answer and say so.

## Deploy it to AWS

Add the [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) and an inbox you can read. That inbox plays the AE.

```bash
make deploy        # asks for AeEmail and the rest, saves answers to samconfig.toml
make setup         # keys into Parameter Store, SES verification email, CRM seed
```

Click the link SES sends you, then:

```bash
make run                 # one Step Functions execution per lead, prints console links
make logs                # tail the Lambda
make approve LEAD=L-2    # same as clicking the email link
make reroute T=0.45      # reroute what actually ran in AWS
```

The stack is Step Functions, two Lambda functions (one behind a function URL for the approve link), two DynamoDB tables, SES and two SecureString parameters. It's one SAM template, [template.yaml](template.yaml).

SES starts in sandbox mode, so follow-ups go to `CustomerEmail`, which defaults to the SES mailbox simulator. The lead's real address is in the subject line. The AE gets a blind copy of everything, so the whole demo shows up in one inbox.

## A note on Bedrock

The agent is built with [Strands](https://strandsagents.com), and the model is one setting, `ModelProvider`. Set it to `bedrock` and it runs on Amazon Nova through Bedrock, in your own account, with Lambda signing in by its IAM role.

I meant to run the talk on Bedrock. My AWS account was brand new, and every Bedrock quota on it was 0. The first call failed with `Too many tokens per day`. Service Quotas couldn't fix it: two of the limits aren't adjustable, and the third only takes requests above its default. That leaves a support case, and people report waiting days or weeks. So the default is `anthropic`: Claude through the Anthropic API, with the key in Parameter Store. When your quota is there, switching to Bedrock is a redeploy, not a code change.

If you're on a new account, check this before you start:

```bash
aws service-quotas get-service-quota --service-code bedrock --quota-code L-45E0AD92 \
  --region us-east-1 --query Quota.Value
```

## Change it

- The thresholds: `SURE_ENOUGH`, `LIKELY_NOTHING` and `LIKELY_PROMISE` in [src/policy.py](src/policy.py).
- The questions Jev answers: [src/jev.py](src/jev.py).
- What the agent is told and which tools it has: [src/agent.py](src/agent.py).
- The model: `ModelProvider`, `AnthropicModel` and `ModelId` in [template.yaml](template.yaml).

Want to see how much of your own agent is really decisions? Put its steps in a text file, one per line, and run `make color FILE=steps.txt`. Jev labels each one decide, generate or code.

## Cleanup

```bash
make teardown   # deletes the keys in Parameter Store, then the stack
```

At demo scale the AWS side should cost cents. Claude and Jev bill separately. Set an AWS Budgets alert before you start anyway.
