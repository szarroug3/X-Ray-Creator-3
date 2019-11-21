# book_parser.py
'''Parses book using given information'''

import os
import re
from struct import unpack, error
from random import shuffle

from calibre.ebooks.mobi import MobiError
from calibre.ebooks.mobi.huffcdic import HuffReader
from calibre.ebooks.mobi.reader.mobi6 import MobiReader
from calibre.ebooks.compression.palmdoc import decompress_doc


PATTERNS = [r'(<)(p|i|h\d).*?>([^a-zA-Z0-9\s]*{}(?:[^a-zA-Z0-9\s]*?|[^a-zA-Z0-9\s]+\S*?))<\/\2.*?(>)', # word is the paragraph
            r'(<)(p|i|h\d).*?>([^a-zA-Z0-9\s]*{}(?:[^a-zA-Z0-9\s]*?|[^a-zA-Z0-9\s]+\S*?))\s.*?<\/\2.*?(>)', # beginning of paragraph
            r'(<)(p|i|h\d).*?>.*?\s([^a-zA-Z0-9\s]*{}(?:[^a-zA-Z0-9\s]*?|[^a-zA-Z0-9\s]+\S*?))<\/\2.*?(>)', # end of paragraph
            r'(<)(p|i|h\d).*?>.*?\s([^a-zA-Z0-9\s]*{}(?:[^a-zA-Z0-9\s]*?|[^a-zA-Z0-9\s]+\S*?))\s.*?<\/\2.*?(>)'] # middle of paragraph


class BookParser(object):
    '''Class to parse book using information from user and goodreads'''

    def __init__(self, book_type, book_path, goodreads_data, aliases):
        self._book_path = book_path
        self._entity_data = {}
        self._quotes = goodreads_data['quotes']
        self._aliases = {}
        self._excerpts = {}
        self._excerpt_id = 0
        self._excerpt_to_id = {}

        self._offset = 0
        if book_type.lower() == 'azw3':
            self._offset = -16

        for char, char_data in goodreads_data['characters'].items():
            original = char_data['label']
            label = original.lower()
            desc = char_data['description']
            self._entity_data[label] = {'original_label': original, 'entity_id': char, 'description': desc,
                                        'type': 1, 'mentions': 0, 'excerpt_ids': [], 'occurrence': []}

        for setting, setting_data in goodreads_data['settings'].items():
            original = setting_data['label']
            label = original.lower()
            desc = setting_data['description']
            self._entity_data[label] = {'original_label': original, 'entity_id': setting, 'description': desc,
                                        'type': 2, 'mentions': 0, 'excerpt_ids': [], 'occurrence': []}

        for term, alias_list in aliases.items():
            if term.lower() in self._entity_data.keys():
                for alias in alias_list:
                    self._aliases[alias.lower()] = term.lower()

    def parse(self):
        '''Parses book'''
        erl, codec = self.find_erl_and_encoding()
        book_html = MobiExtractor(self._book_path, open(os.devnull, 'w')).extract_text()

        occurrence_start = []
        for word, entity_data in self._entity_data.items():
            self._get_occurrences(book_html, word, entity_data, occurrence_start)

        for alias, original in self._aliases.items():
            entity_data = self._entity_data[original]
            self._get_occurrences(book_html, alias, entity_data, occurrence_start)

        return {'erl': erl,
                'excerpt_data': self._excerpts,
                'notable_clips': self._get_notable_clips(),
                'entity_data': self._entity_data,
                'codec': codec}

    def _get_occurrences(self, book_html, word, entity_data, occurrence_start):
        """
        Get the occurences of the word in the book html

        Args:
            :str book_html: the book's text
            :str word: the word we're looking for
            :dict entity_data: dictionary of entity data
            :list occurrence_start: list of occurrence start locations we've come across
        """
        entity_id = entity_data['entity_id']
        occurrences = entity_data['occurrence']
        excerpt_ids = entity_data['excerpt_ids']

        for pattern in PATTERNS:
            re_pat = re.compile(pattern.format(word), re.I)
            for node in re.finditer(re_pat, book_html):
                excerpt = node.group(0)
                excerpt_start = node.start(1) + self._offset
                excerpt_len = node.start(4) - node.start(1)
                word_start = node.start(3) + self._offset
                word_len = node.end(3) - node.start(3)

                if word_start in occurrence_start:
                    continue
                occurrence_start.append(word_start)

                if excerpt in self._excerpt_to_id.keys():
                    occurrence_excerpt_id = self._excerpt_to_id[excerpt]
                    if entity_id not in self._excerpts[occurrence_excerpt_id]['related_entities']:
                        self._excerpts[occurrence_excerpt_id]['related_entities'].append(entity_id)
                else:
                    occurrence_excerpt_id = self._excerpt_id
                    self._excerpts[occurrence_excerpt_id] = {'loc': excerpt_start,
                                                             'len': excerpt_len,
                                                             'related_entities': [entity_id]}
                    self._excerpt_to_id[excerpt] = occurrence_excerpt_id
                    self._excerpt_id += 1

                if occurrence_excerpt_id not in excerpt_ids:
                    occurrences.append({'loc': word_start, 'len': word_len})
                    excerpt_ids.append(occurrence_excerpt_id)
                    entity_data['mentions'] += 1

    def _get_notable_clips(self):
        """
        Gets notable clips from excerpts

        Will pad notable clips to 20 if possible

        Returns:
            list: notable clips
        """
        notable_clips = []
        num_excerpts = len(self._excerpts)

        for quote in self._quotes:
            quote_excerpt_id = self._excerpt_to_id.get(quote)
            if quote_excerpt_id:
                notable_clips.append(quote_excerpt_id)

        if num_excerpts == 0 or len(notable_clips) >= 20:
            return notable_clips

        if len(notable_clips) + num_excerpts >= 20:
            num_of_notable_clips = 20
        else:
            num_of_notable_clips = len(notable_clips) + num_excerpts

        excerpts_available = range(0, num_excerpts)
        shuffle(excerpts_available)
        while len(notable_clips) < num_of_notable_clips:
            rand_excerpt = excerpts_available.pop() if num_excerpts > 1 else 1
            if rand_excerpt not in notable_clips:
                notable_clips.append(rand_excerpt)

        return notable_clips

    def find_erl_and_encoding(self):
        '''Finds book's erl and codec'''
        with open(self._book_path, 'rb') as fname:
            book_data = fname.read()

        try:
            nrecs, = unpack('>H', book_data[76:78])
            recs_start = 78 + (nrecs * 8) + 2
            erl, = unpack('>L', book_data[recs_start + 4:recs_start + 8])
            codec = 'cp1252' if unpack('>L', book_data[recs_start + 28:recs_start + 32])[0] == 1252 else 'utf8'
            return erl, codec
        except error:
            raise MobiError

