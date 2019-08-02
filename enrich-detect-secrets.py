USAGE = """\
Enrich the output of detect-secrets to include the secret and context.

./enrich-detect-secrets.py detect-secrets-output.json scanned-file.json
"""

import sys
import json
import os


def parse_arguments():
    if len(sys.argv) != 3:
        print(USAGE)
        sys.exit(1)

    ds_output = sys.argv[1]
    scanned_file = sys.argv[2]

    if not os.path.exists(ds_output):
        print(USAGE)
        sys.exit(2)

    if not os.path.exists(scanned_file):
        print(USAGE)
        sys.exit(2)

    return ds_output, scanned_file


def get_lines(scanned_file, line_number):
    line_numbers = [line_number - 3,
                    line_number - 2,
                    line_number - 1,
                    line_number,
                    line_number + 1,
                    line_number + 2,
                    line_number + 3,]

    output = []

    for i, line in enumerate(open(scanned_file)):
        if i + 1 in line_numbers:
            output.append(line[:-1])
    
    return output


def enrich(ds_output, scanned_file):
    detected_secrets = json.loads(open(ds_output).read())

    results = detected_secrets.get('results', {})
    
    if len(results) != 1:
        print('Can only handle detect-secrets output with one filename.')
        sys.exit(1)

    for filename in results:
        for result in results[filename]:
            line_number = result['line_number']
            lines = get_lines(scanned_file, line_number)

            result['context'] = lines
    
    json_data = json.dumps(detected_secrets, indent=4)
    output = open(ds_output, 'w')
    output.write(json_data)

if __name__ == '__main__':
    ds_output, scanned_file = parse_arguments()
    enrich(ds_output, scanned_file)
