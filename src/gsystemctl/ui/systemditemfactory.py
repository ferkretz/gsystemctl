from __future__ import annotations

from typing import TYPE_CHECKING

from gi.repository import Gdk, Gtk

from gsystemctl.systemctl import SystemdItemType
from gsystemctl.ui.systemditem import SystemdItem

if TYPE_CHECKING:
    from gsystemctl.ui.systemditemscrolled import SystemdItemScrolled


class SystemdItemFactory(Gtk.SignalListItemFactory):
    def __init__(self, item_window: SystemdItemScrolled, column_index: int, **kwargs):
        super().__init__(**kwargs)

        self._item_window = item_window
        self._column_index = column_index

        self.connect('setup', self.setup)
        self.connect('bind', self.bind)

    def get_nat_chars(self) -> int:
        if self._item_window.get_item_type() == SystemdItemType.UNIT:
            return (35, 8, 8, 8, 8, 70)[self._column_index]
        else:
            return (35, 8, 8, 8)[self._column_index]

    def setup(self, factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell):
        inscription = Gtk.Inscription()
        inscription.set_nat_chars(self.get_nat_chars())
        inscription.set_hexpand(True)
        cell.set_focusable(False)
        cell.set_child(inscription)

    def bind(self, factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell):
        inscription: Gtk.Inscription = cell.get_child()
        item: SystemdItem = cell.get_item()
        inscription.set_text(item.get_prop(self._column_index))

        cell_widget = inscription.get_parent()
        cell_widget.set_tooltip_text(item.get_id())
        gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
        gesture.connect('pressed', lambda gc, np, x, y: self._item_window.get_item_view()
                        .get_model().select_item(cell.get_position(), True))
        cell_widget.add_controller(gesture)
