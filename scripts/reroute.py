import os
import sys

import runs
from common import cached, describe, describe_stack
from policy import SURE_ENOUGH, route


def fetch_states():
    if '--local' in sys.argv:
        raise RuntimeError('Reading the last local run')
    os.environ['RUNS_TABLE'] = describe_stack()[0]['RunsTable']
    return runs.list_states()


threshold = float(next((arg for arg in sys.argv[1:] if not arg.startswith('--')), SURE_ENOUGH))
states = sorted(cached('receipts', fetch_states), key=lambda s: s['lead']['id'])

print(f'Same Jev answers, no new model calls. Threshold {SURE_ENOUGH} → {threshold}\n')
for state in states:
    receipt = state['receipt']
    if 'intent' not in receipt:
        print(f'{state["lead"]["id"]}  {describe(receipt):<36} {receipt["route"]}')
        continue
    before, after = route(receipt), route(receipt, sure_enough=threshold)
    changed = '   ← changed' if before != after else ''
    print(f'{state["lead"]["id"]}  {describe(receipt):<36} {before:>7} → {after}{changed}')
