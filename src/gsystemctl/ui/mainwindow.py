from __future__ import annotations

import threading
from typing import cast

from gi.repository import Gdk, Gio, GLib, Gtk

from gsystemctl.globals import *
from gsystemctl.config import Config
from gsystemctl.systemctl import Systemctl, SystemctlError, SystemdItemCommand
from gsystemctl.ui.dialogs import AboutDialog, ErrorDialog, ParamSetterDialog, SettingsDialog, StatusDialog
from gsystemctl.ui.menus import HamburgerMenu, SystemctlMenu
from gsystemctl.ui.systemditem import SystemdItem
from gsystemctl.ui.systemditemnotebook import SystemdNotebook
from gsystemctl.ui.systemditemscrolled import SystemdItemScrolled


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, width_request=960, height_request=600)

        self._config = Config()

        self._auto_save = self._config.get('general-policy', 'auto-save')
        self._auto_refresh = self._config.get('general-policy', 'auto-refresh')

        self._systemctl = Systemctl()
        self._systemctl.set_path(self._config.get('systemctl', 'path'))
        self._systemctl.set_encoding(self._config.get('systemctl', 'encoding'))

        title_bar = Gtk.HeaderBar()
        self._refresh_button = Gtk.Button(icon_name='view-refresh', tooltip_text=_('Refresh systemd items'))
        self._filter_entry = Gtk.SearchEntry(tooltip_text=_('Filter systemd items'))
        self._filter_entry.set_text(self._config.get('item-filter', 'text'))
        self._case_button = Gtk.ToggleButton(icon_name='format-text-rich', tooltip_text=_('Case sensitive search'))
        self._case_button.set_active(self._config.get('item-filter', 'case-sensitive'))
        self._hamburger_button = Gtk.MenuButton(icon_name='open-menu', tooltip_text=_('Hamburger'))
        self._hamburger_button.set_popover(HamburgerMenu())
        if self._auto_save:
            self._filter_entry.set_text(self._config.get('item-filter', 'text'))
            self._case_button.set_active(self._config.get('item-filter', 'case-sensitive'))
        title_bar.pack_start(self._refresh_button)
        title_bar.pack_start(self._filter_entry)
        title_bar.pack_start(self._case_button)
        title_bar.pack_end(self._hamburger_button)

        self._systemd_notebook = SystemdNotebook()
        if self._auto_save:
            self._systemd_notebook.set_current_page(self._config.get('item-notebook', 'active-page'))
        for page_num in range(0, self._systemd_notebook.get_n_pages()):
            item_filter = self._systemd_notebook.get_tab_scrolled(page_num).get_filter()
            item_filter.set_search(self._filter_entry.get_text())
            item_filter.set_ignore_case(not self._case_button.get_active())

        status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, spacing=5,
                             margin_start=10, margin_end=10, margin_top=10, margin_bottom=10)
        self._load_spinner = Gtk.Spinner()
        self._item_status = Gtk.Label()
        status_bar.append(self._load_spinner)
        status_bar.append(self._item_status)

        self.set_titlebar(title_bar)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(self._systemd_notebook)
        main_box.append(status_bar)
        self.set_child(main_box)

        action_group = Gio.SimpleActionGroup()
        action = Gio.SimpleAction(name='about')
        action.connect('activate', self.on_hamburger_about_activate)
        action_group.add_action(action)
        action = Gio.SimpleAction(name='settings')
        action.connect('activate', self.on_hamburger_settings_activate)
        action_group.add_action(action)
        action = Gio.SimpleAction(name='exit')
        action.connect('activate', lambda a, p: self.close())
        action_group.add_action(action)
        self.insert_action_group('hamburger', action_group)

        action_group = Gio.SimpleActionGroup()
        for action_name in ('status', 'start', 'stop', 'restart', 'enable', 'disable', 'reenable',
                            'reload', 'isolate', 'kill', 'clean', 'freeze', 'thaw', 'preset'):
            action = Gio.SimpleAction(name=action_name)
            action.connect('activate',
                           self.on_systemctl_command_activate,
                           SystemdItemCommand[action_name.upper()])
            action_group.add_action(action)
        self.insert_action_group('systemctl', action_group)

        self.connect('show', self.on_main_window_show)
        self.connect('close-request', self.on_main_window_close)

        self._refresh_button.connect('clicked', self.on_refresh_button_clicked)
        self._filter_entry.connect('search_changed', self.on_filter_entry_search_changed)
        self._case_button.connect('toggled', self.on_case_button_toggled)
        self._systemd_notebook.connect('switch-page', self.on_systemd_notebook_switch_page)

        gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        gesture.connect('pressed', self.on_systemd_notebook_right_button_pressed)
        self._systemd_notebook.add_controller(gesture)

    def on_hamburger_about_activate(self, action: Gio.SimpleAction, parameter: GLib.Variant):
        dialog = AboutDialog(transient_for=self)
        dialog.add_button(_('Close'), lambda cb, ad: ad.close())
        dialog.show()

    def on_hamburger_settings_activate(self, action: Gio.SimpleAction, parameter: GLib.Variant):
        def save_settings(button: Gtk.Button, dialog: SettingsDialog):
            dialog.close()
            self._auto_save = dialog.get_auto_save()
            self._auto_refresh = dialog.get_auto_refresh()
            self._systemctl.set_path(dialog.get_systemctl_path())
            self._systemctl.set_encoding(dialog.get_systemctl_encoding())
            self.save_user_settings()

        settings_dialog = SettingsDialog(transient_for=self)
        settings_dialog.set_auto_save(self._auto_save)
        settings_dialog.set_auto_refresh(self._auto_refresh)
        settings_dialog.set_systemctl_path(self._systemctl.get_path())
        settings_dialog.set_systemctl_encoding(self._systemctl.get_encoding())
        settings_dialog.add_button(_('Cancel'), lambda cb, sd: sd.close())
        settings_dialog.add_button(_('Save'), save_settings)
        settings_dialog.show()

    def on_systemctl_command_activate(self, action: Gio.SimpleAction, parameter: GLib.Variant,
                                      item_command: SystemdItemCommand):
        model = self._systemd_notebook.get_tab_scrolled().get_item_view().get_model()
        item = cast(SystemdItem, cast(Gtk.SingleSelection, model).get_selected_item())

        def pre_run(item_id: str):
            self._load_spinner.set_visible(True)
            self._load_spinner.set_spinning(True)
            self._item_status.set_label(_('Running commands, please wait...'))
            self._refresh_button.set_sensitive(False)
            self._filter_entry.set_sensitive(False)
            self._case_button.set_sensitive(False)
            self._systemd_notebook.set_sensitive(False)

            thread = threading.Thread(target=run, args=[item_id])
            thread.daemon = True
            thread.start()

        def run(item_id: str):
            result = None
            error_msg = None
            try:
                result = self._systemctl.run_item_command(item_command, item_id, item.get_connect_type())
            except SystemctlError as error:
                error_msg = error.args[0]
            GLib.idle_add(lambda: on_done(result, error_msg))

        def on_done(result, error_msg):
            if not error_msg:
                if item_command == SystemdItemCommand.STATUS:
                    status_dialog = StatusDialog(transient_for=self, status_text=result)
                    status_dialog.add_button(_('Close'), lambda cb, sd: sd.close())
                    status_dialog.show()
                self.refresh_systemd_items()

            self._load_spinner.set_visible(False)
            self._load_spinner.set_spinning(False)
            self.refresh_item_status()
            self._refresh_button.set_sensitive(True)
            self._filter_entry.set_sensitive(True)
            self._case_button.set_sensitive(True)
            self._systemd_notebook.set_sensitive(True)

            if error_msg:
                error_dialog = ErrorDialog(transient_for=self, error_text=error_msg)
                error_dialog.add_button(_('Close'), lambda cb, ed: ed.close())
                error_dialog.show()

        if item.is_special():
            param_dialog = ParamSetterDialog(transient_for=self)
            param_dialog.add_button(_('Cancel'), lambda cb, pd: pd.close())
            param_dialog.add_button(_('Run'), lambda rb, pd: (
                pd.close(), pre_run(item.get_id(param_dialog.get_param_text()))
            ))
            param_dialog.show()
        else:
            pre_run(item.get_id())

    def on_main_window_show(self, main_window: MainWindow):
        if self._auto_refresh:
            self.refresh_systemd_items()

    def on_main_window_close(self, main_window: MainWindow):
        self.save_user_settings()

    def on_refresh_button_clicked(self, button: Gtk.Button):
        self.refresh_systemd_items()

    def on_filter_entry_search_changed(self, filter_entry: Gtk.SearchEntry):
        for page_num in range(0, self._systemd_notebook.get_n_pages()):
            item_filter = self._systemd_notebook.get_tab_scrolled(page_num).get_filter()
            item_filter.set_search(filter_entry.get_text())
        self.refresh_item_status()

    def on_case_button_toggled(self, case_button: Gtk.ToggleButton):
        for page_num in range(0, self._systemd_notebook.get_n_pages()):
            item_filter = self._systemd_notebook.get_tab_scrolled(page_num).get_filter()
            item_filter.set_ignore_case(not case_button.get_active())
        self.refresh_item_status()

    def on_systemd_notebook_switch_page(self, systemd_notebook: Gtk.Notebook,
                                        tab_scrolled: SystemdItemScrolled, page_num: int):
        if self._auto_refresh:
            self._systemd_notebook.grab_focus()
            self.refresh_systemd_items(page_num)

    def on_systemd_notebook_right_button_pressed(self, gesture_click: Gtk.GestureClick,
                                                 n_press: int, x: int, y: int):
        bound = Gdk.Rectangle()
        bound.x = x
        bound.y = y

        popover = SystemctlMenu()
        popover.set_pointing_to(bound)
        popover.set_parent(self._systemd_notebook)
        popover.popup()

    def refresh_systemd_items(self, page_num: int | None = None):
        tab_window = self._systemd_notebook.get_tab_scrolled(page_num)
        item_store = tab_window.get_item_list_store()
        item_type = tab_window.get_item_type()
        connect_type = tab_window.get_connect_type()

        def run():
            item_list = None
            error_msg = None
            try:
                item_list = self._systemctl.run_list_command(item_type, connect_type)
            except SystemctlError as error:
                error_msg = error.args[0]
            GLib.idle_add(lambda: on_done(item_list, error_msg))

        def on_done(item_list, error_msg):
            if not error_msg:
                item_store.remove_all()
                for props in item_list:
                    item_store.append(SystemdItem(props, item_type, connect_type))

            self._load_spinner.set_visible(False)
            self._load_spinner.set_spinning(False)
            self.refresh_item_status()
            self._refresh_button.set_sensitive(True)
            self._filter_entry.set_sensitive(True)
            self._case_button.set_sensitive(True)
            self._systemd_notebook.set_sensitive(True)

            if error_msg:
                error_dialog = ErrorDialog(transient_for=self, error_text=error_msg)
                error_dialog.add_button(_('Close'), lambda cb, ed: ed.close())
                error_dialog.show()

        self._load_spinner.set_visible(True)
        self._load_spinner.set_spinning(True)
        self._item_status.set_label(_('Loading units, please wait...'))
        self._refresh_button.set_sensitive(False)
        self._filter_entry.set_sensitive(False)
        self._case_button.set_sensitive(False)
        self._systemd_notebook.set_sensitive(False)

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

    def refresh_item_status(self):
        tab_scrolled = self._systemd_notebook.get_tab_scrolled()
        n_filtered_items = tab_scrolled.get_n_filtered_items()
        n_total_items = tab_scrolled.get_n_total_items()
        item_text = f'{n_filtered_items} item is listed from a total of {n_total_items}'
        self._item_status.set_label(item_text)

    def save_user_settings(self):
        self._config.set('general-policy', 'auto-save', self._auto_save)
        self._config.set('general-policy', 'auto-refresh', self._auto_refresh)
        self._config.set('systemctl', 'path', self._systemctl.get_path())
        self._config.set('systemctl', 'encoding', self._systemctl.get_encoding())
        self._config.set('item-filter', 'text', self._filter_entry.get_text())
        self._config.set('item-filter', 'case-sensitive', self._case_button.get_active())
        self._config.save()
