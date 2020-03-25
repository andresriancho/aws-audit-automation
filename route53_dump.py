"""
Dump all route53 records
"""

from utils.json_printer import json_printer
from utils.json_writer import json_writer
from utils.session import get_session

PRINT_NAMES = ('A', 'CNAME')


def print_interesting(record):
    record_name = record.get('Name', None)

    if record.get('Type') not in PRINT_NAMES:
        return

    # remove trailing dot
    record_name = record_name[:-1]

    if record_name.endswith('internal'):
        return

    # replace the * at the beginning of the record name
    record_name = record_name.replace('*', 'www')

    print(record_name)


def dump_route53_records(route53_client, zone_name, zone_id, all_data):
    pager = route53_client.get_paginator('list_resource_record_sets')

    for page in pager.paginate(HostedZoneId=zone_id):
        for record in page['ResourceRecordSets']:
            record_name = record.get('Name', None)

            if record_name is None:
                continue

            if record_name in all_data:
                continue

            record_name = record_name.replace('\\052', '*')
            record_name = record_name[:-1]
            record['Name'] = record_name

            if zone_name not in all_data:
                all_data[zone_name] = list()

            all_data[zone_name].append(record)
            print_interesting(record)

    return all_data


def main():
    session = get_session()
    route53_client = session.client('route53')

    zone_info = route53_client.list_hosted_zones()

    all_data = dict()

    for zone in zone_info.get('HostedZones'):
        zone_name = zone['Name']
        zone_id = zone['Id']

        dump_route53_records(route53_client, zone_name, zone_id, all_data)

    json_writer('output/route53_dump.json', all_data)
    return all_data


if __name__ == '__main__':
    all_data = main()
    # json_printer(all_data)
