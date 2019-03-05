#!/bin/python

"""
Calls these (from boto) to get an idea of who's behind a set of credentials

    aws sts get-caller-identity
    aws iam get-account-authorization-details
    aws iam list-attached-user-policies --user-name=...
    aws iam list-groups-for-user --user-name=...
    aws iam list-attached-group-policies --group-name ...
"""
import boto3

from utils.json_writer import json_writer
from utils.json_printer import json_printer
from utils.remove_metadata import remove_metadata
from utils.get_user_name import get_principal_name


def get_policy(policy_arn):
    iam_client = boto3.client('iam')

    policy = iam_client.get_policy(
        PolicyArn=policy_arn
    )

    policy_version = iam_client.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=policy['Policy']['DefaultVersionId']
    )

    output = dict()
    output['document'] = policy_version['PolicyVersion']['Document']
    output['statement'] = policy_version['PolicyVersion']['Document']['Statement']
    return output


def main():
    output = {}

    sts_client = boto3.client('sts')
    sts_data = sts_client.get_caller_identity()
    sts_data = remove_metadata(sts_data)

    output['sts'] = sts_data

    principal_type, name = get_principal_name(sts_data)

    json_writer('whoami.json', output)
    json_printer(output)


if __name__ == '__main__':
    main()
