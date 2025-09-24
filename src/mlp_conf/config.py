import configparser
import os
from .envvar import envsubst
from typing import Any, Dict

class Namespace:
    """Namespace for configuration section attributes."""

    def __init__(self, name: str):
        """Initializes a Namespace.

        Args:
            name: The name of the section.
        """
        self._name = name

    def __setattr__(self, key: str, value: Any) -> None:
        """Sets an attribute on the namespace.

        Args:
            key: Attribute name.
            value: Attribute value.
        """
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self.__dict__[key] = value

class MlpConfig:
    """Configuration loader and accessor for INI-style config files."""

    def __init__(self, cfg_path: str = "project.cfg", override_path: str = "project.override.cfg"):
        """Initializes the MlpConfig.

        Args:
            cfg_path: Path to the main config file.
            override_path: Path to the override config file.
        """
        self._sources: Dict[str, str] = {}
        self._namespaces: Dict[str, Namespace] = {}
        self._cfg_path = cfg_path
        self._override_path = override_path
        self._load_config()

    def _load_config(self) -> None:
        """Loads and processes the configuration files."""
        parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        parser.optionxform = str
        parser.read(self._cfg_path)
        base = {}
        # Collect DEFAULT section for variable interpolation
        defaults = dict(parser.defaults())
        for section in parser.sections():
            base[section] = dict(parser.items(section))
        override = {}
        if os.path.exists(self._override_path):
            override_parser = configparser.ConfigParser()
            override_parser.optionxform = str
            override_parser.read(self._override_path)
            for section in override_parser.sections():
                if section not in base:
                    raise ValueError(f"Unknown section '{section}' in override config")
                for k, v in override_parser.items(section):
                    if k not in base[section]:
                        raise ValueError(f"Unknown key '{k}' in override config section '{section}'")
                    override.setdefault(section, {})[k] = v
        # Apply env overrides
        env_overrides = {}
        for section in base:
            for k in base[section]:
                env_key = f"MLP_{section.upper()}_{k.upper()}"
                if env_key in os.environ:
                    env_overrides.setdefault(section, {})[k] = os.environ[env_key]
        # Build namespaces
        for section in base:
            ns = Namespace(section)
            for k, v in base[section].items():
                val = v
                src = "default"
                if section in override and k in override[section]:
                    val = override[section][k]
                    src = "override"
                if section in env_overrides and k in env_overrides[section]:
                    val = env_overrides[section][k]
                    src = "env"
                # Interpolate with DEFAULT section variables first
                if isinstance(val, str):
                    for dkey, dval in defaults.items():
                        val = val.replace(f"{{{dkey}}}", dval)
                    val = envsubst(val)
                # Always treat 'date' as string
                if isinstance(val, str) and k.lower() != "date":
                    val = self._infer_type(val)
                setattr(ns, k, val)
                self._sources[f"{section}.{k}"] = src
            setattr(self, section, ns)
            self._namespaces[section] = ns

    def _infer_type(self, val: str) -> Any:
        """Infer the type of a string value.

        Args:
            val: The value to infer.

        Returns:
            The value converted to int, float, bool, or left as string.
        """
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        if isinstance(val, str):
            v = val.strip().lower()
            if v in ("yes", "true", "on", "1"):
                return True
            if v in ("no", "false", "off", "0"):
                return False
        return val

    def list_params(self) -> list:
        """List all parameters in the configuration.

        Returns:
            list: A list of tuples (section, key, value, source).
        """
        params = []
        for section, ns in self._namespaces.items():
            for k in ns.__dict__:
                if k.startswith('_'):
                    continue
                val = getattr(ns, k)
                src = self._sources.get(f"{section}.{k}", "default")
                params.append((section, k, val, src))
        return params