import datetime
import boto3
import json


def get_all_regions():
    client = boto3.client('ec2')

    for region in client.describe_regions()['Regions']:
        yield region['RegionName']


def get_shapshots_for_region(client):
    paginator = client.get_paginator('describe_db_snapshots')
    
    for page in paginator.paginate():
        for shapshot in page['DBSnapshots']:
            yield shapshot


def get_snapshot_attributes(client, snapshot_id):
    return client.describe_db_snapshot_attributes(DBSnapshotIdentifier=snapshot_id)['DBSnapshotAttributesResult']


def default(o):
  if type(o) is datetime.date or type(o) is datetime.datetime:
    return o.isoformat()


if __name__ == '__main__':
    all_data = {}

    for region in get_all_regions():
        all_data[region] = {}
        client = boto3.client('rds', region_name=region)

        for snapshot in get_shapshots_for_region(client):
            snapshot_id = snapshot['DBSnapshotIdentifier']
            print('Region: %s / Snapshot: %s' % (region, snapshot_id))
            
            try:
                attributes = get_snapshot_attributes(client, snapshot_id)
            except Exception, e:
                msg = 'Failed to retrieve attributes for %s @ %s. Error: "%s"'
                args = (snapshot_id, region, e)
                print(msg % args)
                
                attributes = {}

            all_data[region][snapshot_id] = {}
            all_data[region][snapshot_id]['main'] = snapshot
            all_data[region][snapshot_id]['attributes'] = attributes
        else:
            print('Region: %s / No snapshots found' % (region,))

    data_str = json.dumps(all_data,
                          indent=4,
                          sort_keys=True,
                          default=default)

    file('rds-snapshots.json', 'w').write(data_str)