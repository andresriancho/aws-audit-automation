import datetime
import boto3
import json


def get_role_names(client):
    paginator = client.get_paginator('list_roles')
    page_iterator = paginator.paginate(MaxItems=200)
    
    for page in page_iterator:
        for role in page['Roles']:
            yield role['RoleName']


def get_role_details(client, role_name):
    role = client.get_role(RoleName=role_name)['Role']
    return role


def default(o):
  if type(o) is datetime.date or type(o) is datetime.datetime:
    return o.isoformat()


if __name__ == '__main__':
    all_data = {}

    client = boto3.client('iam')

    for role_name in get_role_names(client):
        print('RoleName: %s' % (role_name,))
        
        roles = []

        try:
            role_details = get_role_details(client, role_name)
        except Exception, e:
            msg = 'Failed to retrieve role for %s. Error: "%s"'
            args = (role_name, e)
            print(msg % args)

        all_data[role_name] = role_details

    data_str = json.dumps(all_data,
                          indent=4,
                          sort_keys=True,
                          default=default)

    file('role-details.json', 'w').write(data_str)
