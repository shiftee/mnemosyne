#
# card_type_wdgt_generic.py <shiftee@posteo.net>
# Based on a file with the same name in the pyqt_ui directory
#

import re

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pygtk_ui.gtextedit2 import GTextEdit2
from mnemosyne.libmnemosyne.ui_components.card_type_widget \
     import GenericCardTypeWidget


class GenericCardTypeWdgt(GenericCardTypeWidget, Gtk.Box):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.vboxlayout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.fact_key_for_edit_box = {}
        self.top_edit_box = None
        self.edit_boxes = []
        self.fact_data_before_edit = {}
        # Does this card type need to deal with the hiding of pronunciation
        # keys?
        if "p_1" not in self.card_type.fact_keys():
            pronunciation_hiding = None
        else:
            pronunciation_hiding = self.config().card_type_property(\
                "hide_pronunciation_field", self.card_type, default=False)
        # Construct the rest of the dialog.
        parent = kwds["parent"] # Also used by other parent classes inits.
        for fact_key, fact_key_name in self.card_type.fact_keys_and_names:
            l = Gtk.Label()
            l.set_text(_(fact_key_name) + ":")
            self.vboxlayout.pack_start(l, False, False, 0)
            if fact_key == "p_1":
                self.pronunciation_label = l
                self.pronunciation_label.setVisible(not pronunciation_hiding)
            t = GTextEdit2(self, self.card_type, pronunciation_hiding)
            t.show()
            self.edit_boxes.append(t)
            self.vboxlayout.pack_start(t, True, True, 0)
            self.fact_key_for_edit_box[t] = fact_key
            if self.top_edit_box is None:
                self.top_edit_box = t
            previous_box = t
            # Bug: update_formatting needs to happen before setting
            # visible.
            self.update_formatting(t)
            if fact_key == "p_1":
                self.pronunciation_box = t
                self.pronunciation_box.setVisible(not pronunciation_hiding)
            t.get_buffer().connect("changed", self.text_changed)
            #t.currentCharFormatChanged.connect(self.reset_formatting)

        self.add(self.vboxlayout)
        self.show_all()

    def pronunciation_hiding_toggled(self, checked):
        self.config().set_card_type_property("hide_pronunciation_field",
            checked, self.card_type)
        self.pronunciation_label.setVisible(not checked)
        self.pronunciation_box.setVisible(not checked)
        for edit_box in self.edit_boxes:
            edit_box.pronunciation_hiding = checked

    def update_formatting(self, edit_box):
        # Font colour.
        fact_key = self.fact_key_for_edit_box[edit_box]
        colour = self.config().card_type_property(\
            "font_colour", self.card_type, fact_key)
        if colour:
            edit_box.setTextColor(QtGui.QColor(colour))
        # Background colour.
        colour = self.config().card_type_property(\
            "background_colour", self.card_type)
        if colour:
            p = QtGui.QPalette()
            p.setColor(QtGui.QPalette.ColorGroup.Active, 
                        QtGui.QPalette.ColorRole.Base,
                        QtGui.QColor(colour))
            edit_box.setPalette(p)
        # Font.
        font_string = self.config().card_type_property(\
            "font", self.card_type, fact_key)
        if font_string:
            font = QtGui.QFont()
            font.fromString(font_string)
            edit_box.setCurrentFont(font)

    def reset_formatting(self):

        """Deleting all the text reverts back to the system font, so we have
        to force our custom font again.

        """

        for edit_box in self.fact_key_for_edit_box:
            self.update_formatting(edit_box)

    def is_empty(self):
        for edit_box in self.fact_key_for_edit_box:
            if edit_box.get_text():
                return False
        return True

    def is_changed(self):
        return self.fact_data() != self.fact_data_before_edit

    def fact_data(self):
        _fact_data = {}
        for edit_box, fact_key in self.fact_key_for_edit_box.items():
            _fact_data[fact_key] = edit_box.get_text()
        return _fact_data

    def foreign_text(self):
        foreign_fact_key = self.config().card_type_property(\
            "foreign_fact_key", self.card_type, default=None)
        if not foreign_fact_key:
            return
        foreign_text = self.fact_data()[foreign_fact_key]
        # Strip Cloze brackets and hints.
        if getattr(self.card_type, "q_a_from_cloze", None):
            foreign_text = self.card_type.q_a_from_cloze(foreign_text, -1)[0]
        # Strip html tags.
        tag_re = re.compile(r"<[^>]+>")
        return tag_re.sub("", foreign_text).strip()

    def set_fact_data(self, fact_data):
        self.fact_data_before_edit = fact_data
        if fact_data:
            for edit_box, fact_key in self.fact_key_for_edit_box.items():
                if fact_key in fact_data:
                    edit_box.setPlainText(fact_data[fact_key])

    def clear(self):
        self.fact_data_before_edit = {}
        for edit_box in self.fact_key_for_edit_box:
            edit_box.set_text("")

    def text_changed(self, buffer):
        self.get_toplevel().set_valid(\
            self.card_type.is_fact_data_valid(self.fact_data()))
