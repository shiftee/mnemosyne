#
# gtk_gui_translator.py <Johannes.Baiter@gmail.com>
#

import os
import sys

import gettext

from mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator \
     import GetTextGuiTranslator


class GtkGuiTranslator(GetTextGuiTranslator):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        '''
            self.qt_dir = os.environ["QTDIR"]
        except:
                self.qt_dir = os.path.join("/usr", "share", "qt6")
        '''
        WHERE_AM_I = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        print("rundir: " + WHERE_AM_I)
        po_path = 'po'
        gettext.bindtextdomain('myapplication', po_path)
        gettext.textdomain('myapplication')
        _ = gettext.gettext

    def translate_ui(self, language):
        print("GtkGuiTranslator::translate_ui() called")
'''
        app = QCoreApplication.instance()
        # We always need to remove a translator, to make sure we generate a
        # LanguageChange event even if their is no Qt translation for that
        # language installed.
        app.removeTranslator(self.qt_translator)
        self.qt_translator.load(os.path.join(self.qt_dir, "translations",
            "qt_" + language + ".qm"))
        app.installTranslator(self.qt_translator)
        # The title can also contain the database name.
        self.controller().update_title()
'''

