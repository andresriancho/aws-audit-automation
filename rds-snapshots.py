import os
import json

import boto3

from utils.session import get_session
from utils.regions import get_all_regions
from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer


def get_shapshots_for_region(client):
    paginator = client.get_paginator('describe_db_snapshots')
    
    for page in paginator.paginate():
        for shapshot in page['DBSnapshots']:
            yield shapshot


def get_snapshot_attributes(client, snapshot_id):
    return client.describe_db_snapshot_attributes(DBSnapshotIdentifier=snapshot_id)['DBSnapshotAttributesResult']


def main():
    session = get_session()

    all_data = {}

    for region in get_all_regions(session):
        all_data[region] = {}
        client = session.client('rds', region_name=region)

        for snapshot in get_shapshots_for_region(client):
            snapshot_id = snapshot['DBSnapshotIdentifier']
            print('Region: %s / Snapshot: %s' % (region, snapshot_id))
            
            try:
                attributes = get_snapshot_attributes(client, snapshot_id)
            except Exception as e:
                msg = 'Failed to retrieve attributes for %s @ %s. Error: "%s"'
                args = (snapshot_id, region, e)
                print(msg % args)
                
                attributes = {}

            all_data[region][snapshot_id] = {}
            all_data[region][snapshot_id]['main'] = snapshot
            all_data[region][snapshot_id]['attributes'] = attributes
        else:
            print('Region: %s / No snapshots found' % (region,))

    os.makedirs('output', exist_ok=True)
    json_writer('output/rds-snapshots.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()
