import os
import sys

import boto3

import crm
from common import describe_stack

if 'TYPESAFE_API_KEY' not in os.environ:
    sys.exit('Set TYPESAFE_API_KEY first. Get one at https://console.typesafe.ai/keys')

outputs, parameters = describe_stack()

boto3.client('ssm').put_parameter(
    Name=parameters['JevKeyParam'],
    Value=os.environ['TYPESAFE_API_KEY'],
    Type='SecureString',
    Overwrite=True,
)
print(f'Jev key stored in {parameters["JevKeyParam"]}')

if parameters['ModelProvider'] == 'anthropic':
    if 'ANTHROPIC_API_KEY' not in os.environ:
        sys.exit(
            'ModelProvider is anthropic. Set ANTHROPIC_API_KEY, or deploy with ModelProvider=bedrock.'
        )
    boto3.client('ssm').put_parameter(
        Name=parameters['AnthropicKeyParam'],
        Value=os.environ['ANTHROPIC_API_KEY'],
        Type='SecureString',
        Overwrite=True,
    )
    print(f'Anthropic key stored in {parameters["AnthropicKeyParam"]}')

ses = boto3.client('sesv2')
email = parameters['AeEmail']
try:
    verified = ses.get_email_identity(EmailIdentity=email)['VerifiedForSendingStatus']
except ses.exceptions.NotFoundException:
    ses.create_email_identity(EmailIdentity=email)
    verified = False
print(f'{email} verified' if verified else f'Click the link AWS sent to {email}, then run again')

with boto3.resource('dynamodb').Table(outputs['CrmTable']).batch_writer() as batch:
    for item in crm.seed_items():
        batch.put_item(Item=item)
print(f'CRM seeded into {outputs["CrmTable"]}')
