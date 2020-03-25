import json
import os

from utils.json_encoder import json_encoder


def json_writer(filename, data):
    os.makedirs('output', exist_ok=True)

    data_str = json.dumps(data,
                          indent=4,
                          sort_keys=True,
                          default=json_encoder)

    open(filename, 'w').write(data_str)
