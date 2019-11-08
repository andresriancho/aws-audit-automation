import os
import json
import sys

import boto3

from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer
from utils.session import get_session
from utils.regions import get_all_regions
from utils.boto_error_handling import yield_handling_errors


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



def main():
    session = get_session()

    all_data = {}
    iam_client = session.client('iam')

    for region in get_all_regions(session):
        all_data[region] = {}
        ec2_client = session.client('ec2', region_name=region)

        print('Processing region: %s' % region)

        iterator = yield_handling_errors(get_instance_profiles, ec2_client, iam_client)
        iterator = enumerate(iterator)

        for i, instance_profile_policy in iterator:
            all_data[region][i] = instance_profile_policy
            
            sys.stdout.write('.')
            sys.stdout.flush()

    os.makedirs('output', exist_ok=True)
    json_writer('output/instance_profile_policies.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()
