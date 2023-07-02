#
# import_dlg.py <shiftee@posteo.net>
# Based on a file with the same name in the pyqt_ui directory
#

import os

import threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog


answer = None
#mutex = QtCore.QMutex()
#dialog_closed = QtCore.QWaitCondition()


class ImportThread(GObject.GObject):
    __gsignals__ = {
        'show_export_metadata': (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    def show_export_metadata_dialog(self, metadata, read_only=True):
        print("ImportThread::show_export_metadata_dialog() called")
    '''
        global answer
        mutex.lock()
        answer = None
        #self.show_export_metadata_signal.emit(metadata, read_only)
        #self.emit("show_export_metadata")
        if not answer:
            dialog_closed.wait(mutex)
        mutex.unlock()
    '''

    def __init__(self, filename, format, extra_tag_names, **kwds):
        GObject.GObject.__init__(self)
        self.filename = filename
        self.format = format
        self.extra_tag_names = extra_tag_names

    def do_work(self):
        print("ImportThread::do_work() called")
        #self.mnemosyne.config()["import_format"] = str(type(self.format))
        self.format.do_import(self.filename, self.extra_tag_names)


class ImportDlg(ImportDialog, Gtk.Dialog):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.file_formats = Gtk.ComboBoxText()
        self.file_formats.connect("changed", self.file_format_changed)

        self.tags = Gtk.ComboBoxText.new_with_entry()

        file_label_text = _('File') + ":"
        section_file_label = Gtk.Label(label=file_label_text)
        self.filename_box = Gtk.Label()
        self.browse_button = Gtk.Button(label=_("Browse"))
        file_choose_box = Gtk.HBox(spacing=6)
        file_choose_box.pack_start(self.filename_box, True, True, 0)
        file_choose_box.pack_start(self.browse_button, False, False, 0)
        self.browse_button.connect("clicked", self.choose_file_button_clicked)

        # File formats.
        i = 0
        current_index = None
        for format in self.component_manager.all("file_format"):
            if not format.import_possible:
                continue
            self.file_formats.append_text(_(format.description))
            if self.config()["import_format"] is not None:
                if str(type(format)) == self.config()["import_format"]:
                    current_index = i
            i += 1
        if current_index is not None:
            self.file_formats.set_active(current_index)
        # Extra tag.
        i = 0
        current_index = None
        for tag in self.database().tags():
            if tag.name == self.config()["import_extra_tag_names"]:
                current_index = i
            if tag.name != "__UNTAGGED__":
                self.tags.append_text(tag.name)
                i += 1
        if current_index is not None:
            self.tags.set_active(current_index)
        if self.config()["import_extra_tag_names"] == "":
            self.tags.prepend_text("")
            self.tags.set_active(0)
        if "," in self.config()["import_extra_tag_names"]:
            self.tags.prepend_text(self.config()["import_extra_tag_names"])
            self.tags.set_active(0)

        section_tags_label = Gtk.Label(label=_('Add additional tag(s) to cards:'))

        box = self.get_content_area()
        box.pack_start(self.file_formats, False, False, 0)
        box.pack_start(section_file_label, False, False, 0)
        box.pack_start(file_choose_box, False, False, 0)
        box.pack_start(section_tags_label, False, False, 0)
        box.pack_start(self.tags, False, False, 0)
        box.show_all()

        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(450, 800)

    def file_format_changed(self, widget):
        self.filename_box.set_text("")

    def activate(self):
        ImportDialog.activate(self)
        response = self.run()
        if response == Gtk.ResponseType.OK:
            self.accept()
        self.destroy()

    def format(self):
        for _format in self.component_manager.all("file_format"):
            if _(_format.description) == self.file_formats.get_active_text():
                return _format

    def browse(self):
        import_dir = self.config()["import_dir"]
        filename = self.main_widget().get_filename_to_open(import_dir,
            _(self.format().filename_filter))
        self.filename_box.set_text(filename)
        if filename:
            self.config()["import_dir"] = os.path.dirname(filename)

    def accept(self):
        filename = self.filename_box.get_text()
        if filename and os.path.exists(filename):
            extra_tag_names = self.tags.get_active_text()
            self.config()["import_extra_tag_names"] = extra_tag_names
            if not extra_tag_names:
                extra_tag_names = ""
            self.worker_thread = ImportThread(filename,
                self.format(), extra_tag_names, mnemosyne=self)
            self.worker_thread.connect("show_export_metadata",\
                self.threaded_show_export_metadata)
            self.run_worker_thread()
        else:
            self.main_widget().show_error(_("File does not exist."))

    def threaded_show_export_metadata(self, metadata, read_only):
        print("called threaded_show_export_metadata()")
        '''
        global answer
        mutex.lock()
        self.true_main_widget.show_export_metadata_dialog(metadata, read_only)
        answer = True
        dialog_closed.wakeAll()
        mutex.unlock()
        '''

    def work_ended(self):
        self.main_widget().close_progress()

    def choose_file_button_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("File selected: " + dialog.get_filename())
            self.filename_box.set_text( dialog.get_filename() )
        dialog.destroy()

    def add_filters(self, dialog):
        '''
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)
        '''

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    #temporary hack to avoid creating a thread
    def run_worker_thread(self):
        self.worker_thread.do_work()
        self.work_ended()

