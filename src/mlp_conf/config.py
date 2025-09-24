import configparser
import os
from .envvar import envsubst

class Namespace:
    def __init__(self, name):
        self._name = name

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self.__dict__[key] = value

class MlpConfig:
    def __init__(self, cfg_path="project.cfg", override_path="project.override.cfg"):
        self._sources = {}
        self._namespaces = {}
        self._cfg_path = cfg_path
        self._override_path = override_path
        self._load_config()

    def _load_config(self):
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
                # --- Only infer type if key is not 'date' ---
                if isinstance(val, str) and k.lower() != "date":
                    val = self._infer_type(val)
                setattr(ns, k, val)
                self._sources[f"{section}.{k}"] = src
            setattr(self, section, ns)
            self._namespaces[section] = ns

    def _infer_type(self, val):
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

    def list_params(self):
        params = []
        for section, ns in self._namespaces.items():
            for k in ns.__dict__:
                if k.startswith('_'):
                    continue
                val = getattr(ns, k)
                src = self._sources.get(f"{section}.{k}", "default")
                params.append((section, k, val, src))
        return params