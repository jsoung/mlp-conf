import argparse
from mlp_conf.argparse import MlpArgumentParser
from mlp_conf.config import MlpConfig


def test_argparse_defaults(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    with open(cfg_path, "w") as f:
        f.write("[section]\nkey.1 = value1\nkey.2 = value2\n")
    conf = MlpConfig(str(cfg_path))
    parser = MlpArgumentParser(conf)
    args = parser.parse_args([])
    assert args.section_key_1 == "value1"
    assert args.section_key_2 == "value2"


def test_argparse_override(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    with open(cfg_path, "w") as f:
        f.write("[section]\nkey.1 = value1\nkey.2 = value2\n")
    conf = MlpConfig(str(cfg_path))
    parser = MlpArgumentParser(conf)
    args = parser.parse_args(["--section_key_1", "cli_value1", "--section_key_2", "cli_value2"])
    assert args.section_key_1 == "cli_value1"
    assert args.section_key_2 == "cli_value2"


def test_argparse_type_inference(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    with open(cfg_path, "w") as f:
        f.write("[section]\nintkey = 42\nfloatkey = 3.14\nboolkey = yes\n")
    conf = MlpConfig(str(cfg_path))
    parser = MlpArgumentParser(conf)
    args = parser.parse_args(["--section_intkey", "123", "--section_floatkey", "2.71", "--section_boolkey", "no"])
    assert args.section_intkey == 123
    assert args.section_floatkey == 2.71
    assert args.section_boolkey is False
