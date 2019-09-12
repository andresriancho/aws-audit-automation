import os
import sys
import boto3

from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer
from utils.session import get_session
from utils.regions import get_all_regions
from botocore.exceptions import EndpointConnectionError


def get_id_pools(client):  
    try:
        id_pools = client.list_identity_pools(MaxResults=60)['IdentityPools']
    except EndpointConnectionError:
        print('Cognito is not supported in this region')
        return
    
    for id_pool in id_pools:
        yield id_pool

def main():
    session = get_session()

    all_data = {}

    for region in get_all_regions(session):
        all_data[region] = {}
        client = session.client('cognito-identity', region_name=region)

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

    os.makedirs('output', exist_ok=True)
    json_writer('output/cognito-id-pools.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()
