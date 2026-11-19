import boto3

from common import describe_stack

_, parameters = describe_stack()
ssm = boto3.client('ssm')
for name in (parameters['JevKeyParam'], parameters['AnthropicKeyParam']):
    try:
        ssm.delete_parameter(Name=name)
        print(f'Deleted {name}')
    except ssm.exceptions.ParameterNotFound:
        pass
print(f'The SES identity {parameters["AeEmail"]} stays.')
