import sys

from gi.repository import Gio, Gtk

from gsystemctl.globals import *
from gsystemctl.ui.mainwindow import MainWindow


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id=get_application_id(),
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS, **kwargs)
        self._main_window = None

    def do_activate(self):
        self._main_window = self._main_window or MainWindow(application=self)
        self._main_window.present()


def run():
    Application().run(sys.argv)
