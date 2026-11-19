import json
import os
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache'
LEADS = json.loads((ROOT / 'seed' / 'leads.json').read_text())
STACK = os.environ.get('STACK', 'beyond-llms-outreach')


def describe_stack():
    stack = boto3.client('cloudformation').describe_stacks(StackName=STACK)['Stacks'][0]
    outputs = {o['OutputKey']: o['OutputValue'] for o in stack['Outputs']}
    parameters = {p['ParameterKey']: p['ParameterValue'] for p in stack['Parameters']}
    return outputs, parameters


def pick_leads(lead_ids):
    return [lead for lead in LEADS if not lead_ids or lead['id'] in lead_ids]


# Live calls save what they got, so the demo can replay it when the venue Wi-Fi fails.
def cached(name, fetch_fresh):
    file = CACHE / f'{name}.json'
    try:
        fresh = fetch_fresh()
    except Exception:
        if not file.exists():
            raise
        print(f'  (offline, replaying {file.relative_to(ROOT)})')
        return json.loads(file.read_text())
    CACHE.mkdir(exist_ok=True)
    file.write_text(json.dumps(fresh, indent=2))
    return fresh


def describe(receipt):
    if 'intent' not in receipt:
        return '-'
    intent = receipt['intent']
    text = f'{intent["choice"]:<8} {intent["confidence"]:>4.0%}'
    if 'promises' in receipt:
        text += f'   promises {receipt["promises"]:>4.0%}'
    return text
