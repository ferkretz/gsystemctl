"""
Simple systemctl wrapper - see systemctl(1) for further information.
"""

import subprocess
import re
from enum import StrEnum


class SystemdItemCommand(StrEnum):
    STATUS = 'status'
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'
    RELOAD = 'reload'
    ISOLATE = 'isolate'
    KILL = 'kill'
    CLEAN = 'clean'
    FREEZE = 'freeze'
    THAW = 'thaw'
    ENABLE = 'enable'
    DISABLE = 'disable'
    REENABLE = 'reenable'
    PRESET = 'preset'


class SystemdItemType(StrEnum):
    UNIT = 'units'
    TEMPLATE = 'unit-files'


class SystemdConnectType(StrEnum):
    SYSTEM = 'system'
    USER = 'user'


class SystemctlError(Exception):
    pass


class Systemctl:

    def __init__(self, **kwargs):
        self._path = kwargs.pop('path', '/usr/bin/systemctl')
        self._encoding = kwargs.pop('encoding', 'UTF-8')

    def set_path(self, path: str):
        self._path = path

    def set_encoding(self, encoding: str):
        self._encoding = encoding

    def get_path(self) -> str:
        return self._path

    def get_encoding(self) -> str:
        return self._encoding

    def run_version_command(self) -> str:
        sp = subprocess.run(
            f'{self._path} --version',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self._encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

        return sp.stdout.decode(encoding=self._encoding).strip().split('\n')[0]

    def run_item_command(self, item_command: SystemdItemCommand, item_id: str,
                         connect_type: SystemdConnectType = SystemdConnectType.SYSTEM) -> str:
        sp = subprocess.run(
            f'{self._path} --{connect_type} {item_command} -- {item_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self._encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

        return sp.stdout.decode(encoding=self._encoding).strip()

    def run_list_command(self, item_type: SystemdItemType,
                         connect_type: SystemdConnectType = SystemdConnectType.SYSTEM) -> []:
        sp = subprocess.run(
            f'{self._path} --quiet --{connect_type} list-{item_type}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self._encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

        item_list = []
        for line in sp.stdout.decode(encoding=self._encoding).split('\n'):
            # skip empty lines
            if line != '':
                # remove indicators (only units are effected)
                if item_type == SystemdItemType.UNIT:
                    line = line[2:]

                # split lines to list (descriptions may contain spaces, but there are only 5 columns)
                prop_list = re.split('\s+', line.strip(), 4)

                # only fixed number of columns allowed
                if item_type == SystemdItemType.UNIT:
                    requested_len = 5
                else:
                    requested_len = 3
                current_len = len(prop_list)
                if current_len != requested_len:
                    raise SystemctlError('Unit must have exactly {} properties but it has {}\n{}'
                                         .format(requested_len, current_len, prop_list))
                item_list.append(prop_list)

        return item_list
