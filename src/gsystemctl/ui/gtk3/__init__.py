__all__ = ['GLADE_UI_PATH', 'IMAGE_PATH']

import gi
import os

from gsystemctl import *

GLADE_UI_PATH = os.path.join(APP_PATH, 'ui/gtk3/glade')
IMAGE_PATH = os.path.join(APP_PATH, 'ui/image')

gi.require_version("Gtk", "3.0")
