"""
Simple systemctl wrapper - see systemctl(1) for further information.
"""

import subprocess
import re
from typing import Final


class SystemctlError(Exception):
    pass


class SystemctlCallType:
    SYSTEM: Final[str] = 'system'
    USER: Final[str] = 'user'


class SystemctlListType:
    UNITS: Final[str] = 'units'
    UNITS_FILES: Final[str] = 'unit-files'


class Systemctl:

    def __init__(self, **kwargs):
        self.systemctl = kwargs.pop('systemctl', '/usr/bin/systemctl')
        self.encoding = kwargs.pop('encoding', 'UTF-8')

    def set_systemctl(self, systemctl: str):
        self.systemctl = systemctl

    def set_encoding(self, encoding: str):
        self.encoding = encoding

    def status(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} status -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

        return sp.stdout.decode(encoding=self.encoding).strip()

    def start(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} start -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

    def stop(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} stop -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

    def restart(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} restart -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

    def is_active(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} is-active -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

        return sp.stdout.decode(encoding=self.encoding).strip()

    def enable(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} enable -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

    def disable(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} disable -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

    def reenable(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} reenable -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

    def is_enabled(self, unit_id: str, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} is-enabled -- {unit_id}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

        return sp.stdout.decode(encoding=self.encoding).strip()

    def list_units(self, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} list-units',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr.strip())

        unit_list = []
        lines = sp.stdout.decode(encoding=self.encoding).split('\n')
        for i in range(1, len(lines) - 7):
            unit_list.append(re.split('\s+', lines[i][2:], 4))

        return unit_list

    def list_unit_files(self, call_type=SystemctlCallType.SYSTEM):
        sp = subprocess.run(
            f'{self.systemctl} --{call_type} list-unit-files',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        stderr = sp.stderr.decode(encoding=self.encoding)
        if stderr != '':
            raise SystemctlError(stderr)

        file_list = []
        lines = sp.stdout.decode(encoding=self.encoding).split('\n')
        for i in range(1, len(lines) - 3):
            file_list.append(re.split('\s+', lines[i]))

        return file_list

    def list(self, list_type=SystemctlListType.UNITS, call_type=SystemctlCallType.SYSTEM):
        if list_type == SystemctlListType.UNITS:
            return self.list_units(call_type)
        elif list_type == SystemctlListType.UNITS_FILES:
            return self.list_unit_files(call_type)

        return []
