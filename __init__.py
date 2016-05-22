#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2016, Samreen Zarroug & Alex Mayer'
__docformat__ = 'restructuredtext en'

# The class that all Interface Action plugin wrappers must inherit from
from calibre.customize import InterfaceActionBase

class XRayCreatorPlugin(InterfaceActionBase):
    name                = 'X-Ray Creator'
    description         = 'A plugin to create X-Ray files for MOBI books'
    supported_platforms = ['windows']
    author              = 'Samreen Zarroug & Alex Mayer'
    version             = (2, 0, 0)
    minimum_calibre_version = (0, 9, 29)
    actual_plugin       = 'calibre_plugins.xray_creator.ui:XRayCreatorInterfacePlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.xray_creator.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()

        # Apply the changes
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()