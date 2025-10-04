# some quick adhoc tests
# to be moved to proper unit tests later

import os
from mlp_conf.argparse import MlpArgumentParser

argparser = MlpArgumentParser(conf=None, description="Test Parser")
args = argparser.parse_args()
print(args)