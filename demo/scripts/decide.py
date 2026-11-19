import os
import sys

import runs
from common import describe_stack

if len(sys.argv) != 3 or sys.argv[2] not in ('approve', 'reject'):
    sys.exit('Usage: decide.py <lead id> approve|reject')

lead_id, decision = sys.argv[1:]
os.environ['RUNS_TABLE'] = describe_stack()[0]['RunsTable']

item = runs.get(lead_id)
if not item or 'taskToken' not in item:
    sys.exit(f'{lead_id} is not waiting for approval.')

runs.decide(item, decision == 'approve')
print(f'{lead_id}: {decision}d')
