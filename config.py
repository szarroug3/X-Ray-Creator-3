#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2016, Samreen Zarroug & Alex Mayer'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QGroupBox

from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/xray_creator')

# Set defaults
prefs.defaults['send_to_device'] = True
prefs.defaults['create_xray_when_sending'] = True
prefs.defaults['mobi'] = True
prefs.defaults['azw3'] = True

class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.send_to_device = QCheckBox('Send x-ray to device if connected')
        self.send_to_device.setChecked(prefs['send_to_device'])
        self.l.addWidget(self.send_to_device)

        self.create_xray_when_sending = QCheckBox('Create x-ray for files that don\'t already have them when sending to device')
        self.create_xray_when_sending.setChecked(prefs['create_xray_when_sending'])
        self.l.addWidget(self.create_xray_when_sending)

        self.book_types_to_create = QGroupBox()
        self.book_types_to_create.setTitle('Book types to create x-ray files for')
        self.book_types_to_create.setLayout(QHBoxLayout (self.book_types_to_create))

        self.mobi = QCheckBox('MOBI')
        self.mobi.setChecked(prefs['mobi'])
        self.book_types_to_create.layout().addWidget(self.mobi)

        self.azw3 = QCheckBox('AZW3')
        self.azw3.setChecked(prefs['azw3'])
        self.book_types_to_create.layout().addWidget(self.azw3)

        self.l.addWidget(self.book_types_to_create)

    def save_settings(self):
        prefs['send_to_device'] = self.send_to_device.isChecked()
        prefs['create_xray_when_sending'] = self.create_xray_when_sending.isChecked()
        prefs['mobi'] = self.mobi.isChecked()
        prefs['azw3'] = self.azw3.isChecked()