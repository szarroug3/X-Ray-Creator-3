# book_parser.py

import os
import re
from struct import unpack
from random import randrange
from datetime import datetime

from calibre.ebooks.mobi.huffcdic import HuffReader
from calibre.ebooks.mobi.reader.mobi6 import MobiReader
from calibre.ebooks.compression.palmdoc import decompress_doc

class BookParser(object):
    PARAGRAPH_PAT = re.compile(r'<p.*?>.+?(?:<\/p>)', re.I)
    PLAIN_TEXT_PAT = re.compile(r'>([^<]+?)<', re.I)

    def __init__(self, book_type, book_path, goodreads_data, aliases):
        self._book_path = book_path
        self._excerpt_data = {}
        self._entity_data = {}
        self._quotes = goodreads_data.quotes
        self._notable_clips = []
        self._aliases = {}

        self._offset = 0
        if book_type.lower() == 'azw3':
            self._offset = -16

        for char, char_data in goodreads_data.characters.items():
            original = char_data['label']
            label = original.lower()
            desc = char_data['description'] if char_data['description'] else ''
            self._entity_data[label] = {'original_label': original, 'entity_id': char, 'description': desc, 'type': 1, 'mentions': 0, 'excerpt_ids': [], 'occurrence': []}

        for setting, setting_data in goodreads_data.settings.items():
            original = setting_data['label']
            label = original.lower()
            desc = setting_data['description'] if setting_data['description'] else ''
            self._entity_data[label] = {'original_label': original, 'entity_id': setting, 'description': desc, 'type': 2, 'mentions': 0, 'excerpt_ids': [], 'occurrence': []}

        for term, alias_list in aliases.items():
            if term.lower() in self.entity_data.keys():
                for alias in alias_list:
                    self._aliases[alias.lower()] = term.lower()

        words_list = self._aliases.keys() + self.entity_data.keys()

        # named this way to keep same format as other regex's above
        escaped_word_list = [re.escape(word) for word in words_list]
        self.WORD_PAT = re.compile(r'(\b' + r'\b|\b'.join(escaped_word_list) + r'\b)', re.I)

    @property
    def erl(self):
        return self._erl
    
    @property
    def excerpt_data(self):
        return self._excerpt_data

    @property
    def notable_clips(self):
        return self._notable_clips
    

    @property
    def entity_data(self):
        return self._entity_data

    @property
    def codec(self):
        return self._codec   

    def parse(self, log=None):
        self._book_html = MobiExtractor(self._book_path, open(os.devnull, 'w')).extract_text()
        self.find_erl_and_encoding()
        paragraph_data = []

        # find all paragraphs (sections enclosed in html p tags) and their starting offset
        if log: log('%s\t\t\tGetting paragraphs...' % datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        for node in re.finditer(self.PARAGRAPH_PAT, self._book_html):
            # get plain text from paragraph and locations of letters from beginning of file
            results = [(word.group(0)[1:-1].decode(self.codec), word.start(0)) for word in re.finditer(self.PLAIN_TEXT_PAT, node.group(0))]
            word_loc = {'words': '', 'locs': [], 'char_sizes': []}
            for group, loc in results:
                start = node.start(0) + loc + 1 + self._offset
                for char in group:
                    word_loc['words'] += char
                    word_loc['locs'].append(start)
                    start += len(char.encode(self.codec))
                    word_loc['char_sizes'].append(len(char.encode(self.codec)))
            if len(word_loc['locs']) > 0:
                paragraph_data.append((word_loc, word_loc['locs'][0]))

        # get db data
        excerpt_id = 0
        if log: log('%s\t\t\tGetting paragraph data...' % datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        if log: log('%s\t\t\t\tNumber of paragraphs: %s' % (datetime.now().strftime('%m-%d-%Y %H:%M:%S'), len(paragraph_data)))
        for word_loc, para_start in paragraph_data:
            rel_ent = []
            if len(self.entity_data.keys()) > 0:
            # for each match found, fill in entity_data and excerpt_data information
                for match in re.finditer(self.WORD_PAT, word_loc['words']):
                    matched_word = match.group(1).decode(self.codec).lower()
                    if matched_word in self.entity_data.keys():
                        term = matched_word
                    elif matched_word in self._aliases.keys():
                        term = self._aliases[matched_word]
                    entity_id = self._entity_data[term]['entity_id']
                    self._entity_data[term]['mentions'] += 1
                    self._entity_data[term]['excerpt_ids'].append(excerpt_id)
                    self._entity_data[term]['occurrence'].append({'loc': word_loc['locs'][self._find_start(match.start(0), word_loc['words'])],
                                'len': self._find_len_word(match.start(0), match.end(0), word_loc)})
                    if entity_id not in rel_ent:
                        rel_ent.append(entity_id)
            for quote in self._quotes:
                if quote.lower() in word_loc['words'].lower() and excerpt_id not in self._notable_clips:
                    self._notable_clips.append(excerpt_id)
            self._excerpt_data[excerpt_id] = {'loc': para_start, 'len': self._find_len_excerpt(word_loc), 'related_entities': rel_ent}
            excerpt_id += 1

        # add random excerpts to make sure notable clips has at least 20 excerpts
        if len(self._notable_clips) + excerpt_id >= 20:
            num_of_notable_clips = 20
        else:
            num_of_notable_clips = len(self._notable_clips) + excerpt_id
        if self._notable_clips < num_of_notable_clips and log: log('%s\t\t\tGetting extra notable clips...' % datetime.now().strftime('%m-%d-%Y %H:%M:%S'))
        while len(self._notable_clips) < num_of_notable_clips:
            rand_excerpt = randrange(0, excerpt_id - 1)
            if rand_excerpt not in self._notable_clips:
                self._notable_clips.append(rand_excerpt)

    def _find_start(self, start, string):
        previous_space = string[:start].rfind(' ')
        if previous_space == -1:
            previous_space = 0
        else:
            previous_space += 1
        return previous_space

    def _find_len_word(self, start, end, word_loc):
        string = word_loc['words']
        char_sizes = word_loc['char_sizes']

        first_char = string[:start].rfind(' ')
        last_char = string.find(' ', end)

        if first_char == -1:
            first_char = 0
        else:
            first_char += 1
        if last_char == -1:
            last_char = len(string) - 1
        else:
            last_char -= 1

        total_len = 0
        for char in range(first_char, last_char + 1):
            total_len += char_sizes[char]

        return total_len

    def _find_len_excerpt(self, word_loc):
        string = word_loc['words']
        char_sizes = word_loc['char_sizes']

        total_len = 0
        for char in range(0, len(string) ):
            total_len += char_sizes[char]

        return total_len

    def find_erl_and_encoding(self):
        with open(self._book_path, 'rb') as f:
            book_data = f.read()

        nrecs, = unpack('>H', book_data[76:78])
        recs_start = 78 + (nrecs * 8) + 2
        self._erl, = unpack('>L', book_data[recs_start + 4:recs_start + 8])
        self._codec = 'latin-1' if unpack('>L', book_data[recs_start + 28:recs_start + 32])[0] == 1252 else 'utf8'

class MobiExtractor(MobiReader):
    def extract_text(self, offset=1):
        text_sections = [self.text_section(i) for i in range(offset, min(self.book_header.records + offset, len(self.sections)))]
        processed_records = list(range(offset-1, self.book_header.records +
            offset))

        self.mobi_html = b''

        if self.book_header.compression_type == 'DH':
            huffs = [self.sections[i][0] for i in range(self.book_header.huff_offset, self.book_header.huff_offset + self.book_header.huff_number)]
            processed_records += list(range(self.book_header.huff_offset, self.book_header.huff_offset + self.book_header.huff_number))
            huff = HuffReader(huffs)
            unpack = huff.unpack

        elif self.book_header.compression_type == '\x00\x02':
            unpack = decompress_doc

        elif self.book_header.compression_type == '\x00\x01':
            unpack = lambda x: x
        else:
            raise MobiError('Unknown compression algorithm: %s' % repr(self.book_header.compression_type))
        self.mobi_html = b''.join(map(unpack, text_sections))
        if self.mobi_html.endswith(b'#'):
            self.mobi_html = self.mobi_html[:-1]

        if self.book_header.ancient and '<html' not in self.mobi_html[:300].lower():
            self.mobi_html = self.mobi_html.replace('\r ', '\n\n ')
        self.mobi_html = self.mobi_html.replace('\0', '')
        if self.book_header.codec == 'cp1252':
            self.mobi_html = self.mobi_html.replace('\x1e', '')  # record separator
            self.mobi_html = self.mobi_html.replace('\x02', '')  # start of text
        return self.mobi_html