#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'

'''
textsearch.py

@since: 2013-08-01
@version: 2023-09-15
@author: Tran Minh Phuc
'''

# set default encodeing to utf-8
from flask import render_template, request, make_response
import json
from sateraito_logger import logging
import datetime
import unicodedata

import google.appengine.api.runtime

from google.appengine.api import taskqueue, memcache
# from gdata.apps.service import AppsForYourDomainException

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page

if sateraito_inc.ES_SEARCH_MODE:
	from search_alt import search_replace as search
else:
	from google.appengine.api import search


MAX_NUM_STORE_SEARCH_HISTORY = 100		# maximum number to store search history words


class TqBuildSearchIndexForAllDocs(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return

		self.buildSearchIndexForAllDocs()

		return make_response('', 200)
	
	def buildSearchIndexForAllDocs(self):
		""" check all docs in the namespace
		  add fulltext index for published doc IF IT HAVE NO INDEX
		  remove fulltext index for un-published doc IF IT HAVE INDEX
		  this function is called at the end of Notes DB upload program
		"""
		
		index = search.Index(name=sateraito_func.INDEX_SEARCH_WORKFLOW_DOC)
		
		q = sateraito_db.WorkflowDoc.query()
		NUM_PER_PAGE = 50
		MAX_PAGE = 1000  # check 50,000 documents max
		for page in range(MAX_PAGE):
			rows = q.fetch(limit=NUM_PER_PAGE, offset=(page * NUM_PER_PAGE))
			logging.info('page ' + str(page))
			if len(rows) == 0:
				break
			for row in rows:
				logging.info('processing doc_id=' + row.doc_id)
				if row.published:
					# PUBLISHED DOC
					index_found = False
					documents = index.get_range(start_id=row.doc_id, limit=1)
					for document in documents:
						if document.doc_id == row.doc_id:
							index_found = True
					if index_found:
						logging.info('Index found for published doc. No operation')
					else:
						logging.info('No index found for published doc, ADDING...')
						sateraito_func.addDocToTextSearchIndex(row)
					
					documents = None		# for collect garbage
				else:
					# UN-Published doc
					index_found = False
					documents = index.get_range(start_id=row.doc_id, limit=1)
					for document in documents:
						doc_id = document.doc_id
						if doc_id == row.doc_id:
							index_found = True
					if index_found:
						logging.info('Index found for un-published doc, REMOVING...')
						sateraito_func.removeDocFromIndex(row.doc_id)
					else:
						logging.info('No index found for un-pulished doc. No operation')
					
					documents = None		# for collect garbage
			
			rows = None		# for collect garbage


class _CheckFulltextReady(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" check if UserInfo data for fulltext search up-to-date
	"""
	
	def process(self, google_apps_domain, app_id):
		# set response header
		self.setResponseHeader('Content-Type', 'application/json')
		# compate date in UserAccessibleInfo
		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email, auto_create=True)
		if user_accessible_info_dict is None:
			# user_accessible_info is not registered to this user
			ret_obj = {
				'is_ready': False,
			}
			return json.JSONEncoder().encode(ret_obj)
		# check if updating process is running
		start_date = user_accessible_info_dict['accessible_cat_and_type_update_start_date']
		logging.info('start_date=' + str(start_date))
		if start_date is not None and start_date > datetime.datetime.now() - datetime.timedelta(minutes=30):
			# start_date is older than 30 min before
			logging.info('start_date is older than 30 min before')
			if user_accessible_info_dict['accessible_cat_and_type_updated_date'] is None:
				# updating process now running
				ret_obj = {
					'is_ready': False,
				}
				return json.JSONEncoder().encode(ret_obj)
			elif user_accessible_info_dict['accessible_cat_and_type_update_start_date'] < user_accessible_info_dict['accessible_cat_and_type_updated_date']:
				# updating process not running
				logging.info('updating process not running:user_accessible_info.accessible_cat_and_type_update_start_date=' + str(user_accessible_info_dict['accessible_cat_and_type_update_start_date']) + ' user_accessible_info.accessible_cat_and_type_updated_date=' + str(user_accessible_info_dict['accessible_cat_and_type_updated_date']))
			else:
				# now updating process running
				logging.info('now updating start_date=' + str(user_accessible_info_dict['accessible_cat_and_type_update_start_date']) + ' finished_date=' + str(user_accessible_info_dict['accessible_cat_and_type_updated_date']))
				ret_obj = {
					'is_ready': False,
				}
				return json.JSONEncoder().encode(ret_obj)
		# check if UPDATING is needed
		google_apps_user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, self.viewer_email)
		is_ready = sateraito_func.isFulltextReady(user_accessible_info_dict, google_apps_user_entry_dict)
		logging.info('is_ready=' + str(is_ready))
		if not is_ready:
			logging.info('need update, adding task')
			# immediate update accessible info
			queue = taskqueue.Queue('update-accessible-info')
			task = taskqueue.Task(
				url='/' + google_apps_domain + '/' + app_id + '/textsearch/tq/updateaccessibleinfo',
				params={
					'user_email': self.viewer_email
				},
				target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
				countdown=0
			)
			queue.add(task)
			# re-check accessible info is updated after 15 minutes
			sateraito_func.addCheckAccessibleInfoQueue(google_apps_domain, app_id, self.viewer_email, countdown=(60 * 15))
			# now updating process kicked, not ready for fulltext search
			ret_obj = {
				'is_ready': False,
			}
			return json.JSONEncoder().encode(ret_obj)
		# now ready for fulltext search
		ret_obj = {
			'is_ready': True,
		}
		return json.JSONEncoder().encode(ret_obj)

class CheckFulltextReady(_CheckFulltextReady):
	""" check if UserInfo data for fulltext search up-to-date
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkGadgetRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)

class CheckFulltextReadyOid(_CheckFulltextReady):
	""" check if UserInfo data for fulltext search up-to-date
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)


class TqUpdateAccessibleInfo(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self, google_apps_domain, app_id):
		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return
		
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		
		# get params
		user_email = self.request.get('user_email')

		# check if another updating is running
		memcache_key = 'script=tqupdateaccessibleinfo&google_apps_domain=' + google_apps_domain + '&app_id=' + app_id + '&user_email=' + user_email + '&g=2'
		is_processing = memcache.get(memcache_key)
		is_processing = is_processing if is_processing is not None else False
		if is_processing:
			logging.info('TqUpdateAccessibleInfo: same updating is running --> no need to update')
			return make_response('', 200)
		
		timeout_time = 60 * 10
		memcache.set(key=memcache_key, value=True, time=timeout_time)
		
		try:
			# start update
			logging.info('start_update user_email=' + str(user_email))
			google_apps_user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email, auto_create=True)
			user_accessible_info = sateraito_db.UserAccessibleInfo.getInstance(user_email, auto_create=True)

			# save start date
			user_accessible_info.accessible_cat_and_type_update_start_date = datetime.datetime.now()
			user_accessible_info.put()

			# logging.info('**1 current_memory_usage=' + str(google.appengine.api.runtime.memory_usage().current))

			my_joining_groups = google_apps_user_entry_dict['google_apps_groups']

			# accessible folder
			accessible_doc_folder_codes, accessible_doc_folder_nos = sateraito_db.DocFolder.getAccessibleDocFolderCodes(user_email, my_joining_groups)
			user_accessible_info.accessible_doc_folder_codes = accessible_doc_folder_codes
			user_accessible_info.accessible_doc_folder_nos = accessible_doc_folder_nos
			# logging.info('**2 current_memory_usage=' + str(google.appengine.api.runtime.memory_usage().current))
			# memcache.set(key=memcache_key, value=True, time=timeout_time)

			# creatable folder
			creatable_doc_folder_codes = sateraito_db.DocFolder.getCreatableDocFolderCodes(user_email, my_joining_groups)
			user_accessible_info.creatable_doc_folder_codes = creatable_doc_folder_codes
			# logging.info('**4 current_memory_usage=' + str(google.appengine.api.runtime.memory_usage().current))
			# memcache.set(key=memcache_key, value=True, time=timeout_time)

			# downloadable folder
			downloadable_doc_folder_codes = sateraito_db.DocFolder.getDownloadableDocFolderCodes(user_email, my_joining_groups)
			user_accessible_info.downloadable_doc_folder_codes = downloadable_doc_folder_codes
			# logging.info('**6 current_memory_usage=' + str(google.appengine.api.runtime.memory_usage().current))
			# memcache.set(key=memcache_key, value=True, time=timeout_time)

			# deletable folder
			deletable_doc_folder_codes = sateraito_db.DocFolder.getDeletableDocFolderCodes(user_email, my_joining_groups)
			user_accessible_info.deletable_doc_folder_codes = deletable_doc_folder_codes
			# logging.info('**7 current_memory_usage=' + str(google.appengine.api.runtime.memory_usage().current))
			# memcache.set(key=memcache_key, value=True, time=timeout_time)

			# subfolder creatable folder
			subfolder_creatable_doc_folder_codes = sateraito_db.DocFolder.getSubFolderCreatableDocFolderCodes(user_email, my_joining_groups)
			user_accessible_info.subfolder_creatable_doc_folder_codes = subfolder_creatable_doc_folder_codes
			# logging.info('**8 current_memory_usage=' + str(google.appengine.api.runtime.memory_usage().current))
			# memcache.set(key=memcache_key, value=True, time=timeout_time)

			user_accessible_info.accessible_cat_and_type_updated_date = datetime.datetime.now()
			user_accessible_info.need_update = False
			user_accessible_info.put()

# 		except AppsForYourDomainException as e:
# 			memcache.delete(memcache_key)
# 			logging.error('class name:' + e.__class__.__name__ + ' message=' +str(e))
# #			logging.info('AppsForYourDomainException:e=' + str(e))
		except Exception as e:
			logging.error('class name:' + e.__class__.__name__ + ' message=' +str(e))
			memcache.delete(memcache_key)
			raise e
		
		# delete flag
		memcache.delete(memcache_key)

		return make_response('', 200)


class _FulltextSearch(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" check if UserInfo data for fulltext search up-to-date
	"""
	
	def pushSearchedWords(self, searched_word):
		if searched_word is None:
			return
		if str(searched_word).strip() == '':
			return
		q = sateraito_db.SearchedWords.query()
		q = q.filter(sateraito_db.SearchedWords.user_id == self.viewer_user_id)
		row = q.get()
		if row is None:
			row = sateraito_db.SearchedWords()
			row.user_id = self.viewer_user_id
			row.searched_words = []
			row.put()
		if searched_word in row.searched_words:
			# no need to add, but move word to last of list
			logging.info('moving word ' + searched_word + ' to last')
			row.searched_words.remove(searched_word)
			row.searched_words.append(searched_word)
			row.put()
		else:
			# add new word
			row.searched_words.append(searched_word)
			if len(row.searched_words) > MAX_NUM_STORE_SEARCH_HISTORY:
				# remove oldest search history
				row.searched_words.pop(0)
			row.put()
	
	def process(self, google_apps_domain, app_id):
		# get params
		keyword_raw = self.request.get('keyword')
		page_raw = self.request.get('page', '1')
		page = int(page_raw)
		grouping_col_raw = self.request.get('grouping_col')
		grouping_col = None
		if str(grouping_col_raw).isdigit():
			grouping_col = int(grouping_col_raw)
		grouping_direction = self.request.get('grouping_direction')
		# set response header
		self.setResponseHeader('Content-Type', 'application/json')
		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(self.viewer_email, auto_create=True)
		# go fulltext search
		index = search.Index(name=sateraito_func.INDEX_SEARCH_WORKFLOW_DOC)
		
		adc_ok, all_doc_folder_nos = sateraito_func.getAllDocFolderNos(google_apps_domain, app_id)
		#
		# Build query string
		#
		# step1. keyword
		logging.info('raw keyword:' + str(keyword_raw))
		keyword = unicodedata.normalize('NFKC', keyword_raw)
		keyword_splited = keyword.split(' ')
		keyword2 = ''
		for k in keyword_splited:
			keyword2 += ' "' + k + '"'
		keyword2 = keyword2.strip()
		logging.info('normarized keyword:' + str(keyword2))
		query_string = ''
		if keyword2.strip('"') == '':
			pass
		else:
			query_string += keyword2 + ' '
		# step2.limit by user's accessible_doc_folder_nos
		if len(user_accessible_info_dict['accessible_doc_folder_nos']) > 0:
			prohibited_doc_folder_nos = list(set(all_doc_folder_nos) - set(user_accessible_info_dict['accessible_doc_folder_nos']))
			if adc_ok and len(prohibited_doc_folder_nos) < len(user_accessible_info_dict['accessible_doc_folder_nos']):
				if len(prohibited_doc_folder_nos) > 0:
					query_string += ' (NOT folder_no:('
					for folder_no in prohibited_doc_folder_nos:
						query_string += str(folder_no) + ' OR '
					# remove last ' OR '
					query_string = query_string[0:(len(query_string) - 4)]
					query_string += '))'
					# query_string += ' AND '
			else:
				query_string += ' (folder_no:('
				for folder_no in user_accessible_info_dict['accessible_doc_folder_nos']:
					query_string += str(folder_no) + ' OR '
				# remove last ' OR '
				query_string = query_string[0:(len(query_string) - 4)]
				query_string += '))'
				# query_string += ' AND '
		logging.info('query_string=' + query_string)
		
		# sort option
		expressions = []
		if grouping_col is None or grouping_col == 0:
			pass
		else:
			logging.info('sorting:grouping_col ' + str(grouping_col) + ' grouping_direction=' + str(grouping_direction))
			direction = search.SortExpression.DESCENDING
			if grouping_direction == 'asc':
				direction = search.SortExpression.ASCENDING
			expressions = [
						search.SortExpression(expression='gc' + str(grouping_col),
											default_value='',
											direction=direction)
						]
		sort_options = search.SortOptions(expressions=expressions, limit=sateraito_func.MAX_NUM_OF_SORTING_DOC)

		offset = ((page - 1) * sateraito_func.NUM_DOC_PER_PAGE)
		query_options = search.QueryOptions(
										sort_options=sort_options,
										limit=sateraito_func.NUM_DOC_PER_PAGE,
										offset=offset)
		# Go query (using page parameter)
		ret_results = []
		q = search.Query(query_string=query_string, options=query_options)
		results = index.search(q)
		logging.info('documents.number_found=' + str(results.number_found))
		
#		google_apps_user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, self.viewer_email)
		
		# build resultset to return 
		for document in results:
			file_id = document.doc_id
			# double-check check user priv by UserInfo
			doc_dict = sateraito_db.WorkflowDoc.getDict(file_id)
			if doc_dict is None:
				# doc not found by doc_id --> doc_id is wrong, should be deleted from Fulltext Index
				sateraito_func.removeDocFromIndex(file_id)
			else:
				is_accessible = sateraito_func.checkDocPrivByUserInfo(doc_dict, user_accessible_info_dict)
				# add this document to resultset if user priv for this document is ok
				if not is_accessible:
					logging.warn('got doc by query but actually not accessible:' + str(document.doc_id))
				else:
					folder_dict = sateraito_db.DocFolder.getDict(doc_dict['folder_code'])
					folder_name = folder_dict['folder_name']
					deletable_admin_only = folder_dict['deletable_admin_only']
					is_downloadable = sateraito_db.DocFolder.isDownloadableCategory(doc_dict['folder_code'], user_accessible_info_dict)
					is_deletable = sateraito_db.DocFolder.isDeletableCategory(doc_dict['folder_code'], user_accessible_info_dict)
					ret_results.append({
								'file_id': file_id,
								'file_name': doc_dict['file_name'],
								'file_size': doc_dict['file_size'],
								'file_description': sateraito_func.noneToZeroStr(doc_dict['file_description']),
								'attachment_type': doc_dict['attachment_type'],
								'attach_link': doc_dict['attach_link'],
								'author_name': doc_dict['author_name'],
								'author_email': doc_dict['author_email'],
								'folder_code': doc_dict['folder_code'],
								'folder_name': folder_name,
								'uploaded_date': str(sateraito_func.toShortLocalTime(doc_dict['uploaded_date'])),
								'is_downloadable': is_downloadable,
								'is_deletable': is_deletable,
								'deletable_admin_only': deletable_admin_only,
								})
		# check if have more rows
		q2 = search.Query(query_string=query_string, options=search.QueryOptions(limit=sateraito_func.NUM_DOC_PER_PAGE, offset=(offset + sateraito_func.NUM_DOC_PER_PAGE)))
		results_more = index.search(q2)
		have_more_rows = False
		if len(results_more.results) > 0:
			have_more_rows = True
		
		ret_obj = {
			'have_more_rows': have_more_rows,
			'results': ret_results
		}
		logging.info('returns entries=' + str(len(ret_results)))

		# add keyword to history
		self.pushSearchedWords(keyword_raw)

		return json.JSONEncoder().encode(ret_obj)

class FulltextSearch(_FulltextSearch):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkGadgetRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)

