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

def test_default_section_variable_interpolation(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, """
[DEFAULT]
user = alice
suffix = _prod

[section]
output = dataset_{user}{suffix}
""")
    conf = MlpConfig(str(cfg_path))
    assert conf.section.output == "dataset_alice_prod"

def test_envvar_interpolation(monkeypatch, tmp_path):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, """
[section]
output = dataset_{{USER}}
date = {{DATE}}
cwd = {{CWD}}
branch = {{GIT_BRANCH}}
""")
    monkeypatch.setenv("USER", "testuser")
    conf = MlpConfig(str(cfg_path))
    assert conf.section.output.startswith("dataset_testuser")
    assert isinstance(conf.section.date, str) and conf.section.date.isdigit() and len(conf.section.date) == 8
    assert os.path.isabs(conf.section.cwd)
    assert isinstance(conf.section.branch, str)

def test_extended_interpolation(tmp_path, monkeypatch):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, """
[project]
name = example_project

[preprocess]
output_dir = ${project:name}/build/output/{{USER}}
""")
    monkeypatch.setenv("USER", "jerry")
    conf = MlpConfig(str(cfg_path))
    assert conf.preprocess.output_dir == "example_project/build/output/jerry"

def test_default_and_envvar_combined(tmp_path, monkeypatch):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, """
[DEFAULT]
prefix = foo

[section]
output = {prefix}_{{USER}}
""")
    monkeypatch.setenv("USER", "bob")
    conf = MlpConfig(str(cfg_path))
    assert conf.section.output == "foo_bob"

def test_list_params(tmp_path):
    cfg_path = tmp_path / "project.cfg"
    write_cfg(cfg_path, """
[DEFAULT]
foo = bar

[section]
num = 1
val = {foo}
""")
    conf = MlpConfig(str(cfg_path))
    params = conf.list_params()
    assert ("section", "num", 1, "default") in params
    assert ("section", "val", "bar", "default") in params