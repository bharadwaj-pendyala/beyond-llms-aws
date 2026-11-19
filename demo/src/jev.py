import json
import urllib.request

import keys

JEV_URL = 'https://api.typesafe.ai/v1/systemone'

INTENTS = {
    'meeting': 'Wants to talk or book a meeting.',
    'pricing': 'Asks about price, plans, or a quote.',
    'info': 'Wants material to read, a demo, or a case study.',
    'unclear': 'Not enough detail to tell what they want.',
}

PROMISES = 'Does this `draft` promise a discount, a delivery date, or a feature?'


def ask(state, questions):
    request = urllib.request.Request(
        JEV_URL,
        data=json.dumps({'model': 'jev-latest', 'state': state, 'questions': questions}).encode(),
        headers={
            'Authorization': f'Bearer {keys.read("TYPESAFE_API_KEY", "JEV_KEY_PARAM")}',
            'Content-Type': 'application/json',
        },
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)['answers']


def ask_intent(note):
    answers = ask(
        {'note': note},
        {
            'intent': {
                'type': 'choice',
                'instructions': 'What is the person in this booth `note` asking for?',
                'criteria': INTENTS,
            }
        },
    )
    return {key: answers['intent'][key] for key in ('choice', 'confidence', 'probabilities')}


def ask_promises(draft):
    answers = ask({'draft': draft}, {'promises': {'type': 'noul', 'instructions': PROMISES}})
    return answers['promises']['noul']
