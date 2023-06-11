#
# review_wdgt.py <shiftee@posteo.net>
# Based on a file with the same name in the pyqt_ui directory
#

import os

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('WebKit2', '4.1')

from gi.repository import Gtk
from gi.repository import WebKit2

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(ReviewWidget, Gtk.Box):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        parent = self.main_widget()

        parent.setCentralWidget(self)

        self.verticalLayout_5 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.vertical_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=9)

        self.question_label = Gtk.Label()
        self.question       = WebKit2.WebView()
        self.question_box   = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.question_box.pack_start(self.question_label, False, False, 0)
        self.question_box.pack_start(self.question, True, True, 0)
        self.vertical_layout.pack_start(self.question_box, True, True, 0)

        self.answer_label = Gtk.Label(label=_('Answer:'))
        self.answer       = WebKit2.WebView()
        self.answer_box   = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.answer_box.pack_start(self.answer_label, False, False, 0)
        self.answer_box.pack_start(self.answer, True, True, 0)
        self.vertical_layout.pack_start(self.answer_box, True, True, 0)

        self.show_button = Gtk.Button.new_with_label("show_button")
        self.show_button.connect("clicked", self.show_answer_button_clicked)
        self.vertical_layout.pack_start(self.show_button, False, False, 0)

        self.grades = Gtk.HButtonBox()
        self.grade_0_button = Gtk.Button.new_with_label("0")
        self.grade_1_button = Gtk.Button.new_with_label("1")
        self.grade_2_button = Gtk.Button.new_with_label("2")
        self.grade_3_button = Gtk.Button.new_with_label("3")
        self.grade_4_button = Gtk.Button.new_with_label("4")
        self.grade_5_button = Gtk.Button.new_with_label("5")
        self.grades.pack_start(self.grade_0_button, True, True, 0)
        self.grades.pack_start(self.grade_1_button, True, True, 0)
        self.grades.pack_start(self.grade_2_button, True, True, 0)
        self.grades.pack_start(self.grade_3_button, True, True, 0)
        self.grades.pack_start(self.grade_4_button, True, True, 0)
        self.grades.pack_start(self.grade_5_button, True, True, 0)
        self.grade_0_button.connect("clicked", self.grade_button_pressed, 0)
        self.grade_1_button.connect("clicked", self.grade_button_pressed, 1)
        self.grade_2_button.connect("clicked", self.grade_button_pressed, 2)
        self.grade_3_button.connect("clicked", self.grade_button_pressed, 3)
        self.grade_4_button.connect("clicked", self.grade_button_pressed, 4)
        self.grade_5_button.connect("clicked", self.grade_button_pressed, 5)

        self.vertical_layout.pack_start(self.grades, False, False, 0)
        self.verticalLayout_5.pack_start(self.vertical_layout, True, True, 0)

        self.add(self.verticalLayout_5)

        self.media_queue = []
        self.player = None

    def show_answer_button_clicked(self, widget):
        ReviewWdgt.show_answer(self)

    def deactivate(self):
        self.stop_media()
        ReviewWidget.deactivate(self)

    def show_answer(self):
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def grade_button_pressed(self, widget, grade):
        self.grade_answer(grade)

    def set_question(self, text):
        self.question_text = text

    def set_answer(self, text):
        self.answer_text = text

    def reveal_question(self):
        self.question.load_html(self.question_text, 'file://')

    def reveal_answer(self):
        self.is_answer_showing = True
        self.answer.load_html(self.answer_text, 'file://')

    def clear_answer(self):
        self.is_answer_showing = False
        self.answer.load_uri("about:blank")

    def set_question_box_visible(self, is_visible):
        if is_visible:
            self.question.show()
            self.question_label.show()
        else:
            self.question.hide()
            self.question_label.hide()

    def set_answer_box_visible(self, is_visible):
        if is_visible:
            self.answer.show()
            self.answer_label.show()
        else:
            self.answer.hide()
            self.answer_label.hide()

    def set_question_label(self, text):
        self.question_label.set_text(text)

    def update_show_button(self, text, is_default, is_enabled):
        self.show_button.set_label(text)
        self.show_button.set_sensitive(is_enabled)

    def set_grades_enabled(self, is_enabled):
        self.grades.set_sensitive(is_enabled)

    def set_grade_text(self, grade, text):
        if grade == 0:
            self.grade_0_button.set_label(text)
        if grade == 1:
            self.grade_1_button.set_label(text)
        if grade == 2:
            self.grade_2_button.set_label(text)
        if grade == 3:
            self.grade_3_button.set_label(text)
        if grade == 4:
            self.grade_4_button.set_label(text)
        if grade == 5:
            self.grade_5_button.set_label(text)

    def redraw_now(self):
        pass

    def play_media(self, filename, start=None, stop=None):
        if self.player == None:
            #print("Initialising mediaplayer")
            #print("Available devices:")
            from PyQt6.QtMultimedia import QMediaDevices
            for device in QMediaDevices().audioOutputs():
                print("  ", device.description())
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            #print("Selected audio output:", self.audio_output.device().description())
            #print("Volume:", self.audio_output.volume())
            #print("Muted:", self.audio_output.isMuted())
            self.player.setAudioOutput(self.audio_output)
            self.player.mediaStatusChanged.connect(self.player_status_changed)
        if start is None:
            start = 0
        if stop is None:
            stop = 999999
        self.media_queue.append((filename, start, stop))
        if not self.player.playbackState() == \
            QMediaPlayer.PlaybackState.PlayingState:
            self.play_next_file()

    def play_next_file(self):
        filename, self.current_media_start, self.current_media_stop = \
            self.media_queue.pop(0)
        #print("Starting to play", filename)
        self.player.setSource(QtCore.QUrl.fromLocalFile(filename))
        self.player.positionChanged.connect(self.stop_playing_if_end_reached)
        self.player.play()

    def stop_playing_if_end_reached(self, current_position):
        if current_position >= 1000*self.current_media_stop:
            self.player.stop()
            self.play_next_file()

    def player_status_changed(self, result):
        if result == QMediaPlayer.MediaStatus.BufferedMedia:
            self.player.setPosition(int(self.current_media_start*1000))
        elif result == QMediaPlayer.MediaStatus.EndOfMedia:
            #print("End of media reached.")
            if len(self.media_queue) >= 1:
                self.player.positionChanged.disconnect()
                self.play_next_file()
            else:
                self.player.setSource(QtCore.QUrl(None))

    def stop_media(self):
        if self.player:
            self.player.stop()
            self.player.setSource(QtCore.QUrl(None))
        self.media_queue = []
