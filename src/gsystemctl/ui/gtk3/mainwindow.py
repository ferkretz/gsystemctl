import os

from gi.repository import Gdk, Gio, GLib, Gtk, GdkPixbuf

from gsystemctl import *
from gsystemctl.systemctl import *
from gsystemctl.ui.gtk3 import *


@Gtk.Template.from_file(os.path.join(GLADE_UI_PATH, 'mainwindow.ui'))
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    header_bar: Gtk.HeaderBar = Gtk.Template.Child()
    notebook: Gtk.Notebook = Gtk.Template.Child()
    page_status: Gtk.Label = Gtk.Template.Child()
    page_selector: Gtk.MenuButton = Gtk.Template.Child()

    MODEL_PROPS = {
        'units': {
            'page-title': 'loaded {} units',
            'column-titles': ['Type', 'Name', 'Load state', 'Active state', 'Sub state', 'Description'],
            'store': Gtk.ListStore(str, str, str, str, str, str),
            'status': '{} loaded units listed',
            'list-type': SystemctlListType.UNITS
        },
        'files': {
            'page-title': '{} template files',
            'column-titles': ['Type', 'Name', 'File state', 'Preset'],
            'store': Gtk.ListStore(str, str, str, str),
            'status': '{} unit files listed',
            'list-type': SystemctlListType.UNITS_FILES
        }
    }

    NOTEBOOK_PROPS = [
        MODEL_PROPS['units'] | {'call-type': SystemctlCallType.SYSTEM},
        MODEL_PROPS['files'] | {'call-type': SystemctlCallType.SYSTEM},
        MODEL_PROPS['units'] | {'call-type': SystemctlCallType.USER},
        MODEL_PROPS['files'] | {'call-type': SystemctlCallType.USER},
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_actions()
        self.init_components()

    def init_components(self):
        self.header_bar.set_title(APP_NAME)

        # Add pages for notebook
        for i, page_props in enumerate(self.NOTEBOOK_PROPS):
            view = Gtk.TreeView()
            self.NOTEBOOK_PROPS[i] |= {'view': view}
            for j, title in enumerate(page_props['column-titles']):
                column = Gtk.TreeViewColumn(_(title), Gtk.CellRendererText(), text=j)
                view.append_column(column)
                column.set_sort_column_id(j)
                column.set_resizable(True)
                column.set_sizing(Gtk.TreeViewColumnSizing(Gtk.TreeViewColumnSizing.FIXED))
            view.set_model(page_props['store'])
            view.connect('button-press-event', self.on_view_button_press_event)
            scrollable = Gtk.ScrolledWindow()
            scrollable.add(view)
            self.notebook.append_page(scrollable)
        self.notebook.show_all()

        # Add page menu for header
        page_menu = Gtk.Menu()

        item = Gtk.MenuItem(_('Refresh page'))
        item.set_action_name('win.refresh-page')
        page_menu.append(item)
        item = Gtk.SeparatorMenuItem()
        page_menu.append(item)
        for i, page_props in enumerate(self.NOTEBOOK_PROPS):
            item = Gtk.MenuItem(_(page_props['page-title']).format(_(page_props['call-type'])).capitalize())
            item.set_action_name('win.select-page')
            item.set_action_target_value(GLib.Variant('i', i))
            page_menu.append(item)
        page_menu.show_all()
        self.page_selector.set_popup(page_menu)

        # Setup page
        self.refresh_page()

    def init_actions(self):
        action = Gio.SimpleAction(name='refresh-page')
        action.connect('activate', self.refresh_page_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='select-page',
                                  parameter_type=GLib.VariantType('i'),
                                  state=GLib.Variant('i', 0))
        action.connect('change-state', self.select_page_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='about')
        action.connect('activate', self.about_action)
        self.add_action(action)

        action = Gio.SimpleAction(name='systemctl-status')
        action.connect('activate', self.systemctl_status_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='systemctl-start')
        action.connect('activate', self.systemctl_start_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='systemctl-stop')
        action.connect('activate', self.systemctl_stop_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='systemctl-restart')
        action.connect('activate', self.systemctl_restart_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='systemctl-enable')
        action.connect('activate', self.systemctl_enable_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='systemctl-disable')
        action.connect('activate', self.systemctl_disable_action)
        self.add_action(action)
        action = Gio.SimpleAction(name='systemctl-reenable')
        action.connect('activate', self.systemctl_reenable_action)
        self.add_action(action)

    def refresh_page(self):
        page_props = self.NOTEBOOK_PROPS[self.notebook.get_current_page()]

        try:
            page_props['store'].clear()
            row_count = 0
            for row in Systemctl().list(page_props['list-type'], page_props['call-type']):
                id_arr = os.path.splitext(row[0])
                del (row[0])
                page_props['store'].append([id_arr[1][1:], id_arr[0]] + row)
                row_count += 1
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()

        self.header_bar.set_subtitle(_(page_props['page-title']).format(_(page_props['call-type'])))
        self.page_status.set_label(_(page_props['status']).format(row_count))

    def refresh_page_action(self, action, value):
        self.refresh_page()

    def select_page_action(self, action, value):
        selected_page = value.get_int32()

        if self.notebook.get_current_page() != selected_page:
            self.notebook.set_current_page(selected_page)
            self.refresh_page()

    def on_view_button_press_event(self, tree_view: Gtk.TreeView, event_button: Gdk.EventButton):
        if event_button.button == Gdk.BUTTON_SECONDARY:
            tree_view.set_cursor(tree_view.get_path_at_pos(int(event_button.x), int(event_button.y))[0])
            model, tree_iter = tree_view.get_selection().get_selected()

            unit_name = model.get_value(tree_iter, 1)
            unit_type = model.get_value(tree_iter, 0)
            unit_id = f'{unit_name}.{unit_type}'
            call_type = self.NOTEBOOK_PROPS[self.notebook.get_current_page()]['call-type']

            actions = {
                'status': False,
                'start': False,
                'stop': False,
                'restart': False,
                'enable': False,
                'disable': False,
                'reenable': False
            }

            if not unit_name.endswith('@'):
                actions['status'] = True
                if Systemctl().is_active(unit_id, call_type) == 'active':
                    actions['stop'] = True
                    actions['restart'] = True
                else:
                    actions['start'] = True

            enabled = Systemctl().is_enabled(unit_id, call_type)
            if enabled not in ['masked', 'masked-runtime', 'bad', 'not-found', 'alias']:
                if enabled in ['enabled', 'enabled-runtime']:
                    actions['disable'] = True
                    actions['reenable'] = True
                else:
                    actions['enable'] = True

            for key, value in actions.items():
                self.lookup_action(f'systemctl-{key}').set_enabled(value)

            menu = Gtk.Menu()
            menu.add(Gtk.MenuItem(label=('Runtime information'), action_name='win.systemctl-status'))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.MenuItem(label=('Start'), action_name='win.systemctl-start'))
            menu.add(Gtk.MenuItem(label=('Stop'), action_name='win.systemctl-stop'))
            menu.add(Gtk.MenuItem(label=('Restart'), action_name='win.systemctl-restart'))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.MenuItem(label=('Enable'), action_name='win.systemctl-enable'))
            menu.add(Gtk.MenuItem(label=('Disable'), action_name='win.systemctl-disable'))
            menu.add(Gtk.MenuItem(label=('Reenable'), action_name='win.systemctl-reenable'))
            menu.show_all()
            menu.attach_to_widget(self)
            menu.popup_at_pointer(event_button)

    def about_action(self, action, value):
        dialog = Gtk.AboutDialog(
            modal=True, transient_for=self,
            program_name=APP_NAME,
            version=APP_VERSION,
            comments=APP_DESCRIPTION,
            license_type=Gtk.License.GPL_3_0,
            copyright=APP_COPYRIGHT,
            website=APP_WEBSITE,
            logo=GdkPixbuf.Pixbuf.new_from_file(os.path.join(IMAGE_PATH, 'gsystemctl.png'))
        )
        dialog.run()
        dialog.destroy()

    def get_selected_unit_id(self):
        page_props = self.NOTEBOOK_PROPS[self.notebook.get_current_page()]
        model, tree_iter = page_props['view'].get_selection().get_selected()
        return f'{model.get_value(tree_iter, 1)}.{model.get_value(tree_iter, 0)}'

    def get_selected_call_type(self):
        page_props = self.NOTEBOOK_PROPS[self.notebook.get_current_page()]
        return page_props['call-type']

    def systemctl_status_action(self, action, value):
        try:
            status = Systemctl().status(self.get_selected_unit_id(), self.get_selected_call_type())
            text_view = Gtk.TextView(editable=False, monospace=True, visible=True)
            text_view.get_buffer().set_text(status)
            dialog = Gtk.Dialog(
                modal=True, transient_for=self,
                title=_('Runtime status information'), width_request=640, height_request=320)
            dialog.get_content_area().add(Gtk.ScrolledWindow(child=text_view, vexpand=True, visible=True))
            dialog.add_button('Close', Gtk.ButtonsType.CLOSE)
            dialog.run()
            dialog.destroy()
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()

    def systemctl_start_action(self, action, value):
        try:
            Systemctl().start(self.get_selected_unit_id(), self.get_selected_call_type())
            self.refresh_page()
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()

    def systemctl_stop_action(self, action, value):
        try:
            Systemctl().stop(self.get_selected_unit_id(), self.get_selected_call_type())
            self.refresh_page()
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()

    def systemctl_restart_action(self, action, value):
        try:
            Systemctl().restart(self.get_selected_unit_id(), self.get_selected_call_type())
            self.refresh_page()
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()

    def systemctl_enable_action(self, action, value):
        try:
            Systemctl().enable(self.get_selected_unit_id(), self.get_selected_call_type())
            self.refresh_page()
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()

    def systemctl_disable_action(self, action, value):
        try:
            Systemctl().disable(self.get_selected_unit_id(), self.get_selected_call_type())
            self.refresh_page()
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()

    def systemctl_reenable_action(self, action, value):
        try:
            Systemctl().reenable(self.get_selected_unit_id(), self.get_selected_call_type())
            self.refresh_page()
        except SystemctlError as error:
            dialog = Gtk.MessageDialog(
                modal=True, transient_for=self,
                buttons=Gtk.ButtonsType.CLOSE, message_type=Gtk.MessageType.ERROR,
                text=_('Error'), secondary_text=error.args[0])
            dialog.run()
            dialog.destroy()
