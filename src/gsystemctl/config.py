import configparser
import os

from gsystemctl.globals import *


class Config:
    def __init__(self):
        config_name = f'{get_application_name()}.ini'
        self._def_cfg_path = os.path.abspath(os.path.join(get_package_dir(), config_name))
        self._cur_cfg_path = os.path.abspath(os.path.join(get_user_config_dir(), config_name))

        self._def_cfg = configparser.ConfigParser()
        self._cur_cfg = configparser.ConfigParser()

        self._def_cfg.read(self._def_cfg_path)

        if os.path.isfile(self._cur_cfg_path):
            self._cur_cfg.read(self._cur_cfg_path)

    def save(self):
        with open(self._cur_cfg_path, 'w') as file:
            self._cur_cfg.write(file)

    def set(self, section: str, option: str, value: str | int | float | bool):
        if self._def_cfg.get(section, option, fallback=None) is not None:
            if not self._cur_cfg.has_section(section):
                self._cur_cfg.add_section(section)
            self._cur_cfg.set(section, option, str(value))

    def get(self, section: str, option: str) -> str | int | float | bool:
        return {
            'str': lambda: self._cur_cfg.get(section, option, fallback=self.get_default(section, option)),
            'int': lambda: self._cur_cfg.getint(section, option, fallback=self.get_default(section, option)),
            'float': lambda: self._cur_cfg.getfloat(section, option, fallback=self.get_default(section, option)),
            'bool': lambda: self._cur_cfg.getboolean(section, option, fallback=self.get_default(section, option)),
        }[self._def_cfg.get(section, f'{option}.type', fallback='str')]()

    def get_default(self, section: str, option: str) -> str | int | float | bool:
        return {
            'str': lambda: self._def_cfg.get(section, option),
            'int': lambda: self._def_cfg.getint(section, option),
            'float': lambda: self._def_cfg.getfloat(section, option),
            'bool': lambda: self._def_cfg.getboolean(section, option),
        }[self._def_cfg.get(section, f'{option}.type', fallback='str')]()
