import os
from urllib.parse import urlencode

import boto3


# The seed leads have fictional addresses, so follow-ups go to CUSTOMER_EMAIL.
# The AE gets a blind copy, so the demo shows every sent email in one inbox.
def send_followup(state):
    draft = state['receipt']['draft']
    _send(
        to=os.environ['CUSTOMER_EMAIL'],
        subject=f'{draft["subject"]} [lead: {state["lead"]["email"]}]',
        body=draft['body'],
        bcc=os.environ['AE_EMAIL'],
    )


def send_approval_request(state, code):
    lead, receipt = state['lead'], state['receipt']
    link = f'{os.environ["APPROVE_URL"]}?' + urlencode({'lead': lead['id'], 'code': code})
    intent = receipt['intent']
    body = f"""Jev was not sure enough to send this one on its own.

Intent: {intent['choice']} ({intent['confidence']:.0%} sure)
Jev's split: {_split(intent['probabilities'])}
Promises something: {receipt['promises']:.0%}

Approve: {link}&decision=approve
Reject:  {link}&decision=reject

---
To: {lead['email']}
Subject: {receipt['draft']['subject']}

{receipt['draft']['body']}
"""
    _send(
        to=os.environ['AE_EMAIL'],
        subject=f'[approve?] {lead["id"]} {receipt["draft"]["subject"]}',
        body=body,
    )


def _split(probabilities):
    ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
    return ', '.join(f'{label} {p:.0%}' for label, p in ranked if p >= 0.05)


def _send(to, subject, body, bcc=None):
    boto3.client('sesv2').send_email(
        FromEmailAddress=os.environ['AE_EMAIL'],
        Destination={'ToAddresses': [to], 'BccAddresses': [bcc] if bcc else []},
        Content={'Simple': {'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body}}}},
    )
