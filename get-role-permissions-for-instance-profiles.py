import datetime
import boto3
import json
import sys


def get_all_regions():
    client = boto3.client('ec2')

    for region in client.describe_regions()['Regions']:
        yield region['RegionName']


def get_instance_profiles(ec2_client, iam_client):

    paginator = ec2_client.get_paginator('describe_instances')
    
    for page in paginator.paginate():
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                if 'IamInstanceProfile' not in instance:
                    continue
                
                if 'Arn' not in instance['IamInstanceProfile']:
                    continue

                instance_profile_arn = instance['IamInstanceProfile']['Arn']
                instance_profile_name = instance_profile_arn.split('/')[-1]

                instance_profile = iam_client.get_instance_profile(InstanceProfileName=instance_profile_name)['InstanceProfile']
                role_name = instance_profile['Roles'][0]['RoleName']

                role_policies = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
                
                for policy_name in role_policies:
                    response = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                    response['IamInstanceProfile'] = instance_profile_arn
                    response['Instance'] = instance
                    yield response



def default(o):
  if type(o) is datetime.date or type(o) is datetime.datetime:
    return o.isoformat()


if __name__ == '__main__':
    all_data = {}
    iam_client = boto3.client('iam')

    for region in get_all_regions():
        all_data[region] = {}
        ec2_client = boto3.client('ec2', region_name=region)

        print('Processing region: %s' % region)

        for i, instance_profile_policy in enumerate(get_instance_profiles(ec2_client, iam_client)):
            all_data[region][i] = instance_profile_policy
            
            sys.stdout.write('.')
            sys.stdout.flush()

    data_str = json.dumps(all_data,
                          indent=4,
                          sort_keys=True,
                          default=default)

    file('instance_profile_policies.json', 'w').write(data_str)
