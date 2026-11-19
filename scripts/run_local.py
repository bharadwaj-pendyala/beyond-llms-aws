import sys
from functools import partial

from app import run_step
from common import cached, describe, pick_leads

PIPELINE = ['check_rules', 'decide_intent', 'write_draft', 'check_draft']
FINISHED = {'blocked', 'skip'}


def run(lead):
    state = {'lead': lead}
    for step in PIPELINE:
        state = cached(f'{lead["id"]}-{step}', partial(run_step, step, state))
        if state['receipt']['route'] in FINISHED:
            break
    return state


states = [run(lead) for lead in pick_leads(sys.argv[1:])]
cached('receipts', lambda: states)

for state in states:
    receipt = state['receipt']
    ms = '  '.join(f'{step} {ms}ms' for step, ms in receipt.get('ms', {}).items())
    print(f'{state["lead"]["id"]}  {describe(receipt):<36} → {receipt["route"]:<8} {ms}')
    if draft := receipt.get('draft'):
        print(f'      {draft["subject"]}')
