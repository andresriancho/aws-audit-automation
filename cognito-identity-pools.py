import datetime
import boto3
import json
import sys


from botocore.exceptions import EndpointConnectionError


def get_all_regions():
    client = boto3.client('ec2')

    for region in client.describe_regions()['Regions']:
        yield region['RegionName']


def get_id_pools(client):  
    try:
        id_pools = client.list_identity_pools(MaxResults=60)['IdentityPools']
    except EndpointConnectionError:
        print('Cognito is not supported in this region')
        return
    
    for id_pool in id_pools:
        yield id_pool


def default(o):
  if type(o) is datetime.date or type(o) is datetime.datetime:
    return o.isoformat()


if __name__ == '__main__':
    all_data = {}
    

    for region in get_all_regions():
        all_data[region] = {}
        client = boto3.client('cognito-identity', region_name=region)

        print('Processing region: %s' % region)

        for i, id_pool in enumerate(get_id_pools(client)):
            id_pool_id = id_pool['IdentityPoolId']

            id_pool = client.describe_identity_pool(IdentityPoolId=id_pool_id)
            pool_roles = client.get_identity_pool_roles(IdentityPoolId=id_pool_id)

            all_data[region][id_pool_id] = {}
            all_data[region][id_pool_id]['describe'] = id_pool
            all_data[region][id_pool_id]['roles'] = pool_roles

            sys.stdout.write('.')
            sys.stdout.flush()


    data_str = json.dumps(all_data,
                          indent=4,
                          sort_keys=True,
                          default=default)

    file('id_pools.json', 'w').write(data_str)