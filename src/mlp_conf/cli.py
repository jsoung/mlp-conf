import sys
from tabulate import tabulate
from mlp_conf.config import MlpConfig

def main():
    conf = MlpConfig()
    params = conf.list_params()
    # Find max section length for alignment
    headers = ["Namespace", "Key", "Value", "Source"]
    print(tabulate(sorted(params), headers=headers, tablefmt="github"))

if __name__ == "__main__":
    main()