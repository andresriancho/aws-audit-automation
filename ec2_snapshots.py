import os
import json
import sys

import boto3

from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer
from utils.session import get_session
from utils.regions import get_all_regions


def get_snapshots(ec2_client):
    paginator = ec2_client.get_paginator('describe_snapshots')

    response_iterator = paginator.paginate(DryRun=False,
                                           OwnerIds=['self'],
                                           PaginationConfig={'MaxItems': 5000, 'PageSize': 100})

    for snapshots_page in response_iterator:
        snapshots = snapshots_page['Snapshots']

        for snapshot in snapshots:
            perms = ec2_client.describe_snapshot_attribute(Attribute='createVolumePermission',
                                                        SnapshotId=snapshot['SnapshotId'])['CreateVolumePermissions']
            
            # The permissions for a snapshot are specified using the 
            # createVolumePermission attribute of the snapshot. 
            #
            # To make a snapshot public, set the group to all. 
            # To share a snapshot with a specific AWS account, 
            # set the user to the ID of the AWS account.
            #
            # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html
            snapshot['CreateVolumePermissions'] = perms

            if perms:
                print('Shared snapshot found: %s !' % snapshot['SnapshotId'])
                shapshot['shared'] = True
            else:
                shapshot['shared'] = False
            
            yield snapshot


def main():
    session = get_session()

    all_data = {}

    for region in get_all_regions(session):
        ec2_client = session.client('ec2', region)
        all_data[region] = {}

        print('Processing region: %s' % region)

        for i, snapshot in enumerate(get_snapshots(ec2_client)):
            all_data[region][i] = snapshot
            
            sys.stdout.write('.')
            sys.stdout.flush()
        
        if all_data[region]:
            print('\n')

    os.makedirs('output', exist_ok=True)
    json_writer('output/ec2_snapshots.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()
