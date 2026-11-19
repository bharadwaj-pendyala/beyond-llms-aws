import secrets
import time

import agent
import crm
import jev
import mail
import runs
from policy import route


def check_rules(state):
    contact = crm.find_contact(state['lead']['email'])
    blocked = bool(contact and contact['doNotContact'])
    return {**state, 'receipt': {'route': 'blocked' if blocked else 'allowed'}}


def decide_intent(state):
    receipt = {**state['receipt'], 'intent': jev.ask_intent(state['lead']['note'])}
    return {**state, 'receipt': {**receipt, 'route': route(receipt)}}


def write_draft(state):
    draft = agent.write_draft(state['lead'], state['receipt']['intent']['choice'])
    return {**state, 'receipt': {**state['receipt'], 'draft': draft}}


def check_draft(state):
    draft = state['receipt']['draft']
    receipt = {
        **state['receipt'],
        'promises': jev.ask_promises(f'{draft["subject"]}\n\n{draft["body"]}'),
    }
    return {**state, 'receipt': {**receipt, 'route': route(receipt)}}


def send(state):
    mail.send_followup(state)
    return {**state, 'receipt': {**state['receipt'], 'route': 'sent'}}


STEPS = {
    'check_rules': check_rules,
    'decide_intent': decide_intent,
    'write_draft': write_draft,
    'check_draft': check_draft,
    'send': send,
}


def run_step(name, state):
    started = time.perf_counter()
    state = STEPS[name](state)
    state['receipt'].setdefault('ms', {})[name] = round((time.perf_counter() - started) * 1000)
    return state


def handler(event, _context):
    if event['step'] == 'request_approval':
        return request_approval(event['state'], event['token'])

    state = run_step(event['step'], event['state'])
    runs.save(state)
    return state


def request_approval(state, token):
    code = secrets.token_urlsafe(12)
    runs.save_approval(state['lead']['id'], token, code)
    mail.send_approval_request(state, code)
    return {'waitingFor': 'approval'}
