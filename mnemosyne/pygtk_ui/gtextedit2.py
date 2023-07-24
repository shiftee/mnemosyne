#
# gtextedit2.py <shiftee@posteo.net>
# Based on the file qtextedit2.py in the pyqt_ui directory
#

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib

from mnemosyne.libmnemosyne.gui_translator import _


class GTextEdit2(Gtk.TextView):

    """Gtk.TextView with extra options in popup menu."""

    def __init__(self, parent, card_type, pronunciation_hiding):

        """'pronunciation_hiding' is set to None when there is no
        pronunciation key to hide, and to True or False when there is one to
        hide.

        """

        super().__init__()
        self.pronunciation_hiding = pronunciation_hiding
        self.card_type = card_type
        # Make list of translators and pronouncers for this card type.
        language_id = self.card_type.config().card_type_property(\
            "language_id", self.card_type, default=None)
        self.translators = [] if not language_id else \
            self.card_type.component_manager.all("translator", language_id)
        self.pronouncers = [] if not language_id else \
            self.card_type.component_manager.all("pronouncer", language_id)

    def contextMenuEvent(self, e):
        popup = self.createStandardContextMenu()
        popup.addSeparator()

        self.insert_image_action = QtGui.QAction(_("Insert &image"), self)
        self.insert_image_action.triggered.connect(self.insert_img)
        self.insert_image_action.setShortcut(QtGui.QKeySequence(_("Ctrl+I")))
        popup.addAction(self.insert_image_action)

        self.insert_sound_action = QtGui.QAction(_("Insert &sound"), self)
        self.insert_sound_action.triggered.connect(self.insert_sound)
        self.insert_sound_action.setShortcut(QtGui.QKeySequence(_("Ctrl+S")))
        popup.addAction(self.insert_sound_action)

        self.insert_video_action = QtGui.QAction(_("Insert &video"), self)
        self.insert_video_action.triggered.connect(self.insert_video)
        self.insert_video_action.setShortcut(QtGui.QKeySequence(_("Ctrl+V")))
        popup.addAction(self.insert_video_action)

        # Pronunciation hiding.
        if self.pronunciation_hiding in [True, False]:
            popup.addSeparator()
            self.hide_action = QtGui.QAction(\
                _("&Hide pronunciation field for this card type"), popup)
            self.hide_action.setCheckable(True)
            self.hide_action.setChecked(self.pronunciation_hiding)
            self.hide_action.toggled.connect(\
                self.parent().pronunciation_hiding_toggled)
            popup.addAction(self.hide_action)
        # Translators.
        if len(self.translators):
            popup.addSeparator()
            for translator in self.translators:
                translator_action = QtGui.QAction(\
                    translator.popup_menu_text, popup)
                translator_action.triggered.connect(\
                    lambda checked, t=translator: self.translate(t))
                translator_action.setShortcuts([QtGui.QKeySequence("Ctrl+T")])
                popup.addAction(translator_action)
        # Pronouncers.
        if len(self.pronouncers):
            popup.addSeparator()
            for pronouncer in self.pronouncers:
                pronouncer_action = QtGui.QAction(\
                    pronouncer.popup_menu_text, popup)
                pronouncer_action.triggered.connect(\
                    lambda checked, p=pronouncer: self.pronounce(p))
                pronouncer_action.setShortcuts([QtGui.QKeySequence("Ctrl+P")])
                popup.addAction(pronouncer_action)
        # Show popup.
        popup.exec(e.globalPos())

    def translate(self, translator):
        foreign_text = self.parent().foreign_text()
        translated_text = translator.show_dialog(self.card_type, foreign_text)
        if translated_text:
            self.insertPlainText(translated_text)

    def pronounce(self, pronouncer):
        foreign_text = self.parent().foreign_text()
        pronounced_text = pronouncer.show_dialog(self.card_type, foreign_text)
        if pronounced_text:
            self.insertPlainText(pronounced_text)

    def insert_img(self):
        filter = "(*.png *.gif *.jpg *.bmp *.jpeg *.svg *.tiff *.webp" + \
                 " *.PNG *.GIF *.JPG *.BMP *.JPEG *.SVG *.TIFF *.WEBP)"
        filename = self.parent().controller().show_insert_img_dialog(filter)
        if filename:
            self.insertPlainText("<img src=\"" + filename + "\">")

    def insert_sound(self):
        filter = "(*.wav *.mp3 *.ogg *.WAV *.MP3 *.OGG)"
        filename = self.parent().controller().show_insert_sound_dialog(filter)
        if filename:
            self.insertPlainText("<audio src=\"" + filename + "\">")

    def insert_video(self):
        filter = "(*.mov *.ogg *.ogv *.mp4 *.qt" + \
                 " *.MOV *.OGG *.OGV *.MP4 *.QT)"
        filename = self.parent().controller().show_insert_video_dialog(filter)
        if filename:
            self.insertPlainText("<video src=\"" + filename + "\">")

    def get_text(self):
        start = self.get_buffer().get_start_iter()
        end   = self.get_buffer().get_end_iter()
        include_hidden = False
        return self.get_buffer().get_text(start, end, include_hidden)

    def set_text(self, text):
        self.get_buffer().set_text(text, len(text))
