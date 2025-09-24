import sys
from tabulate import tabulate
from mlp_conf.config import MlpConfig
from typing import NoReturn

def main() -> None:
    """Entry point for the CLI tool.

    Loads the configuration, lists all parameters, and prints them in a table.
    """
    conf = MlpConfig()
    params = conf.list_params()
    headers = ["Namespace", "Key", "Value", "Source"]
    print(tabulate(sorted(params), headers=headers, tablefmt="github"))

if __name__ == "__main__":
    main()