from gi.repository import Gtk

from gsystemctl.ui.systemditem import SystemdItem


class SystemdItemSorter(Gtk.CustomSorter):
    def __init__(self, column_index: int, **kwargs):
        super().__init__(**kwargs)

        self._column_index = column_index

        self.set_sort_func(self.sort_func)

    def sort_func(self, systemd_item1: SystemdItem, systemd_item2: SystemdItem, user_data) -> int:
        item1 = systemd_item1.get_prop(self._column_index)
        item2 = systemd_item2.get_prop(self._column_index)

        if item1 == item2:
            return 0

        if item1 < item2:
            return -1
        else:
            return 1
