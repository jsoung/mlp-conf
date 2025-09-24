# MLP Configuration Utility

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Build Status](https://img.shields.io/github/actions/workflow/status/<your-github-username>/<your-repo>/python-app.yml?branch=main)

This Python package provides utilities to manage parameters and arguments for Machine Learning projects. A typical ML project consists of multiple scripts for data preparation, cleansing, feature engineering, training, testing, evaluation, and inference. Each script may have dozens of runtime arguments or parameters. This is especially true when scripts are used in both local development and cloud environments, where computation is often scaled using platform tools such as Apache Beam and Vertex AI.

This utility aims to provide a clear and consistent way to manage these parameters and arguments. Parameters can be easily overridden to work in either local or cloud environments. They can also be easily configured to run individually or orchestrated with Airflow.

## Configuration Files

Each project should include a `project.cfg` file (in addition to files such as `pyproject.toml` and `requirements.txt`). The configuration file uses the INI format. For details, refer to the [configparser — Configuration file parser](https://docs.python.org/3/library/configparser.html) documentation.

Developers can override arguments and parameters defined in `project.cfg` by creating a `project.override.cfg` file. The `project.cfg` file should be committed to version control, while `project.override.cfg` should not.

## Main Classes

The package provides two main classes:

- `MlpArgumentParser`: Extends [argparse](https://docs.python.org/3/library/argparse.html).
- `MlpConfig`: Parses configuration files into accessible namespaces.

## Variable Interpolation

This package supports three types of variable interpolation in your config files:

1. **Default variables**:  
   Defined in the `[DEFAULT]` section (or at the top of the config file, without a section header).  
   Referenced as `{var}` in any section.

2. **Section/Key interpolation**:  
   Using `${section:key}` syntax, values from other sections can be referenced (requires `ExtendedInterpolation`).

3. **Environment/system variables**:  
   Special placeholders in the form `{{USER}}`, `{{DATE}}`, `{{GIT_BRANCH}}`, `{{CWD}}` can be used in any config value.  
   These are automatically substituted at load time.

### Example Usage

```ini
[DEFAULT]
user = alice
suffix = _prod

[project]
name = example_project

[preprocess]
output_dir = ${project:name}/build/output/{user}/{{USER}}
```

When you load your config with `MlpConfig`, the variables are resolved as follows:
- `{user}` and `{suffix}` are replaced with values from `[DEFAULT]`.
- `${project:name}` is replaced with the value from `[project]`.
- `{{USER}}` is replaced with the current user.

### How it works

You do **not** need to call any substitution functions yourself.  
Just use `MlpConfig`:

```python
from mlp_conf.config import MlpConfig

cfg = MlpConfig("project.cfg")
print(cfg.preprocess.output_dir)  # e.g. example_project/build/output/alice/jerry
```

### Supported Environment/System Placeholders

- `{{USER}}` — current user name
- `{{DATE}}` — current date in `yyyymmdd` format (always a string)
- `{{GIT_BRANCH}}` — current git branch (if in a git repo)
- `{{CWD}}` — current working directory

### Notes

- You can override any config value via an override file or environment variable (see tests for details).
- The `[env]` section is **not** special; use `[DEFAULT]` for global variables.
- `${section:key}` interpolation is supported via `ExtendedInterpolation`.

### Testing

See `tests/mlp_conf/test_config.py` for comprehensive test cases covering all features.