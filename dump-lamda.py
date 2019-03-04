import datetime
import boto3
import json


def get_all_regions():
    client = boto3.client('ec2')

    for region in client.describe_regions()['Regions']:
        yield region['RegionName']


def get_lambda_functions_for_region(client):
    for lambda_function in client.list_functions()['Functions']:
        yield lambda_function


def default(o):
    if type(o) is datetime.date or type(o) is datetime.datetime:
        return o.isoformat()


def get_function(function_name):
    try:
        function_details = client.get_function(FunctionName=function_name)
    except Exception, e:
        msg = 'Failed to retrieve function details for %s @ %s. Error: "%s"'
        args = (function_name, region, e)
        print(msg % args)

        function_details = {}

    return function_details


def get_policy(function_name):
    try:
        function_policy = client.get_policy(FunctionName=function_name)
    except Exception, e:
        msg = 'Failed to retrieve function policy for %s @ %s. Error: "%s"'
        args = (function_name, region, e)
        print(msg % args)

        function_policy = {}
    else:
        function_policy = json.loads(function_policy['Policy'])

    return function_policy


if __name__ == '__main__':
    all_data = {}

    for region in get_all_regions():

        all_data[region] = {}
        client = boto3.client('lambda', region_name=region)

        for lambda_function in get_lambda_functions_for_region(client):
            function_name = lambda_function['FunctionName']
            print('Region: %s / Lambda function: %s' % (region, function_name))

            function_details = get_function(function_name)
            function_policy = get_policy(function_name)

            all_data[region][function_name] = {}
            all_data[region][function_name]['main'] = lambda_function
            all_data[region][function_name]['details'] = function_details
            all_data[region][function_name]['policy'] = function_policy

    data_str = json.dumps(all_data,
                          indent=4,
                          sort_keys=True,
                          default=default)

    file('lambda-functions.json', 'w').write(data_str)
