from gi.repository import Gio, Gtk

from gsystemctl.globals import *
from gsystemctl.systemctl import SystemdConnectType, SystemdItemType
from gsystemctl.ui.systemditemfactory import SystemdItemFactory
from gsystemctl.ui.systemditemfilter import SystemdItemFilter


class SystemdItemScrolled(Gtk.ScrolledWindow):
    def __init__(self, item_type: SystemdItemType, connect_type: SystemdConnectType, **kwargs):
        super().__init__(**kwargs)

        self._item_type = item_type
        self._connect_type = connect_type

        self._column_view = Gtk.ColumnView(show_column_separators=True, show_row_separators=True)
        self._item_store = Gio.ListStore()
        self._item_filter = SystemdItemFilter()
        self._item_filter_model = Gtk.FilterListModel(model=self._item_store, filter=self._item_filter)
        self._item_selection = Gtk.SingleSelection(model=self._item_filter_model)

        for column_index, column_title in enumerate(self.get_column_titles()):
            factory = SystemdItemFactory(self, column_index)
            view_column = Gtk.ColumnViewColumn(title=column_title, factory=factory, resizable=True)
            self._column_view.append_column(view_column)
        self._column_view.set_model(self._item_selection)

        self.set_child(self._column_view)

    def get_column_titles(self) -> ():
        if self._item_type == SystemdItemType.UNIT:
            return _('Name'), _('Type'), _('Load state'), _('Active state'), _('Sub state'), _('Description')
        else:
            return _('Name'), _('Type'), _('File state'), _('Preset')

    def get_item_type(self) -> SystemdItemType:
        return self._item_type

    def get_connect_type(self) -> SystemdConnectType:
        return self._connect_type

    def get_filter(self) -> SystemdItemFilter:
        return self._item_filter

    def get_n_total_items(self) -> int:
        return self._item_store.get_n_items()

    def get_n_filtered_items(self) -> int:
        return self._item_filter_model.get_n_items()

    def get_item_list_store(self) -> Gio.ListStore:
        return self._item_store

    def get_item_view(self) -> Gtk.ColumnView:
        return self._column_view
