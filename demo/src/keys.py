import os
from functools import cache

import boto3


# Locally the key comes from the environment. In Lambda it comes from an SSM SecureString.
@cache
def read(env_var, param_env_var):
    if key := os.environ.get(env_var):
        return key
    parameter = boto3.client('ssm').get_parameter(
        Name=os.environ[param_env_var], WithDecryption=True
    )
    return parameter['Parameter']['Value']