class FulltextSearchOid(_FulltextSearch):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)


class _GetSearchedWords(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def process(self, google_apps_domain, app_id):
		# set response header
		self.setResponseHeader('Content-Type', 'application/json')
		
		# seek searched words
		q = sateraito_db.SearchedWords.query()
		q = q.filter(sateraito_db.SearchedWords.user_id == self.viewer_user_id)
		row = q.get()
		if row is None:
			result = []
			jsondata = json.JSONEncoder().encode(result)
			self.response.out.write(jsondata)
			return
		if '' in row.searched_words:
			row.searched_words.remove('')
			row.put()
			logging.info('removed zero string word')
		
		return json.JSONEncoder().encode(row.searched_words)

class GetSearchedWords(_GetSearchedWords):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkGadgetRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)

class GetSearchedWordsOid(_GetSearchedWords):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)


def getChildCategoryCodes(folder_code):
	q = sateraito_db.DocFolder.query()
	q = q.filter(sateraito_db.DocFolder.parent_folder_code == folder_code)
	ret_folder_codes = []
	ret_folder_nos = []
	for row in q:
		ret_folder_codes.append(row.folder_code)
		ret_folder_nos.append(row.folder_no)
		child_folder_codes, child_folder_nos = getChildCategoryCodes(row.folder_code)
		ret_folder_codes += child_folder_codes
		ret_folder_nos += child_folder_nos
	return ret_folder_codes, ret_folder_nos


