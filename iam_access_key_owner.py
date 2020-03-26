# Find the IAM username belonging to one access key

import argparse
import boto3
import sys

from botocore.exceptions import ClientError


def get_session():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--profile',
        help='AWS profile from ~/.aws/credentials',
        required=False,
        default='default'
    )

    parser.add_argument(
        '--access-key',
        help='AWS IAM access key',
        required=True
    )

    args = parser.parse_args()

    try:
        session = boto3.Session(profile_name=args.profile)
    except Exception as e:
        print('%s' % e)
        sys.exit(1)

    return session, args.access_key


def find_user(session, access_key):
    iam_client = session.client('iam')

    try:
        key_info = iam_client.get_access_key_last_used(AccessKeyId=access_key)
        return key_info['UserName']
    except ClientError as e:
        print("Received error: %s" % e)

        if e.response['Error']['Code'] == 'AccessDenied':
            return "Key does not exist in target account"


def main():
    session, access_key = get_session()

    user = find_user(session, access_key)
    print(user)


if __name__ == '__main__':
    main()
