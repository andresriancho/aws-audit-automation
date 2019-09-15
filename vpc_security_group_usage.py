import os
import json
import sys

import boto3

from utils.json_printer import json_printer
from utils.session import get_session


def main():
    session = get_session()

    ec2_client = session.client('ec2', region_name='us-east-1')
    
    filters = [{'Name': 'group-id',
                'Values': ['sg-04d318977c82abb58']}]
    result = ec2_client.describe_network_interfaces(Filters=filters)

    result.pop('ResponseMetadata')

    json_printer(result)


if __name__ == '__main__':
    main()
