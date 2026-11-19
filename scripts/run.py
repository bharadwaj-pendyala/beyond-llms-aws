import json
import sys
import time

import boto3

from common import describe_stack, pick_leads

outputs, _ = describe_stack()
sfn = boto3.client('stepfunctions')
region = sfn.meta.region_name

for lead in pick_leads(sys.argv[1:]):
    execution = sfn.start_execution(
        stateMachineArn=outputs['StateMachineArn'],
        name=f'{lead["id"]}-{int(time.time())}',
        input=json.dumps({'lead': lead}),
    )
    console = f'https://{region}.console.aws.amazon.com/states/home?region={region}'
    print(f'{lead["id"]}  {console}#/v2/executions/details/{execution["executionArn"]}')
