#
# export_metadata_dlg.py <shiftee@posteo.net>
# Based on a file with the same name in the pyqt_ui directory
#

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.dialogs import ExportMetadataDialog


class ExportMetadataDlg(ExportMetadataDialog, Gtk.Dialog):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        '''
        self.author_name.setText(self.config()["author_name"])
        self.author_email.setText(self.config()["author_email"])
        self.date.setDate(QtCore.QDate.currentDate())
        self.allow_cancel = True
        self.cancelled = False
        '''

    def activate(self):
        ExportMetadataDialog.activate(self)
        #return self.exec()

    def set_values(self, metadata):
        '''
        if "card_set_name" in metadata:
            self.card_set_name.setText(metadata["card_set_name"])
        if "author_name" in metadata:
            self.author_name.setText(metadata["author_name"])
        if "author_email" in metadata:
            self.author_email.setText(metadata["author_email"])
        if "tags" in metadata:
            self.tags.setText(metadata["tags"])
        if "date" in metadata:
            date = QtCore.QDate()
            date.fromString(metadata["date"])
            self.date.setDate(date)
        if "revision" in metadata:
            self.revision.setValue(int(metadata["revision"]))
        if "notes" in metadata:
            self.notes.setPlainText(metadata["notes"])
        '''

    def set_read_only(self):
        '''
        self.card_set_name.setReadOnly(True)
        self.author_name.setReadOnly(True)
        self.author_email.setReadOnly(True)
        self.tags.setReadOnly(True)
        self.date.setReadOnly(True)
        self.revision.setReadOnly(True)
        self.notes.setReadOnly(True)
        self.allow_cancel = False
        self.setWindowTitle(_("Import cards"))
        '''

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        if self.allow_cancel:
            event.ignore()
            self.reject()
        else:
            event.accept()

    def keyPressEvent(self, event):
        pass

    def reject(self):
        self.cancelled = True
        return QtWidgets.QDialog.reject(self)

    def values(self):
        '''
        if self.cancelled:
            return None
        '''
        metadata = {}
        '''
        metadata["card_set_name"] = self.card_set_name.text()
        metadata["author_name"] = self.author_name.text()
        metadata["author_email"] = self.author_email.text()
        metadata["tags"] = self.tags.text()
        metadata["date"] = self.date.date().toString()
        metadata["revision"] = str(self.revision.value())
        metadata["notes"] = self.notes.toPlainText()
        self.config()["author_name"] = metadata["author_name"]
        self.config()["author_email"] = metadata["author_email"]
        '''
        return metadata
