import argparse
import boto3
import sys


def get_session():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--profile',
        help='AWS profile from ~/.aws/credentials',
        required=False,
        default='default'
    )
    
    args = parser.parse_args()

    try:
        session = boto3.Session(profile_name=args.profile)
    except Exception as e:
        print('%s' % e)
        sys.exit(1)

    return session
