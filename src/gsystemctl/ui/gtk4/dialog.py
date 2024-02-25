import os

from gi.repository import Gtk

from gsystemctl import *
from gsystemctl.ui.gtk4 import *


class AboutDialog(Gtk.AboutDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, modal=True)

        self.set_program_name(APP_NAME)
        self.set_version(APP_VERSION)
        self.set_comments(APP_DESCRIPTION)
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_copyright(APP_COPYRIGHT)
        self.set_website(APP_WEBSITE)
        self.set_logo(Gtk.Image.new_from_file(os.path.join(IMAGE_PATH, 'gsystemctl.png')).get_paintable())


class ErrorDialog(Gtk.Window):
    def __init__(self, **kwargs):
        error_text: str = kwargs.pop('error_text', '')

        super().__init__(**kwargs, title=_('Error'), modal=True, default_width=540)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                      margin_top=15, margin_bottom=15, margin_start=15, margin_end=15)

        text_label = Gtk.Label(label=error_text, vexpand=True, wrap=True,
                               margin_top=10, margin_bottom=15)

        close_button = Gtk.Button(label=_('Close'), hexpand=True)
        close_button.grab_focus()
        close_button.connect('clicked', lambda b: self.close())

        box.append(text_label)
        box.append(close_button)

        self.set_child(box)


class ParamSetterDialog(Gtk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, title=_('Add parameter for the unit'), modal=True, default_width=480)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                      margin_top=15, margin_bottom=15, margin_start=15, margin_end=15)

        self._param_entry = Gtk.Entry(vexpand=True)
        self._param_entry.grab_focus()

        self._cancel_button = Gtk.Button(label=_('Cancel'), hexpand=True)
        self._cancel_button.connect('clicked', lambda b: self.close())
        self._run_button = Gtk.Button(label=_('Run command'), hexpand=True)
        self._run_button.connect('clicked', lambda b: self.close())

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        button_box.append(self._cancel_button)
        button_box.append(self._run_button)

        box.append(self._param_entry)
        box.append(button_box)

        self.set_child(box)

    def get_param_text(self) -> str:
        return self._param_entry.get_text()

    def get_cancel_button(self) -> Gtk.Button:
        return self._cancel_button

    def get_run_button(self) -> Gtk.Button:
        return self._run_button


class StatusDialog(Gtk.Window):
    def __init__(self, **kwargs):
        status_text: str = kwargs.pop('status_text', '')

        super().__init__(**kwargs, title=_('Runtime information'),
                         modal=True, width_request=640, height_request=320)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10,
                      margin_top=15, margin_bottom=15, margin_start=15, margin_end=15)

        text_view = Gtk.TextView(editable=False, monospace=True, visible=True)
        text_view.get_buffer().set_text(status_text)
        scrolled = Gtk.ScrolledWindow(child=text_view, vexpand=True, has_frame=True)

        close_button = Gtk.Button(label=_('Close'), hexpand=True)
        close_button.grab_focus()
        close_button.connect('clicked', lambda b: self.close())

        box.append(scrolled)
        box.append(close_button)

        self.set_child(box)
