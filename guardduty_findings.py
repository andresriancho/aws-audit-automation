import os
import sys
import json
import boto3

from utils.session import get_session
from utils.regions import get_all_regions
from utils.json_encoder import json_encoder
from utils.json_writer import json_writer
from utils.json_printer import json_printer


def get_findings(session, region):
    """
    Identify configured detectors, and retrieve findings.
    """
    gd_client = session.client("guardduty", region)

    detectors = gd_client.list_detectors()
    detectors = detectors['DetectorIds']

    if not detectors:
        print('%s has no detectors' % region)

    findings = []

    for detector in detectors:
        # TODO: Handle findings pagination
        finding_ids = gd_client.list_findings(DetectorId=detector)
        finding_ids = finding_ids['FindingIds']
        
        findings = gd_client.get_findings(
            DetectorId=detector,
            FindingIds=finding_ids
        )
        findings = findings['Findings']

        for f in findings:
            f['DetectorId'] = detector

        findings.extend(findings)

    return findings


def main():
    session = get_session()

    all_data = {}

    for region in get_all_regions(session):
        all_data[region] = get_findings(session, region)

    os.makedirs('output', exist_ok=True)
    json_writer('output/guardduty.json', all_data)
    json_printer(all_data)


if __name__ == '__main__':
    main()
