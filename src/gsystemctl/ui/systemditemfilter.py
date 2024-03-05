from gi.repository import Gtk

from gsystemctl.ui.systemditem import SystemdItem


class SystemdItemFilter(Gtk.Filter):
    def __init__(self, **kwargs):
        self._ignore_case: bool = kwargs.pop('ignore_case', True)
        self._search: str | None = kwargs.pop('search', None)

        super().__init__(**kwargs)

    def do_get_strictness(self) -> Gtk.FilterMatch:
        return self.get_strictness()

    def get_strictness(self) -> Gtk.FilterMatch:
        if not self._search:
            return Gtk.FilterMatch.ALL

        return Gtk.FilterMatch.SOME

    def do_match(self, item: SystemdItem | None = None) -> bool:
        return self.match(item)

    def match(self, item: SystemdItem) -> bool:
        if not self._search:
            return True

        for prop in item.get_props():
            if self._ignore_case:
                if prop.lower().find(self._search.lower()) >= 0:
                    return True
            else:
                if prop.find(self._search) >= 0:
                    return True

        return False

    def set_ignore_case(self, ignore_case: bool):
        if self._ignore_case == ignore_case:
            return

        self._ignore_case = ignore_case
        self.changed(Gtk.FilterChange.LESS_STRICT if ignore_case else Gtk.FilterChange.MORE_STRICT)

    def set_search(self, search: str | None):
        if self._search == search:
            return

        if not search:
            change = Gtk.FilterChange.LESS_STRICT
        elif not self._search:
            change = Gtk.FilterChange.MORE_STRICT
        else:
            change = Gtk.FilterChange.DIFFERENT

        self._search = search
        self.changed(change)

    def get_ignore_case(self) -> bool:
        return self._ignore_case

    def get_search(self) -> str | None:
        return self._search
