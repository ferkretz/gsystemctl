import os
from typing import cast, Sequence

from gi.repository import Gdk, Gio, GObject, Gtk

from gsystemctl import *
from gsystemctl.systemctl import SystemdConnectType, SystemdListType
from gsystemctl.ui.gtk4.menu import SystemctlMenu


class SystemdItem(GObject.Object):
    def __init__(self, props: Sequence, **kwargs):
        super().__init__(**kwargs)

        id_arr = os.path.splitext(props[0])
        if len(props) == 5:
            self._props = (id_arr[0], id_arr[1][1:], props[1], props[2], props[3], props[4])
        else:
            self._props = (id_arr[0], id_arr[1][1:], props[1], props[2])

    def get_props(self):
        return self._props

    def get_prop(self, index) -> str:
        return self._props[index]


class SystemdWindow(Gtk.ScrolledWindow):
    def __init__(self, list_type: SystemdListType, connect_type: SystemdConnectType, **kwargs):
        self._filter_entry: Gtk.SearchEntry | None = kwargs.pop('filter_entry', None)

        super().__init__(**kwargs)

        self._list_type = list_type
        self._connect_type = connect_type

        self._column_view = Gtk.ColumnView(
            show_column_separators=True,
            show_row_separators=True,
            single_click_activate=True
        )

        self._item_store = Gio.ListStore()
        self._item_filter = Gtk.CustomFilter()
        self._item_filter.set_filter_func(self._item_filter_func)
        self._item_filter_model = Gtk.FilterListModel(model=self._item_store, filter=self._item_filter)
        self._item_selection = Gtk.SingleSelection(model=self._item_filter_model)

        for column_index, column_title in enumerate(self._get_column_titles()):
            factory = Gtk.SignalListItemFactory()
            factory.connect('setup', self._item_setup, self._get_item_nat_chars()[column_index])
            factory.connect('bind', self._item_bind, column_index)
            view_column = Gtk.ColumnViewColumn(title=column_title, factory=factory, resizable=True)
            self._column_view.append_column(view_column)
        self._column_view.set_model(self._item_selection)

        self.set_child(self._column_view)

    def _get_column_titles(self) -> ():
        if self._list_type == SystemdListType.UNIT:
            return _('Name'), _('Type'), _('Load state'), _('Active state'), _('Sub state'), _('Description')
        else:
            return _('Name'), _('Type'), _('File state'), _('Preset')

    def _get_item_nat_chars(self) -> ():
        if self._list_type == SystemdListType.UNIT:
            return 35, 8, 8, 8, 8, 70
        else:
            return 35, 8, 8, 8

    @staticmethod
    def _item_setup(factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell, nat_chars: int):
        inscription = Gtk.Inscription()
        inscription.set_nat_chars(nat_chars)
        inscription.set_hexpand(True)
        cell.set_child(inscription)

    def _item_bind(self, factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell, column_index: int):
        inscription: Gtk.Inscription = cell.get_child()
        item: SystemdItem = cell.get_item()
        inscription.set_text(item.get_prop(column_index))
        inscription.set_tooltip_text(f'{item.get_prop(0)}.{item.get_prop(1)}')

    def _item_filter_func(self, item: SystemdItem) -> bool:
        if not self._filter_entry:
            return True

        filter_text = self._filter_entry.get_text()

        if not filter_text:
            return True

        for prop in item.get_props():
            if prop.lower().find(filter_text.lower()) >= 0:
                return True

        return False

    def set_filter_entry(self, filter_entry: Gtk.SearchEntry):
        self._filter_entry = filter_entry

    def get_filter_entry(self) -> Gtk.SearchEntry:
        return self._filter_entry

    def get_list_type(self) -> SystemdListType:
        return self._list_type

    def get_connect_type(self) -> SystemdConnectType:
        return self._connect_type

    def get_item_list_store(self) -> Gio.ListStore:
        return self._item_store

    def get_item_filter_model(self) -> Gtk.FilterListModel:
        return self._item_filter_model

    def get_item_selection(self) -> Gtk.SingleSelection:
        return self._item_selection

    def get_item_filter(self) -> Gtk.CustomFilter:
        return self._item_filter

    def get_item_view(self) -> Gtk.ColumnView:
        return self._column_view


class SystemdNotebook(Gtk.Notebook):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, vexpand=True, enable_popup=True, show_tabs=True)

        for list_type, connect_type, tab_title in (
                (SystemdListType.UNIT, SystemdConnectType.SYSTEM, _('System units')),
                (SystemdListType.TEMPLATE, SystemdConnectType.SYSTEM, _('System templates')),
                (SystemdListType.UNIT, SystemdConnectType.USER, _('User units')),
                (SystemdListType.TEMPLATE, SystemdConnectType.USER, _('User templates'))
        ):
            tab_window = SystemdWindow(list_type, connect_type)
            tab_label = Gtk.Label(label=tab_title)
            self.append_page(tab_window, tab_label)

            # add right button gesture for running a command
            gesture = Gtk.GestureClick(button=Gdk.BUTTON_SECONDARY)
            gesture.connect('pressed', self._on_tab_window_right_button_pressed, tab_window)
            tab_window.get_item_view().add_controller(gesture)

    def _on_tab_window_right_button_pressed(self, gesture_click: Gtk.GestureClick,
                                            n_press: int, x: int, y: int, tab_window: SystemdWindow):
        view = cast(Gtk.ColumnView, gesture_click.get_widget())
        # disable 'hover select'
        view.set_single_click_activate(False)

        bound = Gdk.Rectangle()
        bound.x = x
        bound.y = y

        item = cast(SystemdItem, cast(Gtk.SingleSelection, view.get_model()).get_selected_item())
        connect_type = tab_window.get_connect_type()

        popover = SystemctlMenu(item.get_prop(0), item.get_prop(1), connect_type)
        popover.set_pointing_to(bound)
        popover.set_parent(self)  # gtk bug with view parent (a little offset, with tab labels, and frames)
        # reenable 'hover select'
        popover.connect('closed', lambda p: view.set_single_click_activate(True))
        popover.popup()

    def get_tab_window(self, page_num: int | None) -> SystemdWindow:
        if not page_num:
            page_num = self.get_current_page()

        return cast(SystemdWindow, self.get_nth_page(page_num))
