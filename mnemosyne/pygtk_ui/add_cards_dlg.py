#
# add_cards_dlg.py <shiftee@posteo.net>
# Based on a file with the same name in the pyqt_ui directory
#

import copy

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
#from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import AddCardsDialog
from mnemosyne.pygtk_ui.card_type_wdgt_generic import GenericCardTypeWdgt


class AddEditCards(Component):

    """Code shared between the add and the edit dialogs."""

    def activate(self):
        AddCardsDialog.activate(self)
        status = self.run()
        self.destroy()
        print("activate() got response " + str(status))
        print (status == Gtk.ResponseType.OK)
        return (status == Gtk.ResponseType.OK)

    def initialise_card_types_combobox(self, current_card_type_name):
        # We calculate card_type_by_name here because these names can change
        # if the user chooses another translation.
        self.card_type_by_name = {}
        self.card_type = None
        self.card_type_index = 0
        self.card_type_widget = None
        self.previous_tags = None
        self.previous_card_type_name = current_card_type_name
        db_sorted_card_types = self.database().sorted_card_types()
        card_type_index = 0
        for card_type in db_sorted_card_types:
            if card_type.hidden_from_UI == True:
                continue
            # Adding M-sided cards or converting to them is not (yet) supported.
            if _(card_type.name) != current_card_type_name \
               and card_type.id.startswith("7"):
                continue
            if _(card_type.name) == current_card_type_name:
                self.card_type = card_type
                self.card_type_index = card_type_index
            self.card_type_by_name[_(card_type.name)] = card_type
            self.card_types_widget.append_text(_(card_type.name))
            card_type_index += 1
        if not self.card_type:
            self.card_type = db_sorted_card_types[0]
            self.card_type_index = 0
        self.card_types_widget.set_active(self.card_type_index)
        # Now that the combobox is filled, we can connect the signal.
        self.card_types_widget.connect("changed", self.card_type_changed)
        self.correspondence = {}  # Used when changing card types.
        self.update_card_widget()

    def update_card_widget(self, keep_data_from_previous_widget=True):
        # Determine data to put into card widget. Since we want to share this
        # code between the 'add' and the 'edit' dialogs, we put the reference
        # to self.card (which only exists in the 'edit' dialog) inside a try
        # statement.
        if self.card_type_widget:  # Get data from previous card widget.
            prefill_fact_data = self.card_type_widget.fact_data()
            self.card_type_widget.close()
            self.card_type_widget = None
        else:
            try:  # Get data from fact passed to the 'edit' dialog.
                prefill_fact_data = self.card.fact.data
            except:  # Start from scratch in the 'add' dialog.
                prefill_fact_data = None
        # Transform keys in dictionary if the card type has changed, but don't
        # edit the fact just yet.
        if prefill_fact_data and self.correspondence:
            old_prefill_fact_data = copy.copy(prefill_fact_data)
            prefill_fact_data = {}
            for fact_key in old_prefill_fact_data:
                if fact_key in self.correspondence:
                    value = old_prefill_fact_data[fact_key]
                    prefill_fact_data[self.correspondence[fact_key]] = value
        # If we just want to force a new card in the dialog, e.g. by pressing
        # PageUp or PageDown in the card browser, don't bother with trying to
        # keep old data.
        if not keep_data_from_previous_widget:
            prefill_fact_data = self.card.fact.data
        # Show new card type widget.
        card_type_name = self.card_types_widget.get_active_text()
        self.card_type = self.card_type_by_name[card_type_name]
        try:
            card_class_type = self.component_manager.current(
                "card_type_widget", used_for=self.card_type.__class__)
            card_class_inst = card_class_type(
                 card_type=self.card_type, parent=self,
                 component_manager=self.component_manager)
        except Exception as e:
            if not self.card_type_widget:
                card_class_type = self.component_manager.current(
                    "generic_card_type_widget")
                card_class_inst = card_class_type(
                    card_type=self.card_type, parent=self,
                    component_manager=self.component_manager)
        self.card_type_widget = card_class_inst
        self.card_type_widget.set_fact_data(prefill_fact_data)
        self.card_type_widget.show()
        self.vbox_card_widget.pack_start(self.card_type_widget, True, True, 0)

    def update_tags_combobox(self, current_tag_name):
        all_current_tag_names = current_tag_name.split(", ")
        existing_current_tag_names = []
        self.tags.remove_all()
        num_tags = 0
        for tag in self.database().tags():
            if tag.name != "__UNTAGGED__":
                self.tags.append_text(tag.name)
                num_tags += 1
            if tag.name in all_current_tag_names:
                existing_current_tag_names.append(tag.name)
        current_tag_name = ", ".join(existing_current_tag_names)
        # For the 'special' tags, we add them at the top.
        if "," in current_tag_name:
            self.tags.prepend_text(current_tag_name)
            num_tags += 1
        if current_tag_name == "":
            self.tags.prepend_text(current_tag_name)
            num_tags += 1
        for i in range(num_tags):
            self.tags.set_active(i)
            if self.tags.get_active_text() == current_tag_name:
                break
        self.previous_tags = self.tags.get_active_text()

    def card_type_changed(self, combo_box):
        new_card_type_name = combo_box.get_active_text()
        new_card_type = self.card_type_by_name[new_card_type_name]
        if self.card_type.fact_keys().issubset(new_card_type.fact_keys()) or \
            self.card_type_widget.is_empty():
            self.update_card_widget()
            return
        dlg = ConvertCardTypeKeysDlg(self.card_type, new_card_type,
            self.correspondence, check_required_fact_keys=False, parent=self)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            # Set correspondence so as not to erase previous data.
            self.correspondence = {}
            for key in self.card_type.fact_keys():
                self.correspondence[key] = key
            self.card_types_widget.set_active(self.card_type_index)
            return
        else:
            self.update_card_widget()

    def preview(self):
        fact_data = self.card_type_widget.fact_data()
        fact = Fact(fact_data)
        cards = self.card_type.create_sister_cards(fact)
        tag_text = self.tags.get_active_text()
        dlg = PreviewCardsDlg(cards, tag_text,
            component_manager=self.component_manager, parent=self)
        dlg.exec()

    def __del__(self):
        # Make sure that Python knows Qt has deleted this widget.
        self.card_type_widget = None


