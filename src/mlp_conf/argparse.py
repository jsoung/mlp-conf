import argparse
from typing import Any

from mlp_conf.config import MlpConfig


def str2bool(v: Any) -> bool:
    """Convert a string or boolean value to a boolean.

    Args:
        v: The value to convert. Can be a bool or a string.

    Returns:
        bool: The converted boolean value.

    Raises:
        argparse.ArgumentTypeError: If the value cannot be interpreted as boolean.
    """
    if isinstance(v, bool):
        return v
    v = str(v).strip().lower()
    if v in ("yes", "true", "on", "1"):
        return True
    if v in ("no", "false", "off", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Boolean value expected, got '{v}'")


class MlpArgumentParser(argparse.ArgumentParser):
    """Argument parser that auto-adds arguments from an MlpConfig instance."""

    def __init__(self, conf: Any = None, *args, **kwargs):
        """Initializes the MlpArgumentParser.

        Args:
            conf: An MlpConfig instance containing configuration namespaces. If None, a default MlpConfig will be used.
            *args: Additional positional arguments for ArgumentParser.
            **kwargs: Additional keyword arguments for ArgumentParser.
        """
        super().__init__(*args, **kwargs)
        self.conf = MlpConfig() if conf is None else conf
        self._add_config_args()

    def _add_config_args(self) -> None:
        """Add arguments to the parser based on the config namespaces."""
        for section, ns in self.conf._namespaces.items():
            for k in ns.__dict__:
                if k.startswith("_"):
                    continue
                val = getattr(ns, k)
                # Replace dots with underscores in argument names
                arg_name = f"--{section}_{k.replace('.', '_')}"
                if isinstance(val, bool):
                    self.add_argument(
                        arg_name,
                        default=val,
                        type=str2bool,
                        help=f"({section}) default={val}",
                    )
                else:
                    arg_type = type(val) if type(val) in (int, float) else str
                    self.add_argument(
                        arg_name,
                        default=val,
                        type=arg_type,
                        help=f"({section}) default={val}",
                    )
