"""
Get the total number of bytes used to store non-current versions
of S3 objects in a bucket.

The result of this tool needs to be multiplied by the S3 pricing
associated with your bucket.

https://aws.amazon.com/s3/pricing/
"""
import sys
import argparse
import boto3


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--bucket',
        help='S3 bucket name',
        required=True
    )

    parser.add_argument(
        '--profile',
        help='AWS profile from ~/.aws/credentials',
        required=True
    )

    args = parser.parse_args()

    try:
        session = boto3.Session(profile_name=args.profile)
    except Exception as e:
        print('%s' % e)
        sys.exit(1)

    return args.bucket, session


def get_size_for_previous_versions(session, bucket):
    total_size = 0
    iter_count = 0
    version_count = 0
    non_current_versions = 0

    s3 = session.client('s3')
    paginator = s3.get_paginator('list_object_versions')

    response_iterator = paginator.paginate(Bucket=bucket)

    for response in response_iterator:

        versions = response.get('Versions')

        iter_count += 1

        if iter_count % 50 == 0:
            stats = {
                'analyzed_objects': version_count,
                'non_current_objects': non_current_versions,
                'non_current_objects_size_bytes': total_size
            }
            print(stats)

        for version in versions:
            version_count += 1

            if version['IsLatest']:
                # We just want the cost for the previous versions
                continue

            total_size += version['Size']
            non_current_versions += 1

    return total_size


def main():
    bucket, session = parse_arguments()

    get_size_for_previous_versions(session, bucket)


if __name__ == '__main__':
    main()
