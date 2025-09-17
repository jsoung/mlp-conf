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

### Example Usage

Given a configuration file:

```ini
[preprocess]
input = my_input_data_path/my_input_date_file
```

The script will initialize `MlpConfig` like this:

```python
conf = MlpConfig()
```

Configurations are parsed into the `MlpConfig` instance as namespaces and can be accessed like this:

```python
input = conf.preprocess.input
```

An implicit command line argument equivalent to the following is added to `MlpArgumentParser`:

```python
parser = MlpArgumentParserr(conf)
parser.add_argument('--input', default=conf.preprocess.input)
```

When running the preprocess script, all parameters can be overridden with command line arguments. The script will get the value as:

```python
input = args.input
```

Since the INI file format does not support typing, `MlpArgumentParser` performs basic type conversions, such as the following:

- string: this is the default
- int: for example, 12345
- float: for example, 1.0
- bool: 'yes'/'no', 'on'/'off', 'true'/'false', and '1'/'0'