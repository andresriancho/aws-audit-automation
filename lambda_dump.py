import os
import json

import boto3

from utils.session import get_session
from utils.regions import get_all_regions
from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer


def get_lambda_functions_for_region(client):
    for lambda_function in client.list_functions()['Functions']:
        yield lambda_function


def get_function(client, function_name):
    try:
        function_details = client.get_function(FunctionName=function_name)
    except Exception as e:
        msg = 'Failed to retrieve function details for %s. Error: "%s"'
        args = (function_name, e)
        print(msg % args)

        function_details = {}

    return function_details


def get_policy(client, function_name):
    try:
        function_policy = client.get_policy(FunctionName=function_name)
    except Exception as e:
        msg = 'Failed to retrieve function policy for %s. Error: "%s"'
        args = (function_name, e)
        print(msg % args)

        function_policy = {}
    else:
        function_policy = json.loads(function_policy['Policy'])

    return function_policy


def main():
    session = get_session()

    all_data = {}

    for region in get_all_regions(session):

        all_data[region] = {}
        client = session.client('lambda', region_name=region)

        lambda_functions = get_lambda_functions_for_region(client)

        for lambda_function in lambda_functions:
            function_name = lambda_function['FunctionName']
            print('Region: %s / Lambda function: %s' % (region, function_name))

            function_details = get_function(client, function_name)
            function_policy = get_policy(client, function_name)

            all_data[region][function_name] = {}
            all_data[region][function_name]['main'] = lambda_function
            all_data[region][function_name]['details'] = function_details
            all_data[region][function_name]['policy'] = function_policy
        
        if not all_data[region]:
            print('Region %s / No Lambda functions' % region)
            continue

    os.makedirs('output', exist_ok=True)
    json_writer('output/lambda-functions.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()