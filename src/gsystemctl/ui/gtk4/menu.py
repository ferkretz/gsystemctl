from gi.repository import Gio, GLib, Gtk

from gsystemctl import *
from gsystemctl.systemctl import SystemdConnectType


class HamburgerMenu(Gtk.PopoverMenu):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, has_arrow=False)

        menu = Gio.Menu()
        section = Gio.Menu()
        section.append('About', 'hamburger.about')
        section.append('Settings', 'hamburger.settings')
        menu.append_section(None, section)
        section = Gio.Menu()
        section.append('Exit', 'hamburger.exit')
        menu.append_section(None, section)

        self.set_menu_model(menu)


class SystemctlMenu(Gtk.PopoverMenu):
    def __init__(self, item_name: str, item_type: str, connect_type: SystemdConnectType, **kwargs):
        super().__init__(**kwargs, has_arrow=False)

        self._item_name = item_name
        self._item_type = item_type
        self._connect_type = connect_type

        menu = Gio.Menu()
        section = Gio.Menu()
        self._append_item(section, _('Runtime information'), 'status')
        menu.append_section(None, section)
        section = Gio.Menu()
        self._append_item(section, _('Start'), 'start')
        self._append_item(section, _('Stop'), 'stop')
        self._append_item(section, _('Restart'), 'restart')
        menu.append_section(None, section)
        section = Gio.Menu()
        self._append_item(section, _('Enable'), 'enable')
        self._append_item(section, _('Disable'), 'disable')
        self._append_item(section, _('Reenable'), 'reenable')
        menu.append_section(None, section)

        self.set_menu_model(menu)

    def _append_item(self, section: Gio.Menu, label: str, action_name: str):
        item = Gio.MenuItem()
        item.set_label(label)
        target_value = GLib.Variant('(ssss)', (self._item_name, self._item_type,
                                               action_name.upper(), self._connect_type.name))
        item.set_action_and_target_value(f'systemctl.{action_name}', target_value)
        section.append_item(item)
