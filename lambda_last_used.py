"""
Identify when a lambda function was last modified or invoked. This script
helps identify lambda functions which can be removed from the AWS account
because nobody is using them.

This script is different from the others because it has a lot of external
dependencies and manual steps that need to be done before running it.

Requirements

    1. Enable CloudTrail logging to an S3 bucket

    2. Enable Lambda detailed logging in CloudTrail to get the Invoke calls

    3. Run cloudtrail-partitioner [0], no need to install it, just run the tool
       to get 90 day visibility.

    4. Use Athena to query the events and download the result as CSV. Use the
       this Athena query [1] to get all the data from the previously created
       partitions. Make sure you adjust the dates.

    5. Run this tool

[0] https://github.com/duo-labs/cloudtrail-partitioner/
[1] https://gist.github.com/andresriancho/512bfbae1ad8b175a36d6fdc32b8ccef
"""
import os
import sys
import csv
import json
import argparse
import boto3

from dateutil.parser import parse
from datetime import datetime, timezone

from utils.regions import get_all_regions
from lambda_dump import get_lambda_functions_for_region
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


class LambdaData(object):
    def __init__(self, event_time, request_parameters, aws_region, event_source):
        self.event_time = event_time
        self.request_parameters = request_parameters
        self.aws_region = aws_region
        self.event_source = event_source


def parse_csv(csv_file):
    lambda_last_used_data = dict()

    with open(csv_file, newline='') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader, None)

        for row in reader:
            (event_time, event_name, request_parameters, aws_region, event_source, resources) = row
            request_parameters = json.loads(request_parameters)
            event_time = parse(event_time)

            lambda_function_arn = request_parameters['functionName']

            if lambda_function_arn in lambda_last_used_data:
                # Might need to update the last used time
                if event_time > lambda_last_used_data[lambda_function_arn].event_time:
                    lambda_last_used_data[lambda_function_arn] = LambdaData(event_time,
                                                                            request_parameters,
                                                                            aws_region,
                                                                            event_source)
            else:
                # New lambda function
                lambda_last_used_data[lambda_function_arn] = LambdaData(event_time,
                                                                        request_parameters,
                                                                        aws_region,
                                                                        event_source)

    return lambda_last_used_data


def sort_key(item):
    return item[1]


def print_output(lambda_last_used_data):
    data = []

    for lambda_function_arn, lambda_data in lambda_last_used_data.items():
        item = (lambda_function_arn, lambda_data.event_time,)
        data.append(item)

    data.sort(key=sort_key, reverse=True)

    for lambda_function_arn, event_time in data:
        if event_time is DEFAULT_DATE:
            msg = '%s NOT used during the tracking period'
            args = (lambda_function_arn,)
            print(msg % args)

        else:
            days_ago = datetime.now() - event_time.replace(tzinfo=None)
            days_ago = days_ago.days

            msg = '%s was last used %s days ago'
            args = (lambda_function_arn, days_ago)
            print(msg % args)


def dump_lambda_functions(session):
    all_lambda_functions = []

    for region in get_all_regions(session):

        client = session.client('lambda', region_name=region)

        iterator = yield_handling_errors(get_lambda_functions_for_region, client)

        for lambda_function in iterator:
            function_name = lambda_function['FunctionArn']
            all_lambda_functions.append(function_name)

    return all_lambda_functions


def merge_all_functions(lambda_last_used_data, all_lambda_functions):
    for lambda_function_arn in all_lambda_functions:
        if lambda_function_arn not in lambda_last_used_data:
            lambda_last_used_data[lambda_function_arn] = LambdaData(DEFAULT_DATE,
                                                                    None,
                                                                    None,
                                                                    None)

    return lambda_last_used_data


def main():
    csv_file, session = parse_arguments()

    print('Parsing CSV file...')
    lambda_last_used_data = parse_csv(csv_file)

    print('Getting all existing AWS Lambda functions...')
    all_lambda_functions = dump_lambda_functions(session)

    lambda_last_used_data = merge_all_functions(lambda_last_used_data, all_lambda_functions)

    print('')
    print('Result:')
    print('')
    print_output(lambda_last_used_data)


if __name__ == '__main__':
    main()
