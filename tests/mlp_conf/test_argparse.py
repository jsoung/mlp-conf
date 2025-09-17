import argparse

from mlp_conf.argparse import MlpArgumentParser
from mlp_conf.config import MlpConfig


def test_argparse_defaults(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    with open(cfg_path, "w") as f:
        f.write("[section]\nkey = value\n")
    conf = MlpConfig(str(cfg_path))
    parser = MlpArgumentParser(conf)
    args = parser.parse_args([])
    assert args.key == "value"


def test_argparse_override(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    with open(cfg_path, "w") as f:
        f.write("[section]\nkey = value\n")
    conf = MlpConfig(str(cfg_path))
    parser = MlpArgumentParser(conf)
    args = parser.parse_args(["--key", "cli"])
    assert args.key == "cli"


def test_argparse_type_inference(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    with open(cfg_path, "w") as f:
        f.write("[section]\nintkey = 42\nfloatkey = 3.14\nboolkey = yes\n")
    conf = MlpConfig(str(cfg_path))
    parser = MlpArgumentParser(conf)
    args = parser.parse_args(["--intkey", "123", "--floatkey", "2.71", "--boolkey", "no"])
    assert args.intkey == 123
    assert args.floatkey == 2.71
    assert args.boolkey is False
