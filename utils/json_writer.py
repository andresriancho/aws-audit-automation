import json

from utils.json_encoder import json_encoder


def json_writer(filename, data):
    data_str = json.dumps(data,
                          indent=4,
                          sort_keys=True,
                          default=json_encoder)

    file(filename, 'w').write(data_str)
