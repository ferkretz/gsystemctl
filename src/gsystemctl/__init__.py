__all__ = ['APP_PATH', 'APP_NAME', 'APP_DESCRIPTION', 'APP_VERSION',
           'APP_ID', 'APP_WEBSITE', 'APP_COPYRIGHT', '_']

import gettext
import locale
import os

APP_PATH = os.path.dirname(os.path.abspath(__file__))

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain('base', os.path.join(APP_PATH, 'locale'))
gettext.textdomain('base')

_ = gettext.gettext

APP_NAME = 'gsystemctl'
APP_DESCRIPTION = _('Control the systemd service manager')
APP_VERSION = '0.1.0'
APP_ID = 'com.github.ferkretz.gsystemctl'
APP_WEBSITE = 'https://github.com/ferkretz/gsystemctl'
APP_COPYRIGHT = _('Copyright © {} Ferenc Kretz').format('2024')
