from typing import cast

from gi.repository import Gtk

from gsystemctl.globals import *
from gsystemctl.systemctl import SystemdConnectType, SystemdItemType
from gsystemctl.ui.systemditemscrolled import SystemdItemScrolled


class SystemdNotebook(Gtk.Notebook):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, vexpand=True, enable_popup=True, show_tabs=True)

        for list_type, connect_type, tab_title in (
                (SystemdItemType.UNIT, SystemdConnectType.SYSTEM, _('System units')),
                (SystemdItemType.TEMPLATE, SystemdConnectType.SYSTEM, _('System templates')),
                (SystemdItemType.UNIT, SystemdConnectType.USER, _('User units')),
                (SystemdItemType.TEMPLATE, SystemdConnectType.USER, _('User templates'))
        ):
            tab_scrolled = SystemdItemScrolled(list_type, connect_type)
            tab_label = Gtk.Label(label=tab_title)
            self.append_page(tab_scrolled, tab_label)

    def get_tab_scrolled(self, page_num: int | None = None) -> SystemdItemScrolled:
        if page_num is None:
            page_num = self.get_current_page()

        return cast(SystemdItemScrolled, self.get_nth_page(page_num))
