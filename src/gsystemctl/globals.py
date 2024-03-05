__all__ = ['_', 'n_', 'get_application_version', 'get_application_id',
           'get_application_name', 'get_program_name', 'get_application_description',
           'get_application_website', 'get_application_copyright',
           'get_package_dir', 'get_user_config_dir', 'get_icon_dir', 'get_locale_dir']

import gettext
import os

from gi.repository import GLib

from gsystemctl.version import VERSION

_ = gettext.gettext

n_ = gettext.ngettext


def get_application_version() -> str:
    return VERSION


def get_application_id() -> str:
    return f'com.github.ferkretz.{get_application_name()}'


def get_application_name() -> str:
    return 'gsystemctl'


def get_program_name() -> str:
    return _('Gtk Systemd control')


def get_application_description() -> str:
    return _('Control the systemd service manager')


def get_application_website() -> str:
    return 'https://github.com/ferkretz/gsystemctl'


def get_application_copyright() -> str:
    return _('Copyright © {} Ferenc Kretz').format('2024')


def get_package_dir() -> str:
    return os.path.abspath(os.path.dirname(__file__))


def get_user_config_dir() -> str:
    return GLib.get_user_config_dir()


def get_icon_dir() -> str:
    return os.path.abspath(os.path.join(get_package_dir(), 'ui', 'icons'))


def get_locale_dir() -> str:
    return os.path.abspath(os.path.join(get_package_dir(), 'i18n'))
