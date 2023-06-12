#
# main_wdgt.py <shiftee@posteo.net>
# Based on a file with the same name in the pyqt_ui directory
#

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class MainWdgt(MainWidget, Gtk.Box):

    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.progress_bar = None
        self.progress_bar_update_interval = 1
        self.progress_bar_last_shown_value = 0

        self.b1 = Gtk.Button(label="Main Widget")
        self.centralwidget = Gtk.VBox(spacing=6)

        self.box = Gtk.VBox(spacing=6)
        self.box.pack_start(self.b1, False, False, 0)
        self.box.pack_start(self.centralwidget, True, True, 0)
        self.add(self.box)

    def setCentralWidget(self, widget):
        for old_widget in self.centralwidget.get_children():
            self.centralwidget.remove(self, old_widget)
        self.centralwidget.pack_start(widget, True, True, 0)

    def activate(self):
        MainWidget.activate(self)
        state = self.config()["main_window_state"]
        # Dynamically fill study mode menu.
        study_modes = [x for x in self.component_manager.all("study_mode")]
        study_modes.sort(key=lambda x:x.menu_weight)
        self.study_mode_for_action = {}
        '''
        for study_mode in study_modes:
            action = QtGui.QAction(study_mode.name, self)
            action.setCheckable(True)
            if self.config()["study_mode"] == study_mode.id:
                action.setChecked(True)
            study_mode_group.addAction(action)
            self.menu_Study.addAction(action)
            self.study_mode_for_action[action] = study_mode
        study_mode_group.triggered.connect(self.change_study_mode)

        '''

        GLib.timeout_add_seconds(60, self.controller_heartbeat)

    def change_study_mode(self, action):
        action.setChecked(True)
        study_mode = self.study_mode_for_action[action]
        print("change_study_mode() called with mode " + study_mode)
        self.controller().set_study_mode(study_mode)

    def controller_heartbeat(self):
        self.controller().heartbeat()
        return True

    def show_question(self, text, option0, option1, option2):
        print("main_wdgt.py show_question() called with text " + text)
        '''
        dialog = QtWidgets.QMessageBox(self.top_window())
        dialog.setIcon(QtWidgets.QMessageBox.Icon.Question)
        dialog.setWindowTitle(_("Mnemosyne"))
        dialog.setText(text)
        button0 = dialog.addButton(option0, QtWidgets.QMessageBox.ButtonRole.ActionRole)
        button1 = dialog.addButton(option1, QtWidgets.QMessageBox.ButtonRole.ActionRole)
        if option2:
            button2 = dialog.addButton(option2, QtWidgets.QMessageBox.ButtonRole.ActionRole)
        dialog.exec()
        if dialog.clickedButton() == button0:
            result = 0
        elif dialog.clickedButton() == button1:
            result = 1
        elif dialog.clickedButton() == button2:
            result = 2
        return result
        '''

    def show_error(self, text):
        print("MainWdgt::show_error() called with text " + text)
        #QtWidgets.QMessageBox.critical(self.top_window(), _("Mnemosyne"), text)

    def handle_keyboard_interrupt(self, text):
        self._store_state()

    def get_filename_to_open(self, path, filter, caption=""):
        '''
        filename, _ = QtWidgets.QFileDialog.\
            getOpenFileName(self, caption, path, filter)
        return filename
        '''

    def get_filename_to_save(self, path, filter, caption=""):
        '''
        filename, _ = QtWidgets.QFileDialog.\
            getSaveFileName(self, caption, path, filter)
        return filename
        '''

    def set_status_bar_message(self, text):
        self.status_bar.showMessage(text)

    def set_progress_text(self, text):
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        self.progress_bar.setLabelText(text)
        self.progress_bar.setRange(0, 0)
        self.progress_bar_update_interval = 1
        self.progress_bar_current_value = 0
        self.progress_bar_last_shown_value = 0
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    def set_progress_range(self, maximum):
        self.progress_bar.setRange(0, maximum)

    def set_progress_update_interval(self, update_interval):
        update_interval = int(update_interval)
        if update_interval == 0:
            update_interval = 1
        self.progress_bar_update_interval = update_interval

    def increase_progress(self, value):
        self.set_progress_value(self.progress_bar_current_value + value)

    def set_progress_value(self, value):
        # There is a possibility that 'value' does not visit all intermediate
        # integer values in the range, so we need to check and store the last
        # shown and the current value here.
        self.progress_bar_current_value = value
        if value - self.progress_bar_last_shown_value >= \
               self.progress_bar_update_interval:
            self.progress_bar.setValue(value)
            self.progress_bar_last_shown_value = value
            # This automatically processes events too. Calling processEvents
            # explictly here might even cause some crashes.

    def close_progress(self):
        if self.progress_bar:
            self.progress_bar.close()
        self.progress_bar = None

    def enable_edit_current_card(self, is_enabled):
        #self.actionEditCurrentCard.setEnabled(is_enabled)
        print("enable_edit_current_card() not implemented")

    def enable_delete_current_card(self, is_enabled):
        #self.actionDeleteCurrentCard.setEnabled(is_enabled)
        print("enable_delete_current_card() not implemented")

    def enable_reset_current_card(self, is_enabled):
        #self.actionResetCurrentCard.setEnabled(is_enabled)
        print("enable_reset_current_card() not implemented")

    def enable_browse_cards(self, is_enabled):
        #self.actionBrowseCards.setEnabled(is_enabled)
        print("enable_browse_cards() not implemented")

    def file_new(self):
        self.controller().show_new_file_dialog()

    def file_open(self):
        self.controller().show_open_file_dialog()

    def file_save(self):
        self.controller().save_file()

    def file_save_as(self):
        self.controller().show_save_file_as_dialog()

    def compact_database(self):
        self.controller().show_compact_database_dialog()

    def import_file(self):
        self.controller().show_import_file_dialog()

    def export_file(self):
        self.controller().show_export_file_dialog()

    def sync(self):
        self.controller().show_sync_dialog()

    def add_cards(self):
        self.controller().show_add_cards_dialog()

    def edit_current_card(self):
        self.controller().show_edit_card_dialog()

    def delete_current_card(self):
        self.controller().delete_current_card()

    def reset_current_card(self):
        self.controller().reset_current_card()

    def browse_cards(self):
        self.controller().show_browse_cards_dialog()

    def activate_cards(self):
        self.controller().show_activate_cards_dialog()

    def find_duplicates(self):
        self.controller().find_duplicates()

    def manage_card_types(self):
        self.controller().show_manage_card_types_dialog()

    def configure(self):
        self.controller().show_configuration_dialog()

    def set_card_appearance(self):
        self.controller().show_card_appearance_dialog()

    def manage_plugins(self):
        self.controller().show_manage_plugins_dialog()

    def show_statistics(self):
        self.controller().show_statistics_dialog()

    def show_getting_started(self):
        self.controller().show_getting_started_dialog()

    def show_about(self):
        self.controller().show_about_dialog()
