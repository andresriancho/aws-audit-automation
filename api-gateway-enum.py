import boto3
import json


from utils.json_encoder import json_encoder
from utils.session import get_session
from utils.regions import get_all_regions


def get_api_gateways_for_region(client):
    for rest_api in client.get_rest_apis()['items']:
        yield rest_api


def get_authorizers(client, api_id):
    return client.get_authorizers(restApiId=api_id)['items']


def main():
    all_data = {}
    session = get_session()

    for region in get_all_regions(session):
        all_data[region] = {}
        client = session.client('apigateway', region_name=region)

        for rest_api in get_api_gateways_for_region(client):
            api_id = rest_api['id']
            print('Region: %s / API ID: %s' % (region, api_id))
            
            try:
                authorizers = get_authorizers(client, api_id)
            except Exception as e:
                msg = 'Failed to retrieve authorizers for %s @ %s. Error: "%s"'
                args = (api_id, region, e)
                print(msg % args)
                
                authorizers = {}

            all_data[region][api_id] = {}
            all_data[region][api_id]['main'] = rest_api
            all_data[region][api_id]['authorizers'] = authorizers
        
        else:
            print('Region: %s / No API gateways' % region)

    data_str = json.dumps(all_data,
                          indent=4,
                          sort_keys=True,
                          default=json_encoder)

    file('api-gateways.json', 'w').write(data_str)


if __name__ == '__main__':
    main()
