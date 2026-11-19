import json
import secrets

import runs


def handler(event, _context):
    params = event.get('queryStringParameters') or {}
    lead_id = params.get('lead', '')
    item = runs.get(lead_id)
    matched = bool(
        item and 'code' in item and secrets.compare_digest(item['code'], params.get('code', ''))
    )
    print(
        json.dumps(
            {
                'lead': lead_id,
                'params': sorted(params),
                'waiting': bool(item and 'code' in item),
                'matched': matched,
            }
        )
    )
    if not matched:
        return {'statusCode': 403, 'body': 'This link is unknown or was already used.'}

    approved = params.get('decision') == 'approve'
    runs.decide(item, approved)
    return {
        'statusCode': 200,
        'body': f'{"Approved" if approved else "Rejected"}. You can close this tab.',
    }