class TqCheckAccessibleInfo(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" check if UserInfo data for fulltext search up-to-date
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		
		# get param
		user_email = self.request.get('user_email')

		# compate date in UserAccessibleInfo
		user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(user_email, auto_create=True)

		# check if UPDATING is needed
		google_apps_user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email)
		if google_apps_user_entry_dict is not None:
			is_group_updated = sateraito_func.checkGroupUpdated(google_apps_domain, app_id, user_email)
			is_ready = sateraito_func.isFulltextReady(user_accessible_info_dict, google_apps_user_entry_dict)
			if (not is_ready) or is_group_updated:
				logging.info('need update, adding task to background')
				queue = taskqueue.Queue('update-accessible-info')
				task = taskqueue.Task(
					url='/' + google_apps_domain + '/' + app_id + '/textsearch/tq/updateaccessibleinfo',
					params={
						'user_email': user_email
						},
					target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
					countdown=0
				)
				queue.add(task)

		return make_response('', 200)


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/tq/updateaccessibleinfo',
									 view_func=TqUpdateAccessibleInfo.as_view('TextSearchTqUpdateAccessibleInfo'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/tq/buildsearchindexforalldocs',
									 view_func=TqBuildSearchIndexForAllDocs.as_view('TextSearchTqBuildSearchIndexForAllDocs'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/tq/checkaccessibleinfo',
									 view_func=TqCheckAccessibleInfo.as_view('TextSearchTqCheckAccessibleInfo'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/checkfulltextready',
									 view_func=CheckFulltextReady.as_view('TextSearchCheckFulltextReady'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/oid/checkfulltextready',
									 view_func=CheckFulltextReadyOid.as_view('TextSearchCheckFulltextReadyOid'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/fulltextsearch',
									 view_func=FulltextSearch.as_view('TextSearchFulltextSearch'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/oid/fulltextsearch',
									 view_func=FulltextSearchOid.as_view('TextSearchFulltextSearchOid'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/getsearchedwords',
									 view_func=GetSearchedWords.as_view('TextSearchGetSearchedWords'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/textsearch/oid/getsearchedwords',
									 view_func=GetSearchedWordsOid.as_view('TextSearchGetSearchedWordsOid'))
