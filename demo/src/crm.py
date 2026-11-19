import json
import os
from pathlib import Path

import boto3
from boto3.dynamodb.conditions import Key

# With no table configured, the CRM reads the seed file so the demo runs without deploying.
# Profiles and activity are stored as JSON strings because DynamoDB returns numbers as Decimal.
SEED_FILE = Path(__file__).resolve().parent.parent / 'seed' / 'crm.json'


def find_contact(email):
    if table := _table():
        return table.get_item(Key={'pk': f'CONTACT#{email}', 'sk': 'CONTACT'}).get('Item')
    return next((c for a in _seed() for c in _contacts(a) if c['email'] == email), None)


def get_account(account_id):
    if table := _table():
        item = table.get_item(Key={'pk': f'ACCOUNT#{account_id}', 'sk': 'PROFILE'})['Item']
        return json.loads(item['profile'])
    return next(_profile(a) for a in _seed() if a['id'] == account_id)


def get_activity(account_id, limit=5):
    if table := _table():
        items = table.query(
            KeyConditionExpression=Key('pk').eq(f'ACCOUNT#{account_id}')
            & Key('sk').begins_with('ACTIVITY#'),
            ScanIndexForward=False,
            Limit=limit,
        )['Items']
        return [json.loads(item['activity']) for item in items]
    account = next(a for a in _seed() if a['id'] == account_id)
    return sorted(account['activity'], key=lambda a: a['date'], reverse=True)[:limit]


def seed_items():
    for account in _seed():
        yield {
            'pk': f'ACCOUNT#{account["id"]}',
            'sk': 'PROFILE',
            'profile': json.dumps(_profile(account)),
        }
        for contact in _contacts(account):
            yield {'pk': f'CONTACT#{contact["email"]}', 'sk': 'CONTACT', **contact}
        for activity in account['activity']:
            yield {
                'pk': f'ACCOUNT#{account["id"]}',
                'sk': f'ACTIVITY#{activity["date"]}',
                'activity': json.dumps(activity),
            }


def _table():
    name = os.environ.get('CRM_TABLE')
    return boto3.resource('dynamodb').Table(name) if name else None


def _seed():
    return json.loads(SEED_FILE.read_text())['accounts']


def _contacts(account):
    return [{**c, 'accountId': account['id']} for c in account['contacts']]


def _profile(account):
    return {k: v for k, v in account.items() if k not in ('contacts', 'activity')}
