import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from utils.json_encoder import json_encoder


def json_printer(data):
    json_str = json.dumps(data,
                          indent=4,
                          sort_keys=True,
                          default=json_encoder)

    print(highlight(json_str, JsonLexer(), TerminalFormatter()))