class MobiExtractor(MobiReader):
    '''Reads MOBI file'''
    def extract_text(self, offset=1):
        '''Gets text from file'''
        text_sections = [self.text_section(i) for i in range(offset, min(self.book_header.records + offset,
                                                                         len(self.sections)))]
        processed_records = list(range(offset-1, self.book_header.records +
                                       offset))

        mobi_html = b''

        if self.book_header.compression_type == 'DH':
            huffs = [self.sections[i][0] for i in range(self.book_header.huff_offset,
                                                        self.book_header.huff_offset + self.book_header.huff_number)]
            processed_records += list(range(self.book_header.huff_offset,
                                            self.book_header.huff_offset + self.book_header.huff_number))
            huff = HuffReader(huffs)
            huff_unpack = huff.unpack

        elif self.book_header.compression_type == '\x00\x02':
            huff_unpack = decompress_doc

        elif self.book_header.compression_type == '\x00\x01':
            huff_unpack = lambda x: x
        else:
            raise MobiError('Unknown compression algorithm: %s' % repr(self.book_header.compression_type))
        mobi_html = b''.join(map(huff_unpack, text_sections))
        if mobi_html.endswith(b'#'):
            mobi_html = mobi_html[:-1]

        if self.book_header.ancient and '<html' not in mobi_html[:300].lower():
            mobi_html = mobi_html.replace('\r ', '\n\n ')
        mobi_html = mobi_html.replace('\0', '')
        if self.book_header.codec == 'cp1252':
            mobi_html = mobi_html.replace('\x1e', '')  # record separator
            mobi_html = mobi_html.replace('\x02', '')  # start of text
        return mobi_html
