"""
This script receives a CSV export from the "Tag Editor" [0] and returns
a list of regions where resources are found.

Default resources such as the default security group for RDS, default VPC, etc.
are ignored. These are some examples of ignored resources:

    EC2 DHCPOptions dopt-a1f31ac8
    EC2 InternetGateway igw-e0f01c89
    EC2 NetworkAcl acl-cf39d0a6
    EC2 RouteTable rtb-7348a11a
    EC2 SecurityGroup sg-9117ddf8
    EC2 Subnet subnet-ec36d985
    EC2 Subnet subnet-78062e32
    EC2 Subnet subnet-289f9150
    EC2 VPC vpc-df48a6b6
    RDS DBSecurityGroup default

For each region the script ignores one VPC, three subnets, one route table, etc.
If there are more resources of this type they were created by the user and that
will mark the region as used.

[0] https://us-west-2.console.aws.amazon.com/resource-groups/tag-editor/find-resources?region=us-west-2
"""

import os
import csv
import sys

from utils.json_writer import json_writer
from utils.json_printer import json_printer

RESOURCES_TO_IGNORE_PER_REGION = {
    'dopt': 1,
    'igw': 1,
    'acl': 1,
    'rtb': 1,
    'sg': 1,
    'subnet': 3,
    'vpc': 1,
    'default': 1
}


class Resource(object):
    def __init__(self, name, service, _type, region, _id):
        self.name = name
        self.service = service
        self.type = _type
        self.region = region
        self.id = _id
        self.id_start = self.id.split('-')[0]

    @classmethod
    def from_row(cls, row):
        """
        Create a new Resource from a row. Rows are list that contain these items:

            RDS DBSecurityGroup default,RDS,DBSecurityGroup,ap-south-1,default,-,-,-,-,-,-,-,-

        :param row: A list with the previously documented items
        :return: A new Resource instance
        """
        name, service, _type, region, _id, _, _, _, _, _, _, _, _ = row

        return Resource(name,
                        service,
                        _type,
                        region,
                        _id)

    def to_dict(self):
        return {
            'name': self.name,
            'service': self.service,
            'type': self.type,
            'region': self.region,
            'id': self.id,
            'id_start': self.id_start,
        }

    def __str__(self):
        return '<Resource %s at %s>' % (self.id, self.region)

    def __repr__(self):
        return '<Resource %s at %s>' % (self.id, self.region)


def get_resources(input_filename):
    with open(input_filename, newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            resource = Resource.from_row(row)

            # Ignore the first row which holds the column names
            if resource.region == 'Region':
                continue

            yield resource


def get_input_csv_filename():
    try:
        csv_filename = sys.argv[1]
    except IndexError:
        print('regions_in_use.py resources.csv')
        sys.exit(1)

    return csv_filename


def resource_matches_to_ignore_id(resource):
    for to_ignore_id_start in RESOURCES_TO_IGNORE_PER_REGION:
        if resource.id_start == to_ignore_id_start:
            return True

    return False


def should_ignore_resource(resource, ignored_resources_per_region):
    #
    # The resource doesn't have a name we ignore
    #
    if not resource_matches_to_ignore_id(resource):
        return False

    #
    # The resource is in a region where nothing has been ignored yet, we don't
    # need to count if there are other resources of the same type
    #
    if resource.region not in ignored_resources_per_region:
        ignored_resources_per_region[resource.region] = [resource]
        # print('Ignoring %s' % resource.id)
        return True

    current_ignore_count = {}

    for already_ignored_resource in ignored_resources_per_region[resource.region]:
        if already_ignored_resource.id_start in current_ignore_count:
            current_ignore_count[already_ignored_resource.id_start] += 1
        else:
            current_ignore_count[already_ignored_resource.id_start] = 1

    if resource.id_start not in current_ignore_count:
        # print('Ignoring %s' % resource.id)
        ignored_resources_per_region[resource.region].append(resource)
        return True

    if current_ignore_count[resource.id_start] < RESOURCES_TO_IGNORE_PER_REGION[resource.id_start]:
        # print('Ignoring %s' % resource.id)
        return True

    return False


def main():
    csv_filename = get_input_csv_filename()

    resources_per_region = {}
    ignored_resources_per_region = {}

    #
    #   Filter out the default resources
    #
    for resource in get_resources(csv_filename):
        if should_ignore_resource(resource, ignored_resources_per_region):
            continue

        if resource.region in resources_per_region:
            resources_per_region[resource.region].append(resource)
        else:
            resources_per_region[resource.region] = [resource]

    #
    #   Make the output printable in JSON
    #
    resources_per_region_json = {}

    for region in resources_per_region:
        for resource in resources_per_region[region]:
            if region in resources_per_region_json:
                resources_per_region_json[region].append(resource.to_dict())
            else:
                resources_per_region_json[region] = [resource.to_dict()]

    used_regions = list(resources_per_region_json.keys())
    used_regions.sort()
    used_regions.append('global')

    # Global is always in use
    resources_per_region_json['global'] = ['iam']

    os.makedirs('output', exist_ok=True)
    json_writer('output/regions-in-use.json', used_regions)
    json_writer('output/resources-by-region.json', resources_per_region_json)

    json_printer(used_regions)


if __name__ == '__main__':
    main()
