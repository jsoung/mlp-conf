import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    v = str(v).strip().lower()
    if v in ("yes", "true", "on", "1"):
        return True
    if v in ("no", "false", "off", "0"):
        return False
    raise argparse.ArgumentTypeError(f"Boolean value expected, got '{v}'")


class MlpArgumentParser(argparse.ArgumentParser):
    def __init__(self, conf, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conf = conf
        self._add_config_args()

    def _add_config_args(self):
        for section, ns in self.conf._namespaces.items():
            for k in ns.__dict__:
                if k.startswith("_"):
                    continue
                val = getattr(ns, k)

                if isinstance(val, bool):
                    self.add_argument(f"--{k}", default=val, type=str2bool, help=f"({section}) default={val}")
                else:
                    arg_type = type(val) if type(val) in (int, float) else str
                    self.add_argument(f"--{k}", default=val, type=arg_type, help=f"({section}) default={val}")
