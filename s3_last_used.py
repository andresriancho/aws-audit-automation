"""
Identify when an S3 bucket was last used. This script helps identify S3 buckets
which can be removed from the AWS account because nobody is using them.

An S3 bucket is considered as used when there are calls to:
    * PutObject
    * GetObject
    * ListObjects

This script is different from the others in this repository because it has a
lot of external dependencies and manual steps that need to be done before
running it.

Requirements

    1. Enable CloudTrail logging to an S3 bucket

    2. Enable S3 detailed logging in CloudTrail to get the data API calls

    3. Run cloudtrail-partitioner [0], no need to install the CDK application in
       the account, just run the tool to get 90 day visibility in Athena.

    4. Use Athena to query the events and download the result as CSV. Use the
       this Athena query [1] to get all the data from the previously created
       partitions. Make sure you adjust the dates.

    5. Run this tool

[0] https://github.com/duo-labs/cloudtrail-partitioner/
[1] https://gist.github.com/andresriancho/2a85070593d70f48430ea132e08c1ad9
"""
import os
import sys
import csv
import json
import argparse
import boto3

from dateutil.parser import parse
from datetime import datetime, timezone
from tqdm import tqdm

from utils.boto_error_handling import yield_handling_errors


DEFAULT_DATE = datetime(1970, 1, 1, tzinfo=timezone.utc)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--input',
        help='Athena-generated CSV file',
        required=True
    )

    parser.add_argument(
        '--profile',
        help='AWS profile from ~/.aws/credentials',
        required=True
    )

    args = parser.parse_args()

    try:
        session = boto3.Session(profile_name=args.profile)
    except Exception as e:
        print('%s' % e)
        sys.exit(1)

    csv_file = args.input

    if not os.path.exists(csv_file):
        print('%s is not a file' % csv_file)
        sys.exit(1)

    return csv_file, session


class S3Data(object):
    def __init__(self, event_time, request_parameters, aws_region, event_source):
        self.event_time = event_time
        self.request_parameters = request_parameters
        self.aws_region = aws_region
        self.event_source = event_source


def parse_csv(csv_file):
    s3_last_used_data = dict()

    with open(csv_file, newline='') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader, None)

        for row in tqdm(reader):
            (event_time, event_name, request_parameters, aws_region, event_source, resources) = row
            request_parameters = json.loads(request_parameters)
            event_time = parse(event_time)

            bucket_name = request_parameters['bucketName']

            if bucket_name in s3_last_used_data:
                # Might need to update the last used time
                if event_time > s3_last_used_data[bucket_name].event_time:
                    s3_last_used_data[bucket_name] = S3Data(event_time,
                                                            request_parameters,
                                                            aws_region,
                                                            event_source)
            else:
                # New lambda function
                s3_last_used_data[bucket_name] = S3Data(event_time,
                                                        request_parameters,
                                                        aws_region,
                                                        event_source)

    return s3_last_used_data


def sort_key(item):
    return item[1]


def print_output(s3_last_used_data):
    data = []

    for bucket_name, s3_data in s3_last_used_data.items():
        item = (bucket_name, s3_data.event_time,)
        data.append(item)

    data.sort(key=sort_key, reverse=True)

    for bucket_name, event_time in data:
        if event_time is DEFAULT_DATE:
            msg = '%s NOT used during the tracking period'
            args = (bucket_name,)
            print(msg % args)

        else:
            days_ago = datetime.now() - event_time.replace(tzinfo=None)
            days_ago = days_ago.days

            msg = '%s was last used %s days ago'
            args = (bucket_name, days_ago)
            print(msg % args)


def get_all_buckets(session):
    client = session.client('s3')
    response = client.list_buckets()

    for bucket in response['Buckets']:
        yield bucket['Name']


def dump_s3_buckets(session):
    all_s3_buckets = []

    iterator = yield_handling_errors(get_all_buckets, session)

    for bucket_name in iterator:
        all_s3_buckets.append(bucket_name)

    return all_s3_buckets


def merge_all_buckets(s3_last_used_data, all_s3_buckets):
    for bucket_name in all_s3_buckets:
        if bucket_name not in s3_last_used_data:
            s3_last_used_data[bucket_name] = S3Data(DEFAULT_DATE,
                                                    None,
                                                    None,
                                                    None)

    return s3_last_used_data


def main():
    csv_file, session = parse_arguments()

    print('Getting all existing S3 buckets...')
    all_s3_buckets = dump_s3_buckets(session)

    print('Parsing CSV file...')
    s3_last_used_data = parse_csv(csv_file)

    s3_last_used_data = merge_all_buckets(s3_last_used_data, all_s3_buckets)

    print('')
    print('Result:')
    print('')
    print_output(s3_last_used_data)


if __name__ == '__main__':
    main()