class AddCardsDlg(AddEditCards, AddCardsDialog, Gtk.Dialog):

    def __init__(self, card_type=None, fact_data=None, **kwds):
        super().__init__(**kwds)
        self.setupUI()
        if card_type:
            last_used_card_type = card_type
        else:
            last_used_card_type_id = self.config()["last_used_card_type_id"]
            try:
                last_used_card_type = self.card_type_with_id(\
                    last_used_card_type_id)
            except:
                # First time use, or card type was deleted.
                last_used_card_type = self.card_type_with_id("1")
        self.initialise_card_types_combobox(last_used_card_type.name)
        if last_used_card_type.id not in \
            self.config()["last_used_tags_for_card_type_id"]:
            self.config()["last_used_tags_for_card_type_id"]\
                [last_used_card_type.id] = ""
        if not self.config()["is_last_used_tags_per_card_type"]:
            self.update_tags_combobox(self.config()["last_used_tags"])
        else:
            self.update_tags_combobox(self.config()\
                ["last_used_tags_for_card_type_id"][last_used_card_type.id])
        if fact_data:
            self.card_type_widget.set_fact_data(fact_data)

    def setupUI(self):
        self.vbox_layout      = Gtk.VBox(spacing=6)
        self.vbox_card_widget = Gtk.VBox(spacing=6)

        self.grid_layout = Gtk.Grid()
        self.label_card_type = Gtk.Label()
        self.label_card_type.set_text( _("Card type") + ":" )
        self.grid_layout.attach(self.label_card_type, 0, 0, 1, 1)
        self.card_types_widget = Gtk.ComboBoxText()
        self.grid_layout.attach(self.card_types_widget, 1, 0, 1, 1)
        self.label_tags = Gtk.Label()
        self.label_tags.set_text( _("Tags") + ":" )
        self.grid_layout.attach(self.label_tags, 0, 1, 1, 1)

        self.tags = Gtk.ComboBoxText.new_with_entry()
        self.grid_layout.attach(self.tags, 1, 1, 1, 1)
        self.vbox_layout.pack_start(self.grid_layout, True, True, 0)

        self.vbox_layout.pack_start(self.vbox_card_widget, True, True, 0)

        self.grade_buttons = Gtk.HButtonBox()
        self.grade_0_button = Gtk.Button.new_with_label( _("Yet to learn") )
        self.grade_2_button = Gtk.Button.new_with_label("2")
        self.grade_3_button = Gtk.Button.new_with_label("3")
        self.grade_4_button = Gtk.Button.new_with_label("4")
        self.grade_5_button = Gtk.Button.new_with_label("5")
        self.grade_0_button.connect("clicked", self.create_new_cards, 0)
        self.grade_2_button.connect("clicked", self.create_new_cards, 2)
        self.grade_3_button.connect("clicked", self.create_new_cards, 3)
        self.grade_4_button.connect("clicked", self.create_new_cards, 4)
        self.grade_5_button.connect("clicked", self.create_new_cards, 5)
        self.grade_buttons.pack_start(self.grade_0_button, True, True, 0)
        self.grade_buttons.pack_start(self.grade_2_button, True, True, 0)
        self.grade_buttons.pack_start(self.grade_3_button, True, True, 0)
        self.grade_buttons.pack_start(self.grade_4_button, True, True, 0)
        self.grade_buttons.pack_start(self.grade_5_button, True, True, 0)
        self.vbox_layout.pack_start(self.grade_buttons, True, True, 0)

        self.bottom_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.preview_button = Gtk.Button.new_with_label( _("Preview") )
        self.exit_button = Gtk.Button.new_with_label( _("Exit") )
        self.bottom_buttons.pack_start(self.preview_button, True, True, 0)
        self.bottom_buttons.pack_start(self.exit_button, True, True, 0)
        self.vbox_layout.pack_start(self.bottom_buttons, True, True, 0)

        self.exit_button.connect("clicked", self.on_exit_clicked)
        self.preview_button.connect("clicked", AddCardsDlg.preview)

        box = self.get_content_area()
        box.pack_start(self.vbox_layout, True, True, 0)
        box.show_all()

    def card_type_changed(self, new_card_type_name):
        # We only store the last used tags when creating a new card,
        # not when editing.
        new_card_type = self.card_type_by_name[new_card_type_name]
        self.config()["last_used_card_type_id"] = new_card_type.id
        if new_card_type.id not in \
            self.config()["last_used_tags_for_card_type_id"]:
            self.config()["last_used_tags_for_card_type_id"]\
                [new_card_type.id] = ""
        if not self.config()["is_last_used_tags_per_card_type"]:
            if not self.tags.get_active_text():
                self.update_tags_combobox(self.config()["last_used_tags"])
        else:
            if not self.tags.get_active_text() \
                or self.card_type_widget.is_empty():
                self.update_tags_combobox(self.config()\
                    ["last_used_tags_for_card_type_id"][new_card_type.id])
        AddEditCards.card_type_changed(self, new_card_type_name)

    def set_valid(self, valid):
        self.grade_buttons.set_sensitive(valid)
        self.preview_button.set_sensitive(valid)

    def create_new_cards(self, grade):
        if grade == 0:
            grade = -1
        fact_data = self.card_type_widget.fact_data()
        tag_names = [c.strip() for c in \
                     self.tags.get_active_text().split(',')]
        card_type_name = self.card_types_widget.get_active_text()
        card_type = self.card_type_by_name[card_type_name]
        c = self.controller()
        c.create_new_cards(fact_data, card_type, grade, tag_names, save=True)
        tag_text = ", ".join(tag_names)
        self.update_tags_combobox(tag_text)
        self.config()["last_used_tags"] = tag_text
        self.config()["last_used_tags_for_card_type_id"][card_type.id] \
            = tag_text
        self.card_type_widget.clear()

    def reject(self):
        # Generated when pressing escape or clicking the exit button.
        if not self.card_type_widget.is_empty() and \
            self.card_type_widget.is_changed():
            status = self.main_widget().show_question(\
                _("Abandon current card?"), _("&Yes"), _("&No"), "")
            if status == 0:
                Gtk.Dialog.response(self, Gtk.ResponseType.CANCEL)
                return
        else:
            Gtk.Dialog.response(self, Gtk.ResponseType.CANCEL)

    def on_exit_clicked(self, button):
        AddCardsDlg.reject(self)
