# book_settings.py

import os
import re
import functools
from urllib import urlencode
from httplib import HTTPSConnection

from calibre_plugins.xray_creator.lib.goodreads_parser import GoodreadsParser

from calibre.utils.config import JSONConfig
from calibre.library import current_library_path
from calibre.ebooks.BeautifulSoup import BeautifulSoup

class BookSettings(object):
    GOODREADS_URL_PAT = re.compile(r'href="(/book/show/.+?)"')

    HEADERS = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    LIBRARY = current_library_path()
    HONORIFICS = 'mr mrs ms esq prof dr fr rev pr atty adv hon pres gov sen ofc pvt cpl sgt maj capt cmdr lt col gen'
    HONORIFICS = HONORIFICS.split()
    HONORIFICS.extend([x + '.' for x in HONORIFICS])
    HONORIFICS += 'miss master sir madam lord dame lady esquire professor doctor father mother brother sister reverend pastor elder rabbi sheikh'.split()
    HONORIFICS += 'attorney advocate honorable president governor senator officer private corporal sargent major captain commander lieutenant colonel general'.split()
    RELIGIOUS_HONORIFICS = 'fr br sr rev pr'
    RELIGIOUS_HONORIFICS = RELIGIOUS_HONORIFICS.split()
    RELIGIOUS_HONORIFICS.extend([x + '.' for x in RELIGIOUS_HONORIFICS])
    RELIGIOUS_HONORIFICS += 'father mother brother sister reverend pastor elder rabbi sheikh'.split()
    DOUBLE_HONORIFICS = 'lord'
    # We want all the honorifics to be in the general honorifics list so when we're checking if a word is an honorifics, we only need to search in one list
    HONORIFICS += RELIGIOUS_HONORIFICS
    HONORIFICS += DOUBLE_HONORIFICS

    COMMON_WORDS = 'the of de'.split()

    def __init__(self, db, book_id, connection):
        self._db = db
        self._book_id = book_id
        self._connection = connection

        book_path = self._db.field_for('path', book_id).replace('/', os.sep)

        self._prefs = JSONConfig(os.path.join(book_path, 'book_settings'), base_path=self.LIBRARY)
        self._prefs.setdefault('goodreads_url', '')
        self._prefs.setdefault('aliases', {})
        self._prefs.commit()

        self._title = self._db.field_for('title', book_id)
        self._author = ' & '.join(self._db.field_for('authors', self._book_id))

        self.goodreads_url = self._prefs['goodreads_url']
        if self.goodreads_url == '':
            url = None
            if self.title != 'Unknown' and self.author != 'Unknown':
                url = self.search_goodreads(self.title_and_author)

            if url:
                self.goodreads_url = url
                self._prefs['goodreads_url'] = self.goodreads_url

        self._aliases = self._prefs['aliases']
        if len(self._aliases.keys()) == 0 and self.goodreads_url != '':
            self.update_aliases(self.goodreads_url)
        self.save()

    @property
    def prefs(self):
        return self._prefs

    @property
    def title(self):
        return self._title
    
    @property
    def author(self):
        return self._author

    @property
    def title_and_author(self):
        return '%s - %s' % (self.title, self.author)

    @property
    def goodreads_url(self):
        return self._goodreads_url
    
    @goodreads_url.setter
    def goodreads_url(self, val):
        self._goodreads_url = val

    @property
    def aliases(self):
        return self._aliases

    @aliases.setter
    def aliases(self, val):
        # 'aliases' is a string containing a comma separated list of aliases.  
        #
        # Split it, remove whitespace from each element, drop empty strings (strangely, split only does this if you don't specify a separator)
        #
        # so "" -> []  "foo,bar" and " foo   , bar " -> ["foo", "bar"]
        label, aliases = val
        aliases = [x.strip() for x in aliases.split(",") if x.strip()]
        self._aliases[label] =  aliases

    def save(self):
        self._prefs['goodreads_url'] = self.goodreads_url
        self._prefs['aliases'] = self.aliases

    def search_goodreads(self, keywords):
        query = urlencode ({'q': keywords})
        try:
            self._connection.request('GET', '/search?' + query)
            response = self._connection.getresponse().read()
        except:
            try:
                self._connection.close()
                if self._proxy:
                    self._connection = HTTPSConnection(self._https_address, self._https_port)
                    self._connection.set_tunnel('www.goodreads.com', 443)
                else:
                    self._connection = HTTPSConnection('www.goodreads.com')

                self._connection.request('GET', '/search?' + query)
                response = self._connection.getresponse().read()
            except:
                return None
        
        # check to make sure there are results
        if 'No results' in response:
            return None

        urlsearch = self.GOODREADS_URL_PAT.search(response)
        if not urlsearch:
            return None

        return 'https://www.goodreads.com' + urlsearch.group(1)

    def update_aliases(self, url, overwrite=False):
        goodreads_parser = GoodreadsParser(url, self._connection)
        goodreads_parser.get_characters()
        goodreads_parser.get_settings()
        goodreads_chars =  goodreads_parser.characters

        if overwrite:
            self._prefs['aliases'] = {}
            self._aliases = {}
        
        characters = []
        alias_lookup = {}
        for char, char_data in goodreads_chars.items():
            characters.append(char_data['label'])
            alias_lookup[char_data['label']] = char_data['label']

            if char_data['label'] not in self.aliases.keys():
                self.aliases = (char_data['label'], ','.join(goodreads_chars[char]['aliases']))

            for alias in char_data['aliases']:
                characters.append(alias)
                alias_lookup[alias] = char_data['label']

        aliases = self.auto_expand_aliases(characters)
        for alias, fullname in aliases.items():
            self.aliases = (alias_lookup[fullname], alias + ',' + ','.join(self.aliases[alias_lookup[fullname]]))

        for setting, setting_data in goodreads_parser.settings.items():
            self.aliases = (setting_data['label'], '')

    def auto_expand_aliases(self, characters):
        actual_aliases = {}
        duplicates = [x.lower() for x in characters]
        for fullname in characters:
            aliases = self.fullname_to_possible_aliases(fullname.lower())
            for alias in aliases:
                # if this alias has already been flagged as a duplicate or is a common word, skip it
                if alias in duplicates or alias in self.COMMON_WORDS:
                    continue
                # check if this alias is a duplicate but isn't in the duplicates list
                if actual_aliases.has_key(alias):
                    duplicates.append(alias)
                    actual_aliases.pop(alias)
                    continue

                # at this point, the alias is new -- add it to the dict with the alias as the key and fullname as the value
                actual_aliases[alias] = fullname

        return actual_aliases

    def fullname_to_possible_aliases(self, fullname):
        """
        Given a full name ("{Title} ChristianName {Middle Names} {Surname}"), return a list of possible aliases
        
        ie. Title Surname, ChristianName Surname, Title ChristianName, {the full name}
        
        The returned aliases are in the order they should match
        """
        aliases = []        
        parts = fullname.split()

        if parts[0].lower() in self.HONORIFICS:
            title = []
            while len(parts) > 0 and parts[0].lower() in self.HONORIFICS:
                title.append(parts.pop(0))
            title = ' '.join(title)
        else:
            title = None
            
        if len(parts) >= 2:
            # Assume: {Title} Firstname {Middlenames} Lastname
            # Already added the full form, also add Title Lastname, and for some Title Firstname
            surname = parts.pop() # This will cover double barrel surnames, we split on whitespace only
            christian_name = parts.pop(0)
            middlenames = parts
            if title:
                # Religious Honorifics usually only use {Title} {ChristianName}
                # ie. John Doe could be Father John but usually not Father Doe
                if title in self.RELIGIOUS_HONORIFICS:
                    aliases.append("%s %s" % (title, christian_name))
                # Some titles work as both {Title} {ChristianName} and {Title} {Lastname}
                # ie. John Doe could be Lord John or Lord Doe
                elif title in self.DOUBLE_HONORIFICS:
                    aliases.append("%s %s" % (title, christian_name))
                    aliases.append("%s %s" % (title, surname))
                # Everything else usually goes {Title} {Lastname}
                # ie. John Doe could be Captain Doe but usually not Captain John
                else:
                    aliases.append("%s %s" % (title, surname))
            aliases.append(christian_name)
            aliases.append(surname)
            aliases.append("%s %s" % (christian_name, surname))

        elif title:
            # Odd, but got Title Name (eg. Lord Buttsworth), so see if we can alias
            if len(parts) > 0:
                aliases.append(parts[0])
        else:
            # We've got no title, so just a single word name.  No alias needed
            pass
        return aliases