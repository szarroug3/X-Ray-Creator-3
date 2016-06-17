#!/usr/bin/env python2
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2016, Samreen Zarroug & Alex Mayer'
__docformat__ = 'restructuredtext en'

import os
import functools
from PyQt5.QtCore import *
from httplib import HTTPSConnection

from PyQt5.Qt import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.Qt import QLabel, QLineEdit, QPushButton, QScrollArea

from calibre_plugins.xray_creator.lib.book_settings import BookSettings

from calibre import get_proxies

class BookConfigWidget(QDialog):
    def __init__(self, db, ids, parent):
        QDialog.__init__(self, parent)
        self.resize(500,500)
        self._index = 0

        self._book_settings = []

        http_proxy = get_proxies(debug=False).get('http', None)
        if http_proxy:
            self._proxy = True
            self._http_address = ':'.join(http_proxy.split(':')[:-1])
            self._http_port = int(http_proxy.split(':')[-1])
            self._connection = HTTPSConnection(self._http_address, self._http_port)
            self._connection.set_tunnel('www.goodreads.com', 443)
        else:
            self._connection = HTTPSConnection('www.goodreads.com')

        for book_id in ids:
            self._book_settings.append(BookSettings(db, book_id, self._connection))

        self.v_layout = QVBoxLayout(self)

        self.setWindowTitle('title - author')

        # add Goodreads url text box
        self.goodreads_layout = QHBoxLayout(None)
        self.goodreads_url = QLabel('Goodreads URL:')
        self.goodreads_url.setFixedWidth(100)
        self.goodreads_url_edit = QLineEdit('')
        self.goodreads_url_edit.textEdited.connect(self.edit_goodreads_url)
        self.goodreads_layout.addWidget(self.goodreads_url)
        self.goodreads_layout.addWidget(self.goodreads_url_edit)
        self.v_layout.addLayout(self.goodreads_layout)

        self.update_buttons_layout = QHBoxLayout(None)
        self.update_goodreads_url_button = QPushButton('Search for Goodreads URL')
        self.update_goodreads_url_button.setFixedWidth(175)
        self.update_goodreads_url_button.clicked.connect(self.search_for_goodreads_url)
        self.update_buttons_layout.addWidget(self.update_goodreads_url_button)

        self.update_aliases_button = QPushButton('Update Aliases from URL')
        self.update_aliases_button.setFixedWidth(175)
        self.update_aliases_button.clicked.connect(self.update_aliases)
        self.update_buttons_layout.addWidget(self.update_aliases_button)
        self.v_layout.addLayout(self.update_buttons_layout)

        # add scrollable area for aliases
        self.aliases_label = QLabel('Aliases:')
        self.v_layout.addWidget(self.aliases_label)
        self.scroll_area = QScrollArea()
        self.v_layout.addWidget(self.scroll_area)

        # add status box
        self.status = QLabel('')
        self.v_layout.addWidget(self.status)

        # add previous, ok, cancel, and next buttons
        self.buttons_layout = QHBoxLayout(None)
        self.buttons_layout.setAlignment(Qt.AlignRight)

        if len(ids) > 1:
            self.previous_button = QPushButton("Previous")
            self.previous_button.setEnabled(False)
            self.previous_button.setFixedWidth(100)
            self.previous_button.clicked.connect(self.previous)
            self.buttons_layout.addWidget(self.previous_button)

        self.OK_button = QPushButton("OK")
        self.OK_button.setFixedWidth(100)
        self.OK_button.clicked.connect(self.ok)
        self.buttons_layout.addWidget(self.OK_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.clicked.connect(self.cancel)
        self.buttons_layout.addWidget(self.cancel_button)

        if len(ids) > 1:
            self.next_button = QPushButton("Next")
            self.next_button.setFixedWidth(100)
            self.next_button.clicked.connect(self.next)
            self.buttons_layout.addWidget(self.next_button)

        self.v_layout.addLayout(self.buttons_layout)
        self.setLayout(self.v_layout)

        self.show_book_prefs()
        self.show()

    @property
    def book(self):
        return self._book_settings[self._index]

    def edit_goodreads_url(self, val):
        goodreads_string = 'https://www.goodreads.com/'
        index = 0
        if val[:len(goodreads_string)] != goodreads_string:
            for i, letter in enumerate(val):
                if i < len(goodreads_string):
                    if letter == goodreads_string[i]:
                            index += 1
                    else:
                        break
                else:
                    break
            self.goodreads_url_edit.setText(goodreads_string + val[index:])

        self.book.goodreads_url = val

    def search_for_goodreads_url(self):
        url = None
        if self.book.title != 'Unknown' and self.book.author != 'Unknown':
            url = self.book.search_goodreads(self.book.title_and_author)
        if url:
            self.update_aliases_button.setEnabled(True)
            self.book.goodreads_url = url
            self.goodreads_url_edit.setText(url)
        else:
            self.status.setText('Goodreads url not found.')
            self.update_aliases_button.setEnabled(False)
            self.goodreads_url_edit.setText('')

    def update_aliases(self):
        try:
            self.book.update_aliases(self.goodreads_url_edit.text(), overwrite=True)
            self.update_aliases_on_gui()
            self.status.setText('Aliases updated.')
        except:
            self.status.setText('Invalid Goodreads url.')

    def edit_aliases(self, term, val):
        self.book.aliases = (term, val)

    def previous(self):
        self.status.setText('')
        self._index -= 1
        self.next_button.setEnabled(True)
        if self._index == 0:
            self.previous_button.setEnabled(False)
        self.show_book_prefs()

    def ok(self):
        for book in self._book_settings:
            book.save()
        self.close()

    def cancel(self):
        self.close()

    def next(self):
        self.status.setText('')
        self._index += 1
        self.previous_button.setEnabled(True)
        if self._index == len(self._book_settings) - 1:
            self.next_button.setEnabled(False)
        self.show_book_prefs()

    def show_book_prefs(self):
        self.setWindowTitle(self.book.title_and_author)
        self.goodreads_url_edit.setText(self.book.goodreads_url)
        self.update_aliases_on_gui()

    def update_aliases_on_gui(self):
        self.aliases_widget = QWidget()
        self.aliases_layout = QGridLayout(self.aliases_widget)
        self.aliases_layout.setAlignment(Qt.AlignTop)

        # add aliases for current book
        for index, aliases in enumerate(sorted(self.book.aliases.items())):
            label = QLabel(aliases[0] + ':')
            label.setFixedWidth(125)
            self.aliases_layout.addWidget(label, index, 0)

            line_edit = QLineEdit(', '.join(aliases[1]))
            line_edit.setFixedWidth(300)
            line_edit.textEdited.connect(functools.partial(self.edit_aliases, aliases[0]))
            self.aliases_layout.addWidget(line_edit, index, 1)

        self.scroll_area.setWidget(self.aliases_widget)