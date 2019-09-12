def get_all_regions(session):
    client = session.client('ec2', 'us-east-1')

    for region in client.describe_regions()['Regions']:
        yield region['RegionName']
