#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
'''Creates plugin for Calibre to allow users to create x-ray, author profile, start actions, and end actions for devices'''

from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__ = 'GPL v3'
__copyright__ = '2016, Samreen Zarroug, Anthony Toole, & Alex Mayer'
__docformat__ = 'restructuredtext en'

# The class that all Interface Action plugin wrappers must inherit from
from calibre.utils.config import JSONConfig
from calibre.customize import InterfaceActionBase

__prefs__ = JSONConfig('plugins/xray_creator')

class XRayCreatorPlugin(InterfaceActionBase):
    '''Initializes X-Ray Creator Plugin'''
    name = 'X-Ray Creator'
    description = 'A plugin to create X-Ray files for Kindle books'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Samreen Zarroug, Anthony Toole, & Alex Mayer'
    version = (3, 1, 4)
    minimum_calibre_version = (2, 0, 0)
    actual_plugin = 'calibre_plugins.xray_creator.ui:XRayCreatorInterfacePlugin'

    def __init__(self, *args, **kwargs):
        InterfaceActionBase.__init__(self, *args, **kwargs)
        self.set_default_prefs()

    @staticmethod
    def is_customizable():
        '''Tells Calibre that this widget is customizable'''
        return True

    @staticmethod
    def config_widget():
        '''Creates preferences dialog'''
        from calibre_plugins.xray_creator.config import ConfigWidget
        return ConfigWidget()

    @staticmethod
    def save_settings(config_widget):
        '''Saves preferences into book setting's json file'''
        config_widget.save_settings()

    def set_default_prefs(self):
        '''Set default plugin settings'''
        __prefs__.defaults['send_to_device'] = True
        __prefs__.defaults['create_files_when_sending'] = True
        __prefs__.defaults['expand_aliases'] = True
        __prefs__.defaults['overwrite_when_creating'] = False
        __prefs__.defaults['overwrite_when_sending'] = False
        __prefs__.defaults['create_send_xray'] = True
        __prefs__.defaults['create_send_author_profile'] = False
        __prefs__.defaults['create_send_start_actions'] = False
        __prefs__.defaults['create_send_end_actions'] = False
        __prefs__.defaults['file_preference'] = 'mobi'
        __prefs__.defaults['tld'] = None
        __prefs__['plugin_path'] = self.plugin_path

        if __prefs__.has_key('mobi') and __prefs__.has_key('azw3'):
            __prefs__['formats'] = [ftype for ftype in ['mobi', 'azw3'] if __prefs__[ftype]]
            for ftype in ['mobi', 'azw3']:
                if __prefs__.has_key(ftype):
                    del __prefs__[ftype]
        else:
            __prefs__.defaults['formats'] = ['mobi', 'azw3']

    def do_user_config(self, parent=None):
        '''
        This method shows a configuration dialog for this plugin. It returns
        True if the user clicks OK, False otherwise. The changes are
        automatically applied.
        '''
        from PyQt5.Qt import QDialog, QDialogButtonBox, QVBoxLayout
        from calibre.gui2 import gprefs

        prefname = 'plugin config dialog:' + self.type + ':' + self.name
        geom = gprefs.get(prefname, None)

        config_dialog = QDialog(parent)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout = QVBoxLayout(config_dialog)

        def size_dialog():
            '''Sets size of dialog'''
            if geom is None:
                config_dialog.resize(config_dialog.sizeHint())
            else:
                config_dialog.restoreGeometry(geom)

        button_box.accepted.connect(lambda: self.validate(config_dialog, config_widget))
        button_box.rejected.connect(config_dialog.reject)
        config_dialog.setWindowTitle('Customize ' + self.name)

        config_widget = self.config_widget()
        layout.addWidget(config_widget)
        layout.addWidget(button_box)
        size_dialog()
        config_dialog.exec_()

        geom = bytearray(config_dialog.saveGeometry())
        gprefs[prefname] = geom

        return config_dialog.result()

    def validate(self, config_dialog, config_widget):
        '''Validates config widget info'''
        if config_widget.validate():
            config_dialog.accept()
            self.save_settings(config_widget)
