import gettext
import locale

from gi.repository import GLib

from gsystemctl.globals import *

GLib.set_application_name(get_application_name())
GLib.set_prgname(get_program_name())

locale.setlocale(locale.LC_ALL, None)
gettext.bindtextdomain(get_application_name(), get_locale_dir())
gettext.textdomain(get_application_name())
