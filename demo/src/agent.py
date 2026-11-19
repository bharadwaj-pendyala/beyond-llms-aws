import os

from pydantic import BaseModel
from strands import Agent, tool
from strands.models import BedrockModel
from strands.models.anthropic import AnthropicModel

import crm
import keys

SYSTEM_PROMPT = """You write follow-up emails for an account executive after a conference booth visit.
Look up the account and its recent activity before you write.
Write 80 to 120 words in plain language. Refer to what they asked for and to one detail from
their history. Do not repeat material that was already sent. Sign with the account executive's name.
Do not offer discounts, delivery dates, or features that are not already live. Offer a call
with the account executive instead."""


class Email(BaseModel):
    subject: str
    body: str


@tool
def lookup_account(email: str) -> dict:
    """Get the contact's name, company, plan, and account executive for a contact email."""
    contact = crm.find_contact(email)
    if not contact:
        return {'error': f'No contact with email {email}'}
    return {'contactName': contact['name'], **crm.get_account(contact['accountId'])}


@tool
def recent_activity(account_id: str) -> list[dict]:
    """Get the latest emails, meetings, and support tickets for an account, newest first."""
    return crm.get_activity(account_id)


# Bedrock is the target. The Anthropic API is the fallback while this account's Bedrock quota is 0.
def build_model():
    if os.environ.get('MODEL_PROVIDER', 'anthropic') == 'bedrock':
        return BedrockModel(model_id=os.environ.get('MODEL_ID', 'us.amazon.nova-lite-v1:0'))
    return AnthropicModel(
        client_args={'api_key': keys.read('ANTHROPIC_API_KEY', 'ANTHROPIC_KEY_PARAM')},
        model_id=os.environ.get('ANTHROPIC_MODEL', 'claude-opus-5-5'),
        max_tokens=4096,
        params={
            'output_config': {'effort': 'low'},
            'extra_body': {'fallbacks': 'default'},
            'extra_headers': {'anthropic-beta': 'server-side-fallback-2026-07-01'},
        },
    )


def write_draft(lead, intent):
    agent = Agent(
        model=build_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=[lookup_account, recent_activity],
        callback_handler=None,
    )
    prompt = f'Contact email: {lead["email"]}\nThey asked for: {intent}\nBooth note: {lead["note"]}'
    return agent(prompt, structured_output_model=Email).structured_output.model_dump()
