#
# Find which principals can run a specific API method:
#
#     python iam_simulate_action.py lambda:GetFunction
#
import os
import sys
import json
import itertools

import boto3

from utils.session import get_session
from utils.regions import get_all_regions
from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer


def get_users(client):
    """
    :return: ARN for all IAM users
    """
    return [u['Arn'] for u in client.list_users(MaxItems=1000)['Users']]


def get_groups(client):
    """
    :return: ARN for all IAM groups
    """
    return [g['Arn'] for g in client.list_groups(MaxItems=1000)['Groups']]


def get_roles(client):
    """
    :return: ARN for all IAM roles
    """
    return [r['Arn'] for r in client.list_roles(MaxItems=1000)['Roles']]


def main():
    session = get_session()
    actions = [
        'sts:AssumeRole'
    ]

    iam_client = session.client('iam')

    all_principals = itertools.chain(
        get_users(iam_client),
        get_groups(iam_client),
        get_roles(iam_client),
    )

    allowed_principals = []

    for principal in all_principals:
        evaluation_result = iam_client.simulate_principal_policy(
            PolicySourceArn=principal,
            ActionNames=actions
        )
        
        if evaluation_result['EvaluationResults'][0]['EvalDecision'] == 'allowed':
            allowed_principals.append(principal)
            sys.stdout.write('A')
            sys.stdout.flush()
        else:
            sys.stdout.write('.')
            sys.stdout.flush()

    print('\n')

    print('These principals are allowed to %s:' % actions)
    print('\n'.join([' - %s' % ap for ap in allowed_principals]))

if __name__ == '__main__':
    main()
