import os
import pytest
from mlp_conf.config import MlpConfig

def write_cfg(path, content):
    with open(path, "w") as f:
        f.write(content)

def test_basic_config(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, "[section]\nkey = value\n")
    conf = MlpConfig(str(cfg_path))
    assert conf.section.key == "value"

def test_override_config(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    override_path = tmp_path / "project.override.cfg"
    write_cfg(cfg_path, "[section]\nkey = value\n")
    write_cfg(override_path, "[section]\nkey = override\n")
    conf = MlpConfig(str(cfg_path), str(override_path))
    assert conf.section.key == "override"
    assert conf._sources["section.key"] == "override"

def test_type_inference(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, "[types]\nintkey = 42\nfloatkey = 3.14\nboolkey = yes\nstrkey = hello\n")
    conf = MlpConfig(str(cfg_path))
    assert isinstance(conf.types.intkey, int)
    assert isinstance(conf.types.floatkey, float)
    assert isinstance(conf.types.boolkey, bool)
    assert isinstance(conf.types.strkey, str)
    assert conf.types.intkey == 42
    assert conf.types.floatkey == 3.14
    assert conf.types.boolkey is True
    assert conf.types.strkey == "hello"

def test_env_override(monkeypatch, tmp_path):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, "[section]\nkey = value\n")
    monkeypatch.setenv("MLP_SECTION_KEY", "envval")
    conf = MlpConfig(str(cfg_path))
    assert conf.section.key == "envval"
    assert conf._sources["section.key"] == "env"

def test_override_unknown_key(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    override_path = tmp_path / "project.override.cfg"
    write_cfg(cfg_path, "[section]\nkey = value\n")
    write_cfg(override_path, "[section]\nunknown = value\n")
    with pytest.raises(ValueError):
        MlpConfig(str(cfg_path), str(override_path))