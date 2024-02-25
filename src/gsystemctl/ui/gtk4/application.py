import sys

from gi.repository import Gio, Gtk

from gsystemctl import *
from gsystemctl.ui.gtk4.mainwindow import MainWindow


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id=APP_ID,
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS, **kwargs)
        self.main_window = None

    def do_activate(self):
        self.main_window = self.main_window or MainWindow(application=self)
        self.main_window.present()


def run():
    Application().run(sys.argv)
