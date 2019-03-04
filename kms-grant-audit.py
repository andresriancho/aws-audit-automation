import datetime
import boto3
import json


def get_all_regions():
    all_regions = []
    client = boto3.client('ec2')

    for region in client.describe_regions()['Regions']:
        all_regions.append(region['RegionName'])

    all_regions.sort()
    return all_regions


def get_keys_for_region(client):
    client = boto3.client('kms', region_name=region)
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


def default(o):
    if type(o) is datetime.date or type(o) is datetime.datetime:
        return o.isoformat()


if __name__ == '__main__':
    all_regions = get_all_regions()
    all_data = {}

    for region in all_regions:
        all_data[region] = {}
        client = boto3.client('kms', region_name=region)

        keys_for_region = get_keys_for_region(client)
        for key in keys_for_region:
            print('Region: %s / KeyId: %s' % (region, key))

            grants = []
            policies = []

            try:
                grants = get_key_grants(client, key)
            except Exception, e:
                msg = 'Failed to retrieve grants for %s @ %s. Error: "%s"'
                args = (key, region, e)
                print(msg % args)

            try:
                policies = get_key_policies(client, key)
            except Exception, e:
                msg = 'Failed to retrieve policies for %s @ %s. Error: "%s"'
                args = (key, region, e)
                print(msg % args)

            all_data[region][key] = {}
            all_data[region][key]['grants'] = grants
            all_data[region][key]['policies'] = policies

    data_str = json.dumps(all_data,
                          indent=4,
                          sort_keys=True,
                          default=default)

    file('key-grants.json', 'w').write(data_str)
