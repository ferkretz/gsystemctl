import os

from gi.repository import Gtk

from gsystemctl.globals import *


class Dialog(Gtk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, modal=True)

        self._main_box = self.get_child()
        if self._main_box is None:
            self._main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.set_child(self._main_box)
        self._main_box.set_spacing(10)
        self._main_box.set_margin_top(15)
        self._main_box.set_margin_bottom(15)
        self._main_box.set_margin_start(15)
        self._main_box.set_margin_end(15)

        self._button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        self._main_box.append(self._button_box)

    def add_button(self, label: str, action_func: callable, *args):
        button = Gtk.Button(label=label, hexpand=True)
        if action_func and callable(action_func):
            button.connect('clicked', action_func, self, *args)

        self._button_box.append(button)


class AboutDialog(Gtk.AboutDialog, Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_program_name(get_program_name())
        self.set_version(get_application_version())
        self.set_comments(get_application_description())
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_copyright(get_application_copyright())
        self.set_website(get_application_website())
        logo_path = os.path.join(get_icon_dir(), '160x160', 'gsystemctl.png')
        self.set_logo(Gtk.Image.new_from_file(logo_path).get_paintable())


class ErrorDialog(Dialog):
    def __init__(self, **kwargs):
        error_text: str = kwargs.pop('error_text', '')

        super().__init__(**kwargs, title=_('Error'), default_width=540)

        text_label = Gtk.Label(label=error_text, vexpand=True, wrap=True,
                               margin_top=10, margin_bottom=15)

        self._main_box.prepend(text_label)


class ParamSetterDialog(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, title=_('Add parameter for the unit'), default_width=480)

        self._param_entry = Gtk.Entry(vexpand=True)
        self._param_entry.grab_focus()

        self._main_box.prepend(self._param_entry)

    def get_param_text(self) -> str:
        return self._param_entry.get_text()


class StatusDialog(Dialog):
    def __init__(self, **kwargs):
        status_text: str = kwargs.pop('status_text', '')

        super().__init__(**kwargs, title=_('Runtime information'), width_request=640, height_request=320)

        text_view = Gtk.TextView(editable=False, monospace=True, visible=True)
        text_view.get_buffer().set_text(status_text)
        scrolled = Gtk.ScrolledWindow(child=text_view, vexpand=True, has_frame=True)
        self._main_box.prepend(scrolled)


class SettingsDialog(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, title=_('Settings'), default_width=480)

        general_frame = Gtk.Frame(label=_('General policy'))
        general_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                              margin_start=10, margin_end=10, margin_top=0, margin_bottom=10)
        self._auto_save_check = Gtk.CheckButton(label=_('Automatically save and reload components states'))
        self._auto_refresh_check = Gtk.CheckButton(label=_('Automatically refresh unit list when pages appear'))
        general_box.append(self._auto_save_check)
        general_box.append(self._auto_refresh_check)
        general_frame.set_child(general_box)

        systemctl_frame = Gtk.Frame(label=_('Systemctl'))
        systemctl_grid = Gtk.Grid(column_spacing=5, row_spacing=5,
                                  margin_start=10, margin_end=10, margin_top=0, margin_bottom=10)
        self._systemctl_path_entry = Gtk.Entry(hexpand=True)
        self._systemctl_encoding_entry = Gtk.Entry(hexpand=True)
        systemctl_grid.attach(Gtk.Label(label=_('Path:'), xalign=0), 0, 0, 1, 1)
        systemctl_grid.attach(Gtk.Label(label=_('Encoding:'), xalign=0), 0, 1, 1, 1)
        systemctl_grid.attach(self._systemctl_path_entry, 1, 0, 1, 1)
        systemctl_grid.attach(self._systemctl_encoding_entry, 1, 1, 1, 1)
        systemctl_frame.set_child(systemctl_grid)

        self._main_box.prepend(systemctl_frame)
        self._main_box.prepend(general_frame)

    def set_auto_save(self, auto_save: bool):
        self._auto_save_check.set_active(auto_save)

    def set_auto_refresh(self, auto_refresh: bool):
        self._auto_refresh_check.set_active(auto_refresh)

    def set_systemctl_path(self, systemctl_path: str):
        self._systemctl_path_entry.set_text(systemctl_path)

    def set_systemctl_encoding(self, systemctl_encoding: str):
        self._systemctl_encoding_entry.set_text(systemctl_encoding)

    def get_auto_save(self) -> bool:
        return self._auto_save_check.get_active()

    def get_auto_refresh(self) -> bool:
        return self._auto_refresh_check.get_active()

    def get_systemctl_path(self):
        return self._systemctl_path_entry.get_text()

    def get_systemctl_encoding(self):
        return self._systemctl_encoding_entry.get_text()
