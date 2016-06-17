# db_writer.py

import os
from sqlite3 import *

class DBWriter(object):
	def __init__(self, filename):
		if (os.path.exists(filename)):
			os.remove(filename)
		self._connection = connect(filename)
		self._connection.text_factory = Binary
		self._cursor = self._connection.cursor()
		self._import_base_db()

	def save(self):
		self._connection.commit()

	def close(self):
		self._connection.close()

	def _import_base_db(self):
		self._cursor.execute('PRAGMA user_version = 1')
		self._cursor.execute('PRAGMA encoding = utf8')

		# create tables
		self._cursor.execute('CREATE TABLE type(id INTEGER, label INTEGER, singular_label INTEGER, icon INTEGER, top_mentioned_entities TEXT, PRIMARY KEY(id))')
		self._cursor.execute('CREATE TABLE string(id INTEGER, language TEXT, text TEXT)')
		self._cursor.execute('CREATE TABLE source(id INTEGER, label INTEGER, url INTEGER, license_label INTEGER, license_url INTEGER, PRIMARY KEY(id))')
		self._cursor.execute('CREATE TABLE occurrence(entity INTEGER, start INTEGER, length INTEGER)')
		self._cursor.execute('CREATE TABLE excerpt(id INTEGER, start INTEGER, length INTEGER, image TEXT, related_entities TEXT, goto INTEGER, PRIMARY KEY(id))')
		self._cursor.execute('CREATE TABLE entity_excerpt(entity INTEGER, excerpt INTEGER)')
		self._cursor.execute('CREATE TABLE entity_description(text TEXT, source_wildcard TEXT, source INTEGER, entity INTEGER, PRIMARY KEY(entity))')
		self._cursor.execute('CREATE TABLE entity(id INTEGER, label TEXT, loc_label INTEGER, type INTEGER, count INTEGER, has_info_card TINYINT, PRIMARY KEY(id))')
		self._cursor.execute('CREATE TABLE book_metadata(srl INTEGER, erl INTEGER, has_images TINYINT, has_excerpts TINYINT, show_spoilers_default TINYINT, num_people INTEGER, num_terms INTEGER, num_images INTEGER, preview_images TEXT)')

		# insert base data
		self._insert_into_table('type', self.BASE_DB_TYPE)
		self._insert_into_table('source', self.BASE_DB_SOURCE)
		self._insert_into_table('entity', self.BASE_DB_ENTITY)
		self._insert_into_table('string', self.BASE_DB_STRING)

	def _insert_into_table(self, tableName, data):
		if len(data) == 0: return
		if isinstance(data, list):
			params = ['?' for d in data[0]]
			self._cursor.executemany('INSERT INTO %s VALUES (%s)' % (tableName, ','.join(params)), data)
		elif isinstance(data, tuple):
			params = ['?' for d in data]
			self._cursor.execute('INSERT INTO %s VALUES (%s)' % (tableName, ','.join(params)), data)
		else:
			raise ValueError('data is invalid. Expected list or tuple, found %s' % type(data))

	def insert_into_book_metadata(self, data):
		'''Insert data into the book_metadata table'''
		self._insert_into_table('book_metadata', data)

	def insert_into_entity(self, data):
		'''Insert data into the entity table'''
		self._insert_into_table('entity', data)

	def insert_into_entity_description(self, data):
		'''Insert data into the entity_description table'''
		self._insert_into_table('entity_description', data)

	def insert_into_entity_excerpt(self, data):
		'''Insert data into the entity_excerpt table'''
		self._insert_into_table('entity_excerpt', data)

	def insert_into_excerpt(self, data):
		'''Insert data into the excerpt table'''
		self._insert_into_table('excerpt', data)

	def insert_into_occurrence(self, data):
		'''Insert data into the occurrence table'''
		self._insert_into_table('occurrence', data)

	def update_string(self, url):
		'''Update Goodreads url in string table'''
		self._cursor.execute('UPDATE string SET text=? WHERE id=15', (url,))
		self._connection.commit()

	def update_type(self, type_id, data):
		'''Update top_mentioned_entities in type table'''
		if type_id != 1 and type_id != 2:
			raise ValueError('type_id %i is invalid; must be 1 or 2.' % type_id)
		self._cursor.execute('UPDATE type SET top_mentioned_entities=? WHERE id=?', (data, type_id))

	def create_indices(self):
		self._cursor.execute('CREATE INDEX idx_entity_excerpt ON entity_excerpt(entity ASC)')
		self._cursor.execute('CREATE INDEX idx_entity_type ON entity(type ASC)')
		self._cursor.execute('CREATE INDEX idx_occurrence_start ON occurrence(start ASC)')





	BASE_DB_TYPE = [('1','7','8','1', ''), ('2','9','10','2', '')]
	BASE_DB_SOURCE = [('0','3','13',None,None), ('1','4','14','5','6'), ('2','2','15',None,None)]
	BASE_DB_ENTITY = ('0',None,'1',None,None,'0')
	BASE_DB_STRING = [('0','de','Alle'),
						('0','en','All'),
						('0','en-US','All'),
						('0','es','Todo'),
						('0','fr','Toutes'),
						('0','it','Tutto'),
						('0','ja','すべて'),
						('0','nl','Alles'),
						('0','pt-BR','Todos'),
						('0','ru','Все'),
						('0','zh-CN','全部'),
						('1','de','Buch'),
						('1','en','Book'),
						('1','en-US','Book'),
						('1','es','Libro'),
						('1','fr','Livre'),
						('1','it','Libro'),
						('1','ja','本'),
						('1','nl','Boeken'),
						('1','pt-BR','eBook'),
						('1','ru','Книга'),
						('1','zh-CN','电子书'),
						('2','de','goodreads'),
						('2','en','goodreads'),
						('2','en-US','goodreads'),
						('2','es','goodreads'),
						('2','fr','goodreads'),
						('2','it','goodreads'),
						('2','ja','goodreads'),
						('2','nl','goodreads'),
						('2','pt-BR','goodreads'),
						('2','ru','goodreads'),
						('2','zh-CN','goodreads'),
						('3','de','Kindle-Shop'),
						('3','en','Kindle Store'),
						('3','en-US','Kindle Store'),
						('3','es','Tienda Kindle'),
						('3','fr','Boutique Kindle'),
						('3','it','Kindle Store'),
						('3','ja','Kindleストア'),
						('3','nl','Kindle-winkel'),
						('3','pt-BR','Loja Kindle'),
						('3','ru','Магазин Kindle'),
						('3','zh-CN','Kindle 商店'),
						('4','de','Wikipedia'),
						('4','en','Wikipedia'),
						('4','en-US','Wikipedia'),
						('4','es','Wikipedia'),
						('4','fr','Wikipédia'),
						('4','it','Wikipedia'),
						('4','ja','Wikipedia'),
						('4','nl','Wikipedia'),
						('4','pt-BR','Wikipédia'),
						('4','ru','Википедия'),
						('4','zh-CN','维基百科'),
						('5','en','Creative Commons Attribution Share-Alike license'),
						('6','en','http://creativecommons.org/licenses/by-sa/3.0/legalcode'),
						('1000','de','Wichtige Clips'),
						('1000','en','Notable Clips'),
						('1000','en-US','Notable Clips'),
						('1000','es','Recortes destacables'),
						('1000','fr','Clips Notable'),
						('1000','it','Ritagli rilevanti'),
						('1000','ja','重要な抜粋'),
						('1000','nl','Opvallende clips'),
						('1000','pt-BR','Recortes notáveis'),
						('1000','ru','Важные отрывки'),
						('1000','zh-CN','选段'),
						('1001','de','Wichtige Clips'),
						('1001','en','Notable Clips'),
						('1001','en-US','Notable Clips'),
						('1001','es','Recortes destacables'),
						('1001','fr','Clips Notable'),
						('1001','it','Ritagli rilevanti'),
						('1001','ja','重要な抜粋'),
						('1001','nl','Opvallende clips'),
						('1001','pt-BR','Recortes notáveis'),
						('1001','ru','Важные отрывки'),
						('1001','zh-CN','选段'),
						('7','de','Personen'),
						('7','en','People'),
						('7','en-US','People'),
						('7','es','Gente'),
						('7','fr','Personnes'),
						('7','it','Persone'),
						('7','ja','人物'),
						('7','nl','Mensen'),
						('7','pt-BR','Pessoas'),
						('7','ru','Люди'),
						('7','zh-CN','人物'),
						('8','de','Person'),
						('8','en','Person'),
						('8','en-US','Person'),
						('8','es','Persona'),
						('8','fr','Personne'),
						('8','it','Persona'),
						('8','ja','人物'),
						('8','nl','Persoon'),
						('8','pt-BR','Pessoa'),
						('8','ru','Человек'),
						('8','zh-CN','人物'),
						('9','de','Begriffe'),
						('9','en','Terms'),
						('9','en-US','Terms'),
						('9','es','Términos'),
						('9','fr','Termes'),
						('9','it','Termini'),
						('9','ja','トピック'),
						('9','nl','Termen'),
						('9','pt-BR','Termos'),
						('9','ru','Термины'),
						('9','zh-CN','术语'),
						('10','de','Begriff'),
						('10','en','Term'),
						('10','en-US','Term'),
						('10','es','Término'),
						('10','fr','Terme'),
						('10','it','Termine'),
						('10','ja','トピック'),
						('10','nl','Term'),
						('10','pt-BR','Termo'),
						('10','ru','Термин'),
						('10','zh-CN','术语'),
						('11','de','Themen'),
						('11','en','Themes'),
						('11','en-US','Themes'),
						('11','es','Temas'),
						('11','fr','Thèmes'),
						('11','it','Temi'),
						('11','ja','テーマ'),
						('11','nl','Thema''s'),
						('11','pt-BR','Tema'),
						('11','ru','Темы'),
						('11','zh-CN','主题'),
						('12','de','Thema'),
						('12','en','Theme'),
						('12','en-US','Theme'),
						('12','es','Tema'),
						('12','fr','Thème'),
						('12','it','Tema'),
						('12','ja','テーマ'),
						('12','nl','Thema''s'),
						('12','pt-BR','Tema'),
						('12','ru','Тема'),
						('12','zh-CN','主题'),
						('13','en','store://%s'),
						('14','en','http://en.wikipedia.org/wiki/%s'),
						('15','en','http://www.goodreads.com')]