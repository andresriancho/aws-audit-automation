import boto3

# Enable logging
# boto3.set_stream_logger(name='botocore')

client = boto3.client('cognito-identity', region_name='us-east-1')

_id = client.get_id(IdentityPoolId='us-east-1:XXXXXX-XXXXXXXXX-XXXXXXX-XXXXXX')
_id = _id['IdentityId']
print(_id)

print client.get_credentials_for_identity(IdentityId=_id)
