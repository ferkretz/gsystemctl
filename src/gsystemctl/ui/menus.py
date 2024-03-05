from gi.repository import Gio, Gtk

from gsystemctl.globals import *


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
    def __init__(self, **kwargs):
        super().__init__(**kwargs, has_arrow=False)

        menu = Gio.Menu()
        section = Gio.Menu()
        section.append(_('Runtime information'), 'systemctl.status')
        menu.append_section(None, section)
        section = Gio.Menu()
        section.append(_('Start'), 'systemctl.start')
        section.append(_('Stop'), 'systemctl.stop')
        section.append(_('Restart'), 'systemctl.restart')
        menu.append_section(None, section)
        section = Gio.Menu()
        section.append(_('Enable'), 'systemctl.enable')
        section.append(_('Disable'), 'systemctl.disable')
        section.append(_('Reenable'), 'systemctl.reenable')
        menu.append_section(None, section)
        section = Gio.Menu()
        submenu = Gio.Menu()
        subsection = Gio.Menu()
        subsection.append(_('Reload'), 'systemctl.reload')
        subsection.append(_('Isolate'), 'systemctl.isolate')
        subsection.append(_('Kill'), 'systemctl.kill')
        subsection.append(_('Clean'), 'systemctl.clean')
        subsection.append(_('Freeze'), 'systemctl.freeze')
        subsection.append(_('Thaw'), 'systemctl.thaw')
        submenu.append_section(None, subsection)
        subsection = Gio.Menu()
        subsection.append(_('Preset'), 'systemctl.preset')
        submenu.append_section(None, subsection)
        section.append_submenu(_('Advanced'), submenu)
        menu.append_section(None, section)

        self.set_menu_model(menu)
