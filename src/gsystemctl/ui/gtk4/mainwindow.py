from gi.repository import Gio, GLib, GObject, Gtk

from gsystemctl import *
from gsystemctl.systemctl import Systemctl, SystemctlError, SystemdConnectType, SystemdItemCommand
from gsystemctl.ui.gtk4.dialog import AboutDialog, ErrorDialog, ParamSetterDialog, StatusDialog
from gsystemctl.ui.gtk4.menu import HamburgerMenu
from gsystemctl.ui.gtk4.systemdnotebook import SystemdItem, SystemdNotebook


class TitleBar(Gtk.HeaderBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title_widget(Gtk.Label(label=APP_NAME))

        self._refresh_button = Gtk.Button(icon_name='view-refresh', tooltip_text=_('Refresh systemd items'))
        self._filter_entry = Gtk.SearchEntry(tooltip_text=_('Filter systemd items'))
        self._hamburger_button = Gtk.MenuButton(icon_name='open-menu', tooltip_text=_('Hamburger'))
        self._hamburger_button.set_popover(HamburgerMenu())

        self.pack_start(self._refresh_button)
        self.pack_start(self._filter_entry)
        self.pack_end(self._hamburger_button)

        self._refresh_button.connect('clicked', lambda rb: self.emit('refresh-clicked', rb))
        self._filter_entry.connect('search-changed', lambda fe: self.emit('filter-changed', fe))

    def get_refresh_button(self) -> Gtk.Button:
        return self._refresh_button

    def get_filter_entry(self) -> Gtk.SearchEntry:
        return self._filter_entry

    def get_hamburger_button(self) -> Gtk.MenuButton:
        return self._hamburger_button


GObject.signal_new('refresh-clicked', TitleBar, GObject.SignalFlags.RUN_LAST, None, (Gtk.Button,))
GObject.signal_new('filter-changed', TitleBar, GObject.SignalFlags.RUN_LAST, None, (Gtk.SearchEntry,))


class StatusBar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, orientation=Gtk.Orientation.HORIZONTAL,
                         margin_start=10, margin_end=10, margin_top=10, margin_bottom=10)

        self._version_label = Gtk.Label(hexpand=True, halign=Gtk.Align.START,
                                        tooltip_text=_('Systemd version'))
        self._item_label = Gtk.Label(hexpand=True, halign=Gtk.Align.END,
                                     tooltip_text=_('Item status'))

        self.append(self._version_label)
        self.append(self._item_label)

    def set_version_text(self, version_text: str):
        self._version_label.set_label(version_text)

    def set_item_status(self, listed_n_items: int, total_n_items):
        item_text = f'{listed_n_items} item is listed from a total of {total_n_items}'
        self._item_label.set_label(item_text)


class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, width_request=960, height_request=600)

        title_bar = TitleBar()
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._systemd_notebook = SystemdNotebook()
        self._status_bar = StatusBar()
        for page_num in range(0, self._systemd_notebook.get_n_pages()):
            tab_window = self._systemd_notebook.get_tab_window(page_num)
            tab_window.set_filter_entry(title_bar.get_filter_entry())

        main_box.append(self._systemd_notebook)
        main_box.append(self._status_bar)

        self.set_titlebar(title_bar)
        self.set_child(main_box)

        self.set_actions()

        self.connect('show', self.on_show_main_window)
        title_bar.connect('refresh-clicked', lambda tb, rb: self.refresh_systemd_items())
        title_bar.connect('filter-changed', lambda tb, fe: self.refresh_systemd_filter())
        self._systemd_notebook.connect('switch-page', lambda sn, tw, pn: self.refresh_systemd_items(pn))

    def set_actions(self):
        action_group = Gio.SimpleActionGroup()
        action = Gio.SimpleAction(name='about')
        action.connect('activate', lambda a, p: AboutDialog(transient_for=self).show())
        action_group.add_action(action)
        action = Gio.SimpleAction(name='exit')
        action.connect('activate', lambda a, p: self.get_application().quit())
        action_group.add_action(action)
        self.insert_action_group('hamburger', action_group)

        action_group = Gio.SimpleActionGroup()
        for action_name in ('status', 'start', 'stop', 'restart', 'enable', 'disable', 'reenable'):
            action = Gio.SimpleAction(name=action_name, parameter_type=GLib.VariantType('(ssss)'))
            action.connect('activate', lambda a, p: self.on_systemctl_item_activate(p))
            action_group.add_action(action)
        self.insert_action_group('systemctl', action_group)

    def on_show_main_window(self, main_window: 'MainWindow'):
        try:
            self._status_bar.set_version_text(Systemctl().run_version_command())
        except SystemctlError as error:
            ErrorDialog(transient_for=self, error_text=error.args[0]).show()
        self.refresh_systemd_items()

    def refresh_systemd_filter(self, page_num: int | None = None):
        tab_window = self._systemd_notebook.get_tab_window(page_num)
        item_filter = tab_window.get_item_filter()
        item_store = tab_window.get_item_list_store()
        item_filter_model = tab_window.get_item_filter_model()

        item_filter.changed(Gtk.FilterChange.DIFFERENT)
        self._status_bar.set_item_status(item_filter_model.get_n_items(), item_store.get_n_items())

    def refresh_systemd_items(self, page_num: int | None = None):
        tab_window = self._systemd_notebook.get_tab_window(page_num)
        item_store = tab_window.get_item_list_store()
        item_filter_model = tab_window.get_item_filter_model()
        list_type = tab_window.get_list_type()
        connect_type = tab_window.get_connect_type()

        try:
            item_store.remove_all()
            for props in Systemctl().run_list_command(list_type, connect_type):
                item_store.append(SystemdItem(props))
        except SystemctlError as error:
            ErrorDialog(transient_for=self, error_text=error.args[0]).show()
        self._status_bar.set_item_status(item_filter_model.get_n_items(), item_store.get_n_items())

    def on_systemctl_item_activate(self, p: ()):
        item_command = SystemdItemCommand[p[2]]
        connect_type = SystemdConnectType[p[3]]

        if p[0].endswith('@'):
            param_dialog = ParamSetterDialog(transient_for=self)
            param_dialog.get_run_button().connect('clicked', lambda b: self.run_systemd_item_command(
                item_command, f'{p[0]}{param_dialog.get_param_text()}.{p[1]}', connect_type))
            param_dialog.show()
        else:
            self.run_systemd_item_command(item_command, f'{p[0]}.{p[1]}', connect_type)

    def run_systemd_item_command(self, item_command: SystemdItemCommand,
                                 item_id: str, connect_type: SystemdConnectType):
        try:
            result = Systemctl().run_item_command(item_command, item_id, connect_type)
            if item_command == SystemdItemCommand.STATUS:
                StatusDialog(transient_for=self, status_text=result).show()
        except SystemctlError as error:
            ErrorDialog(transient_for=self, error_text=error.args[0]).show()
