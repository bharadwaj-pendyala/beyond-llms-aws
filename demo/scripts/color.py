import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import jev

KINDS = {
    'decide': 'The answer is one item from a short list you could write down today, '
    'such as a team, yes or no, or a level.',
    'generate': 'The answer is new text, such as a reply, a summary, or code.',
    'code': 'Plain code can do it with no model, such as a lookup, a calculation, or an API call.',
}

SAMPLE_STEPS = [
    'Check the do-not-contact list',
    'Work out what the lead is asking for',
    'Decide if the lead is worth an email',
    'Look up the account in the CRM',
    'Write the follow-up email',
    'Check if the email promises a discount or a date',
    'Decide whether to send it or ask the account executive',
]


def color(step):
    answers = jev.ask(
        {'step': step},
        {
            'kind': {
                'type': 'choice',
                'instructions': 'An AI agent runs this `step`. What kind of work is it?',
                'criteria': KINDS,
            }
        },
    )
    return answers['kind']


steps = Path(sys.argv[1]).read_text().splitlines() if len(sys.argv) > 1 else SAMPLE_STEPS
steps = [step for step in steps if step.strip()]

with ThreadPoolExecutor() as pool:
    kinds = list(pool.map(color, steps))

for step, kind in zip(steps, kinds):
    print(f'{kind["choice"].upper():<8} {kind["confidence"]:>4.0%}  {step}')

decisions = sum(kind['choice'] == 'decide' for kind in kinds)
print(f'\n{decisions} of {len(steps)} steps are decisions.')
