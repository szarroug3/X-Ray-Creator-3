#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2016, Samreen Zarroug, Anthony Toole, & Alex Mayer'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QMenu, QToolButton, QDialog

from calibre.gui2 import error_dialog
from calibre.gui2 import Dispatcher
from calibre.gui2.actions import InterfaceAction
from calibre.gui2.threaded_jobs import ThreadedJob

from calibre_plugins.xray_creator.config import prefs
from calibre_plugins.xray_creator.lib.xray_creator import *
from calibre_plugins.xray_creator.book_config import BookConfigWidget

class XRayCreatorInterfacePlugin(InterfaceAction):

    name = 'X-Ray Creator'

    # Set main action and keyboard shortcut
    action_spec = ('X-Ray Creator', None,
            'Run X-Ray Creator', 'Ctrl+Shift+Alt+X')
    popup_type = QToolButton.InstantPopup
    action_type = 'current'

    def genesis(self):
        # initial setup here
        self._send_to_device = prefs['send_to_device']
        self._create_xray_when_sending = prefs['create_xray_when_sending']
        self._mobi = prefs['mobi']
        self._azw3 = prefs['azw3']

        icon = get_icons('images/icon.png')

        self.menu = QMenu(self.gui)
        self.create_menu_action(self.menu, 'Book Specific Preferences',
                'Book Specific Preferences', None, 'CTRL+SHIFT+ALT+Z',
                'Set preferences specific to the book', self.book_config)
        self.create_menu_action(self.menu, 'X-Ray Creator Create/Update Button',
                'Create/Update X-Rays', None, 'CTRL+SHIFT+ALT+X',
                'Create/Update x-rays for chosen books', self.create_xrays)
        self.create_menu_action(self.menu, 'Send Local X-Rays to Device',
                'Sends X-Ray Files to Device', None, 'CTRL+SHIFT+ALT+C',
                'Sends x-Ray files to device', self.send_xrays)

        self.menu.addSeparator()

        self.create_menu_action(self.menu, 'X-Ray Creator Preferences Button',
                'Preferences', None, None,
                'Create X-Rays for Chosen Books', self.config)
        self.qaction.setIcon(icon)
        self.qaction.setMenu(self.menu)

    def apply_settings(self):
        from calibre_plugins.xray_creator.config import prefs

        self._send_to_device = prefs['send_to_device']
        self._create_xray_when_sending = prefs['create_xray_when_sending']
        self._mobi = prefs['mobi']
        self._azw3 = prefs['azw3']

    def create_xrays(self):
        xray_creator = self._get_books('Cannot create X-Rays')
        if xray_creator:
            job = ThreadedJob('create_xray', 'Creating X-Ray Files', xray_creator.create_xrays_event, (), {}, Dispatcher(self.created_xrays))
            self.gui.job_manager.run_threaded_job(job)

    def send_xrays(self):
        xray_creator = self._get_books('Cannot send X-Rays')
        if xray_creator:
            job = ThreadedJob('create_xray', 'Sending X-Ray Files to Device', xray_creator.send_xrays_event, (), {}, Dispatcher(self.sent_xrays))
            self.gui.job_manager.run_threaded_job(job)

    def book_config(self):
        db = self.gui.current_db
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            error_dialog(self.gui, 'Cannot set book preferences',
                         'No books selected', show=True)
            return

        ids = list(map(self.gui.library_view.model().id, rows))
        db = db.new_api

        book_configs = BookConfigWidget(db, ids, self.gui)

    def created_xrays(self, job):
        pass

    def sent_xrays(self, job):
        pass

    def _get_books(self, error_msg):
        from calibre.ebooks.metadata.meta import get_metadata, set_metadata

        db = self.gui.current_db
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            error_dialog(self.gui, error_msg,
                         'No books selected', show=True)
            return None

        if not self._mobi and not self._azw3:
            error_dialog(self.gui, error_msg,
                         'No formats chosen in preferences.', show=True)
            return None

        ids = list(map(self.gui.library_view.model().id, rows))
        db = db.new_api

        formats = []
        if self._mobi:
            formats.append('MOBI')
        if self._azw3:
            formats.append('AZW3')

        xray_creator = XRayCreator(db, ids, formats=formats, send_to_device=self._send_to_device, create_xray=self._create_xray_when_sending)
        return xray_creator

    def config(self):
        self.interface_action_base_plugin.do_user_config(self.gui)