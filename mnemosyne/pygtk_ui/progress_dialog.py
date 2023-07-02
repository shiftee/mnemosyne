#
# progress_dialog.py <shiftee@posteo.net>
# Provides a basic progress dialog with a simple API
#


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class ProgressDialog(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_border_width(10)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.progressbar = Gtk.ProgressBar()
        vbox.pack_start(self.progressbar, True, True, 0)

        self.range = 100
        self.progressbar.set_show_text(True)

    def set_label_text(self, text):
        if text is not None:
            self.progressbar.set_text(text)

    def set_range(self, maximum):
        self.range = maximum

    def set_value(self, new_value):
        new_value = float(new_value) / self.range
        self.progressbar.set_fraction(new_value)

