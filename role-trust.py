import os
import json

import boto3

from utils.session import get_session
from utils.regions import get_all_regions
from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer


def get_role_names(client):
    paginator = client.get_paginator('list_roles')
    page_iterator = paginator.paginate(MaxItems=200)
    
    for page in page_iterator:
        for role in page['Roles']:
            yield role['RoleName']


def get_role_details(client, role_name):
    role = client.get_role(RoleName=role_name)['Role']
    return role


def main():
    session = get_session()

    all_data = {}

    client = session.client('iam')

    for role_name in get_role_names(client):
        print('RoleName: %s' % (role_name,))
        
        roles = []

        try:
            role_details = get_role_details(client, role_name)
        except Exception as e:
            msg = 'Failed to retrieve role for %s. Error: "%s"'
            args = (role_name, e)
            print(msg % args)

        all_data[role_name] = role_details

    os.makedirs('output', exist_ok=True)
    json_writer('output/role-details.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()
