import json
import os

import boto3


def save(state):
    _table().update_item(
        Key={'leadId': state['lead']['id']},
        UpdateExpression='SET #s = :s',
        ExpressionAttributeNames={'#s': 'state'},
        ExpressionAttributeValues={':s': json.dumps(state)},
    )


def save_approval(lead_id, token, code):
    _table().update_item(
        Key={'leadId': lead_id},
        UpdateExpression='SET taskToken = :t, code = :c',
        ExpressionAttributeValues={':t': token, ':c': code},
    )


def get(lead_id):
    return _table().get_item(Key={'leadId': lead_id}).get('Item')


def list_states():
    return [json.loads(item['state']) for item in _table().scan()['Items']]


def decide(item, approved):
    state = json.loads(item['state'])
    state['receipt']['decision'] = 'approve' if approved else 'reject'
    boto3.client('stepfunctions').send_task_success(
        taskToken=item['taskToken'], output=json.dumps(state)
    )
    _table().update_item(Key={'leadId': item['leadId']}, UpdateExpression='REMOVE taskToken, code')


def _table():
    return boto3.resource('dynamodb').Table(os.environ['RUNS_TABLE'])
