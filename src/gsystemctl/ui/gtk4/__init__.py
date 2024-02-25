__all__ = ['CSS_PATH', 'IMAGE_PATH']

import gi
import os

from gsystemctl import *

CSS_PATH = os.path.join(APP_PATH, 'ui/gtk4/css')
IMAGE_PATH = os.path.join(APP_PATH, 'ui/image')

gi.require_version("Gtk", "4.0")

