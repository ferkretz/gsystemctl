import os
from typing import Sequence

from gi.repository import GObject

from gsystemctl.systemctl import SystemdConnectType, SystemdItemType


class SystemdItem(GObject.Object):
    def __init__(self, props: Sequence, item_type: SystemdItemType,
                 connect_type: SystemdConnectType, **kwargs):
        super().__init__(**kwargs)

        self._item_type = item_type
        self._connect_type = connect_type

        id_arr = os.path.splitext(props[0])
        if item_type == SystemdItemType.UNIT:
            if len(props) != 5:
                raise TypeError(_(f'Unit item requires exactly 5 properties ({len(props)} given)'))
            self._props = (id_arr[0], id_arr[1][1:], props[1], props[2], props[3], props[4])
        else:
            if len(props) != 3:
                raise TypeError(_(f'Unit template requires exactly 3 properties ({len(props)} given)'))
            self._props = (id_arr[0], id_arr[1][1:], props[1], props[2])

    def get_item_type(self) -> SystemdItemType:
        return self._item_type

    def get_connect_type(self) -> SystemdConnectType:
        return self._connect_type

    def get_props(self) -> ():
        return self._props

    def get_prop(self, index) -> str:
        return self._props[index]

    def is_special(self) -> bool:
        return self.get_prop(0).endswith('@')

    def get_id(self, params: str | None = None) -> str:
        if params is None:
            params = ''

        return f'{self.get_prop(0)}{params}.{self.get_prop(1)}'
