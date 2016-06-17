# xray_db_writer.py

import os

from calibre_plugins.xray_creator.lib.db_writer import DBWriter

class XRayDBWriter(object):
    def __init__(self, xray_directory, goodreads_url, parsed_data):
        self._filename = os.path.join(xray_directory, 'XRAY.asc')
        if not os.path.exists(xray_directory): os.mkdir(xray_directory)
        self._goodreads_url = goodreads_url
        self._db_writer = DBWriter(self._filename)
        self._erl = parsed_data.erl
        self._excerpt_data = parsed_data.excerpt_data
        self._notable_clips = parsed_data.notable_clips
        self._entity_data = parsed_data.entity_data
        self._codec = parsed_data.codec

    def create_xray(self):
        self.fill_book_metadata()
        self.fill_entity()
        self.fill_entity_description()
        self.fill_entity_excerpt()
        self.fill_excerpt()
        self.fill_occurrence()
        self.update_string()
        self.update_type()
        self._db_writer.create_indices()
        self._db_writer.save()
        self._db_writer.close()

    def fill_book_metadata(self):
        srl = num_images = show_spoilers_default = '0'.encode(self._codec);
        has_excerpts = '1'.encode(self._codec) if self._excerpt_data > 0 else '0'.encode(self._codec)
        num_people = str(sum(1 for char in self._entity_data.keys() if self._entity_data[char]['type'] == 1)).encode(self._codec)
        num_terms = str(sum(1 for term in self._entity_data.keys() if self._entity_data[term]['type'] == 2)).encode(self._codec)
        self._db_writer.insert_into_book_metadata((srl, self._erl, 0, has_excerpts, show_spoilers_default, num_people, num_terms, num_images, None))

    def fill_entity(self):
        entity_data = []
        for entity in self._entity_data.keys():
            original_label = self._entity_data[entity]['original_label']
            entity_id = str(self._entity_data[entity]['entity_id']).encode(self._codec)
            entity_type = str(self._entity_data[entity]['type']).encode(self._codec)
            count = str(self._entity_data[entity]['mentions']).encode(self._codec)
            has_info_card = '1'.encode(self._codec) if self._entity_data[entity]['description'] else '0'.encode(self._codec)
            entity_data.append((entity_id, original_label.encode(self._codec), None, entity_type, count, has_info_card))
        self._db_writer.insert_into_entity(entity_data)

    def fill_entity_description(self):
        entity_description_data = []
        for entity in self._entity_data.keys():
            original_label = self._entity_data[entity]['original_label']
            entity_id = str(self._entity_data[entity]['entity_id']).encode(self._codec)
            text = str(self._entity_data[entity]['description']).encode(self._codec)
            source = '2'.encode(self._codec)
            entity_description_data.append((text, original_label.encode(self._codec), source, entity_id))
        self._db_writer.insert_into_entity_description(entity_description_data)

    def fill_entity_excerpt(self):
        entity_excerpt_data = []

        # add notable clips to entity_excerpt as entity 0
        for notable_clip in self._notable_clips:
            entity_excerpt_data.append(('0'.encode(self._codec), str(notable_clip).encode(self._codec)))

        for entity in self._entity_data.keys():
            entity_id = str(self._entity_data[entity]['entity_id']).encode(self._codec)
            for excerpt_id in self._entity_data[entity]['excerpt_ids']:
                entity_excerpt_data.append((str(entity_id).encode(self._codec), str(excerpt_id).encode(self._codec)))
        self._db_writer.insert_into_entity_excerpt(entity_excerpt_data)

    def fill_excerpt(self):
        excerpt_data = []
        for excerpt_id in self._excerpt_data.keys():
            if len(self._excerpt_data[excerpt_id]['related_entities']) > 0 or excerpt_id in self._notable_clips:
                start = str(self._excerpt_data[excerpt_id]['loc']).encode(self._codec)
                length = str(self._excerpt_data[excerpt_id]['len']).encode(self._codec)
                image = ''.encode(self._codec)
                related_entities = ','.join([str(entity_id) for entity_id in self._excerpt_data[excerpt_id]['related_entities']]).encode(self._codec)
                excerpt_data.append((str(excerpt_id).encode(self._codec), start, length, image, related_entities, None))
        self._db_writer.insert_into_excerpt(excerpt_data)

    def fill_occurrence(self):
        occurrence_data = []
        for entity in self._entity_data.keys():
            entity_id = str(self._entity_data[entity]['entity_id']).encode(self._codec)
            for excerpt in self._entity_data[entity]['occurrence']:
                occurrence_data.append((entity_id, str(excerpt['loc']).encode(self._codec), str(excerpt['len']).encode(self._codec)))
        self._db_writer.insert_into_occurrence(occurrence_data)

    def update_string(self):
        self._db_writer.update_string(self._goodreads_url.encode(self._codec))

    def update_type(self):
        top_mentioned_people = [(str(self._entity_data[entity]['entity_id']), self._entity_data[entity]['mentions']) for entity in self._entity_data.keys() if self._entity_data[entity]['type'] == 1]
        top_mentioned_people.sort(key=lambda x:x[1], reverse=True)
        if len(top_mentioned_people) > 10:
            top_mentioned_people = top_mentioned_people[:10]
        top_mentioned_people = [entity_id for entity_id, mentions in top_mentioned_people]
        self._db_writer.update_type(1, ','.join(top_mentioned_people).encode(self._codec))

        top_mentioned_terms = [(str(self._entity_data[entity]['entity_id']), self._entity_data[entity]['mentions']) for entity in self._entity_data.keys() if self._entity_data[entity]['type'] == 2]
        top_mentioned_terms.sort(key=lambda x:x[1], reverse=True)
        if len(top_mentioned_terms) > 10:
            top_mentioned_terms = top_mentioned_terms[:10]
        top_mentioned_terms = [entity_id for entity_id, mentions in top_mentioned_terms]
        self._db_writer.update_type(2, ','.join(top_mentioned_terms).encode(self._codec))