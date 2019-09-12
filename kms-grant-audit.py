import os
import json

import boto3

from utils.session import get_session
from utils.regions import get_all_regions
from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer


def get_keys_for_region(client):
    region_keys = client.list_keys(Limit=1000)['Keys']
    return [k['KeyId'] for k in region_keys]


def get_key_grants(client, key_id):
    grants = client.list_grants(KeyId=key_id)['Grants']
    return grants


def get_key_policies(client, key_id):
    policies = []

    for policy in client.list_key_policies(KeyId=key_id)['PolicyNames']:
        policy_json = client.get_key_policy(KeyId=key_id, PolicyName=policy)
        policy_json = json.loads(policy_json['Policy'])
        policies.append(policy_json)

    return policies


def main():
    session = get_session()

    all_data = {}

    for region in get_all_regions(session):
        all_data[region] = {}
        client = session.client('kms', region_name=region)

        keys_for_region = get_keys_for_region(client)

        if not keys_for_region:
            print('Region: %s / No KMS keys' % region)
            continue

        for key in keys_for_region:
            print('Region: %s / KeyId: %s' % (region, key))

            grants = []
            policies = []

            try:
                grants = get_key_grants(client, key)
            except Exception as e:
                msg = 'Failed to retrieve grants for %s @ %s. Error: "%s"'
                args = (key, region, e)
                print(msg % args)

            try:
                policies = get_key_policies(client, key)
            except Exception as e:
                msg = 'Failed to retrieve policies for %s @ %s. Error: "%s"'
                args = (key, region, e)
                print(msg % args)

            all_data[region][key] = {}
            all_data[region][key]['grants'] = grants
            all_data[region][key]['policies'] = policies

    os.makedirs('output', exist_ok=True)
    json_writer('output/key-grants.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()
