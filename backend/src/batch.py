#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'

from flask import Flask, Response, render_template, request, make_response
from sateraito_logger import logging
import datetime
from ucf.utils.ucfutil import UcfUtil

from google.appengine.api import namespace_manager
from google.appengine.api import taskqueue
from google.appengine.ext.db.metadata import Namespace
# from webapp2_extras.appengine.sessions_ndb import Session
import google.appengine.api.runtime

import sateraito_inc
import sateraito_page
import sateraito_func
import sateraito_db

'''
batch.py

@since: 2013-08-01
@version: 2013-09-15
@author: Akitoshi Abe
'''


# prepare for max 500,000 namespaces
NUM_PER_PAGE_NAMESPACE = 500
MAX_PAGES_NAMESPACE = 1000

# prepare for max 1,000,000 docs
NUM_PER_PAGE_DOCS = 200
MAX_PAGES_DOCS = 5000


class StartUpdateNumPublishedDocs(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('start update published doc counter')

		# kick start
		que = taskqueue.Queue('default')
		task = taskqueue.Task(
				url='/batch/tq/updatetotalfilesize',
				target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
				countdown=1
		)
		que.add(task)

		return make_response('', 200)

class TqUpdateTotalFileSize(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return
		
		# step1. update num FileSizeCounterShared
		
		# seek all namespace
		logging.info('** step 1')
		q_ns = Namespace.all()
		for i in range(MAX_PAGES_NAMESPACE):
			rows = q_ns.fetch(limit=NUM_PER_PAGE_NAMESPACE, offset=(i * NUM_PER_PAGE_NAMESPACE))
			if len(rows) == 0:
				break
			for row_ns in rows:
				namespace_name = row_ns.namespace_name

				if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE:
					google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

					logging.info('processing namespace=%s' % namespace_name)
					if not sateraito_func.checkTimeLastLogin(google_apps_domain):
						logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
						continue

					if sateraito_func.isDomainDisabled(google_apps_domain):
						# skip this domain
						logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
						continue

					namespace_manager.set_namespace(namespace_name)
					
					q = sateraito_db.FileflowDoc.query()
					q = q.filter(sateraito_db.FileflowDoc.del_flag == False)
					total_size = 0
					for key in q.iter(keys_only=True):
						row = sateraito_db.FileflowDoc.getDict(key.id())
						total_size += row['file_size']
					
					sateraito_db.FileSizeCounterShared.resetCounter(total_size)
					logging.info('updating finished: google_apps_domain=' + str(google_apps_domain) + ' app_id=' + str(app_id) + ' total_size=' + str(total_size))
					sateraito_func.updateFreeSpaceStatus(google_apps_domain)
					sateraito_func.loggingRuntimeStatus()
		
		# step2. update GoogleAppsDomainEntry.total_file_size
		logging.info('** step 2')
		q_ns = Namespace.all()
		for i in range(MAX_PAGES_NAMESPACE):
			rows = q_ns.fetch(limit=NUM_PER_PAGE_NAMESPACE, offset=(i * NUM_PER_PAGE_NAMESPACE))
			if len(rows) == 0:
				break
			for row_ns in rows:
				namespace_name = row_ns.namespace_name

				if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE:
					google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

					logging.info('processing namespace=%s' % namespace_name)
					if not sateraito_func.checkTimeLastLogin(google_apps_domain):
						logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
						continue

					if sateraito_func.isDomainDisabled(google_apps_domain):
						# skip this domain
						logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
						continue

					namespace_manager.set_namespace(namespace_name)
					
					if app_id == sateraito_func.DEFAULT_APP_ID:
						total_file_size = sateraito_db.FileSizeCounterShared.get_total()
						row = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
						if row is not None:
							logging.info('saving total_file_size=' + str(total_file_size))
							row.total_file_size = total_file_size
							row.put()

		return make_response('', 200)


class StartUpdateAccessibleInfo(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('start update accessible info')
		sateraito_db.BatchTimeLog.registerTime('REBUILD_ACCESSIBLE_INFO_START')
		# kick start
		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': ''
		}
		task = taskqueue.Task(
			url='/batch/tq/updateaccessibleinfo',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			countdown=1
		)
		que.add(task)

		return make_response('', 200)

class TqUpdateAccessibleInfo(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return
		
		# get param
		namespace_name_bigger_than = self.request.get('namespace_name_bigger_than')
		if namespace_name_bigger_than is None:
			namespace_name_bigger_than = ''

		logging.info('get_namespace_name_bigger_than=' + str(namespace_name_bigger_than))
		row_ns = None
		# seek all namespace
		q_ns = Namespace.all()
		if namespace_name_bigger_than:
			q_ns.filter('__key__ >', Namespace.key_for_namespace(namespace_name_bigger_than))
		q_ns.order('__key__')
		rows = q_ns.fetch(2)
		for row in rows:
			if row.namespace_name != '':
				row_ns = row
				break
		if row_ns is None:
			logging.info('FINISHED REBUILDING ACCESSIBLE INFO')
			sateraito_db.BatchTimeLog.registerTime('REBUILD_ACCESSIBLE_INFO_FINISH')
			return make_response('', 200)

		namespace_name = row_ns.namespace_name
		google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

		logging.info('processing namespace_name=%s' % namespace_name)
		ok_to_start_rebuild = True
		if not sateraito_func.checkTimeLastLogin(google_apps_domain):
			logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
			ok_to_start_rebuild = False

		if sateraito_func.isDomainDisabled(google_apps_domain):
			# skip this domain
			logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
			ok_to_start_rebuild = False

		if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE and ok_to_start_rebuild:
			try:
				namespace_manager.set_namespace(namespace_name)
				self.updateAccessibleInfo(namespace_name)
			except Exception as ex:
				logging.info(str(ex))

		if namespace_name:
			que = taskqueue.Queue('default')
			params = {
				'namespace_name_bigger_than': namespace_name
			}
			task = taskqueue.Task(
				url='/batch/tq/updateaccessibleinfo',
				params=params,
				target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
				countdown=10
			)
			que.add(task)

		return make_response('', 200)
	
	def updateAccessibleInfo(self, namespace_name):
		logging.info('updateAccessibleInfo namespace_name=' + str(namespace_name))
		google_apps_domain = self.getGoogleAppsDomainFromNamespace(namespace_name)
		app_id = self.getAppIdFromNamespace(namespace_name)
		
		all_user_info_emails = sateraito_db.UserInfo.getAllEmails()
		for user_email in all_user_info_emails:
			logging.info('checking user_email=' + str(user_email))
			google_apps_user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, user_email)
			user_accessible_info_dict = sateraito_db.UserAccessibleInfo.getDict(user_email, auto_create=True)
			if google_apps_user_entry_dict is None:
				continue
			is_ready = sateraito_func.isFulltextReady(user_accessible_info_dict, google_apps_user_entry_dict)
			if not is_ready:
				logging.info('need update, adding task=' + str(user_email))
				# immediate update accessible info
				queue = taskqueue.Queue('update-accessible-info')
				task = taskqueue.Task(
					url='/' + google_apps_domain + '/' + app_id + '/textsearch/tq/updateaccessibleinfo',
					params={
						'user_email': user_email
						},
					countdown=1,
					target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
				)
				queue.add(task)
			else:
				logging.info('not need update, adding task=' + str(user_email))

class StartUpdateDomainAndAppIdList(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('start update domain and app_id list')
		# kick start
		que = taskqueue.Queue('default')
		task = taskqueue.Task(
				url='/batch/tq/updatedomainandappidlist',
				target=sateraito_func.getBackEndsModuleNameDeveloper('b1process'),
				countdown=1
		)
		que.add(task)

		return make_response('', 200)

class TqUpdateDomainAndAppIdList(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return
		
		# seek all namespace
		q_ns = Namespace.all()
		for i in range(MAX_PAGES_NAMESPACE):
			rows = q_ns.fetch(limit=NUM_PER_PAGE_NAMESPACE, offset=(i * NUM_PER_PAGE_NAMESPACE))
			if len(rows) == 0:
				break
			for row_ns in rows:
				namespace_name = row_ns.namespace_name

				if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE:
					google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

					logging.info('processing namespace=%s' % namespace_name)
					if not sateraito_func.checkTimeLastLogin(google_apps_domain):
						logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
						continue

					if sateraito_func.isDomainDisabled(google_apps_domain):
						# skip this domain
						logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
						continue

					namespace_manager.set_namespace(namespace_name)

					is_exists = sateraito_db.DomainAndAppId.isExists(google_apps_domain, app_id)
					if not is_exists:
						logging.info('adding DomainAndAppId entry google_apps_domain=' + str(google_apps_domain) + ' app_id=' + str(app_id))
						created_date = datetime.datetime.now()
						row_o = sateraito_db.OtherSetting.getInstance()
						if row_o is not None:
							created_date = row_o.created_date
						sateraito_db.DomainAndAppId.addIfNotRegistered(google_apps_domain, app_id, created_date=created_date)

		return make_response('', 200)


class StartRebuildAllIndex(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('start rebuild all fulltext search index')
		sateraito_db.BatchTimeLog.registerTime('REBUILD_ALL_SEARCH_INDEX_START')
		# kick start
		que = taskqueue.Queue('default')
		params = {
				'namespace_name_bigger_than': ''
				}
		task = taskqueue.Task(
				url='/batch/tq/rebuildallindex',
				params=params,
				target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
				countdown=1
		)
		que.add(task)

		return make_response('', 200)

class TqRebuildAllIndex(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def _rebuildAllSearchIndex(self, namespace_name, doc):
		
		logging.info('processing doc_id=' + doc.workflow_doc_id)
		logging.info('REBUILDING...')
		sateraito_func.removeDocFromIndex(doc.workflow_doc_id)
		sateraito_func.addDocToTextSearchIndex(doc)

		# don't remove in text search -> because of admin search type
		# if not doc.del_flag:
		# 	logging.info('REBUILDING...')
		# 	sateraito_func.removeDocFromIndex(doc.workflow_doc_id)
		# 	sateraito_func.addDocToTextSearchIndex(doc)
		# else:
		# 	# deleted doc
		# 	sateraito_func.removeDocFromIndex(doc.workflow_doc_id)
		# 	logging.info('REMOVING...')
	
	def rebuildAllSearchIndex(self, namespace_name):
		
		q = sateraito_db.WorkflowDoc.query()
		# max 250,000 docs
		NUM_PER_PAGE = 500
		MAX_PAGES = 500
		for page in range(MAX_PAGES):
			rows = q.fetch(limit=NUM_PER_PAGE, offset=(page * NUM_PER_PAGE))
			logging.info('page ' + str(page))
			if len(rows) == 0:
				break
			for doc in rows:
				self._rebuildAllSearchIndex(namespace_name, doc)
				is_shutting_down = google.appengine.api.runtime.is_shutting_down()
				current_memory_usage = google.appengine.api.runtime.memory_usage().current
				logging.info('is_shutting_down=' + str(is_shutting_down) + ' current_memory_usage=' + str(current_memory_usage))

	def doAction(self):
		
		namespace_name_bigger_than = self.request.get('namespace_name_bigger_than')
		if namespace_name_bigger_than is None:
			namespace_name_bigger_than = ''
		# seek all namespace
		row_ns = None
		q_ns = Namespace.all()
		q_ns.order('__key__')
		if namespace_name_bigger_than != '' and namespace_name_bigger_than is not None:
			q_ns.filter('__key__ >', Namespace.key_for_namespace(namespace_name_bigger_than))
			row_ns = q_ns.get()
			if row_ns is None:
				logging.info('NO NAMESPACE bigger than ' + namespace_name_bigger_than)
				logging.info('FINISHED REBUILDING SEARCH INDEX')
				sateraito_db.BatchTimeLog.registerTime('REBUILD_ALL_SEARCH_INDEX_FINISH')

				return make_response('', 200)
		else:
			rows = q_ns.fetch(2)
			for row in rows:
				if row.namespace_name != '':
					row_ns = row
					break
		namespace_name = row_ns.namespace_name
		google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

		logging.info('processing namespace_name=%s' % namespace_name)
		ok_to_start_rebuild = True
		if not sateraito_func.checkTimeLastLogin(google_apps_domain):
			logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
			ok_to_start_rebuild = False

		if sateraito_func.isDomainDisabled(google_apps_domain):
			# skip this domain
			logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
			ok_to_start_rebuild = False

		if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE and ok_to_start_rebuild:
			try:
				namespace_manager.set_namespace(namespace_name)
				self.rebuildAllSearchIndex(namespace_name)
			except Exception as ex:
				logging.info(str(ex))
		
		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': namespace_name
		}
		task = taskqueue.Task(
			url='/batch/tq/rebuildallindex',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			countdown=10
		)
		que.add(task)

		return make_response('', 200)


class StartDeleteOldSession(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		que = taskqueue.Queue('default')
		task = taskqueue.Task(
			url='/batch/tq/deleteoldsession',
			target=sateraito_func.getBackEndsModuleNameDeveloper('default'),  # frontend
			countdown=1,
		)
		que.add(task)

		return make_response('', 200)

# class TqDeleteOldSession(sateraito_page._BasePage):
#
# 	def post(self):
# 		# check retry count
# 		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
# 		logging.info('retry_cnt=' + str(retry_cnt))
# 		if retry_cnt is not None:
# 			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
# 				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
# 				return
#
# 		# list up
# 		q = Session.query()
# 		q = q.order(Session.updated)
# 		keys = q.fetch(limit=500, keys_only=True)
# 		del_cnt = 0
# 		for key in keys:
# 			row = key.get()
# 			if row is not None:
# 				# delete 10 days older session data
# 				if row.updated < datetime.datetime.now() - datetime.timedelta(days=sateraito_page.MAX_OPENID_SESSION_AGE_DAYS):
# 					logging.info('deleting session ' + str(row.key.id()) + ' updated=' + str(row.updated))
# 					row.key.delete()
# 					del_cnt += 1
# 				else:
# 					# no old session data
# 					logging.info('not found more data to delete')
# 					break
# 		logging.info('** deleted ' + str(del_cnt) + ' session data')


# class StartUpdateNoticeUsesDoc(sateraito_page._BasePage):
#
# 	def get(self):
# 		logging.info('StartUpdateNoticeUsesDoc')
# 		# kick start
# 		que = taskqueue.Queue('default')
# 		params = {
# 			'namespace_name_bigger_than': ''
# 		}
# 		task = taskqueue.Task(
# 			url='/batch/tq/updatenoticeusesdoc',
# 			params=params,
# 			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
# 		)
# 		que.add(task)
#
# class TqUpdateNoticeUsesDoc(sateraito_page._BasePage):
#
# 	def post(self):
# 		namespace_name_bigger_than = self.request.get('namespace_name_bigger_than')
# 		if namespace_name_bigger_than is None:
# 			namespace_name_bigger_than = ''
# 		# seek all namespace
# 		row_ns = None
# 		q_ns = Namespace.all()
# 		q_ns.order('__key__')
# 		if namespace_name_bigger_than != '' and namespace_name_bigger_than is not None:
# 			q_ns.filter('__key__ >', Namespace.key_for_namespace(namespace_name_bigger_than))
# 			row_ns = q_ns.get()
# 			if row_ns is None:
# 				logging.info('NO NAMESPACE bigger than ' + namespace_name_bigger_than)
# 				logging.info('FINISHED REBUILDING SEARCH INDEX')
# 				sateraito_db.BatchTimeLog.registerTime('REBUILD_ALL_SEARCH_INDEX_FINISH')
# 				return
# 		else:
# 			rows = q_ns.fetch(2)
# 			for row in rows:
# 				if row.namespace_name != '':
# 					row_ns = row
# 					break
# 		namespace_name = row_ns.namespace_name
# 		google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)
#
# 		logging.info('processing namespace_name=%s' % namespace_name)
# 		ok_to_start_rebuild = True
# 		if not sateraito_func.checkTimeLastLogin(google_apps_domain):
# 			logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
# 			ok_to_start_rebuild = False
#
# 		if sateraito_func.isDomainDisabled(google_apps_domain):
# 			# skip this domain
# 			logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
# 			ok_to_start_rebuild = False
#
# 		if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE and ok_to_start_rebuild:
# 			try:
# 				namespace_manager.set_namespace(namespace_name)
# 				self.updateNoticeDoc(namespace_name)
# 			except Exception as ex:
# 				logging.info(str(ex))
#
# 		que = taskqueue.Queue('default')
# 		params = {
# 			'namespace_name_bigger_than': namespace_name
# 		}
# 		task = taskqueue.Task(
# 			url='/batch/tq/updatenoticeusesdoc',
# 			params=params,
# 			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
# 			countdown=3  # for test
# 		)
# 		que.add(task)
#
# 	def updateNoticeDoc(self, namespace_name):
# 		logging.info('START: updateNoticeDoc namespace_name=' + str(namespace_name))
# 		total = 0
# 		q = sateraito_db.WorkflowDoc.query()
# 		for row in q:
# 			row.notice_users = row.accessible_users
# 			row.put()
# 			total += 1
#
# 		logging.info('COMPLETE: updateNoticeDoc ' + str(total) + ' doc namespace_name=' + str(namespace_name))


class StartUpdateClient(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('start update doc and client')
		# kick start
		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': ''
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdateclient',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
		)
		que.add(task)

		return make_response('', 200)

class TqStartUpdateClient(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def updateClient(self):
		# update document code for client
		q_client = sateraito_db.ClientInfo.query()
		for row_client in q_client:

			q_doc = sateraito_db.WorkflowDoc.query()
			q_doc = q_doc.filter(sateraito_db.WorkflowDoc.client_id == row_client.client_id)
			row_doc = q_doc.get()

			if not row_doc:
				# pass if not workflow doc use
				logging.warn(row_client)
				logging.warn('workflow doc not use')
				continue

			row_client.document_code = row_doc.document_code
			row_client.put()

	def doAction(self):

		namespace_name_bigger_than = self.request.get('namespace_name_bigger_than')
		if namespace_name_bigger_than is None:
			namespace_name_bigger_than = ''
		# seek all namespace
		row_ns = None
		q_ns = Namespace.all()
		if namespace_name_bigger_than != '' and namespace_name_bigger_than is not None:
			q_ns.filter('__key__ >', Namespace.key_for_namespace(namespace_name_bigger_than))
			row_ns = q_ns.get()
			if row_ns is None:
				logging.info('NO NAMESPACE bigger than ' + namespace_name_bigger_than)
				logging.info('FINISHED REBUILDING SEARCH INDEX')
				sateraito_db.BatchTimeLog.registerTime('REBUILD_ALL_SEARCH_INDEX_FINISH')

				return make_response('', 200)
		else:
			rows = q_ns.fetch(2)
			for row in rows:
				if row.namespace_name != '':
					row_ns = row
					break
		namespace_name = row_ns.namespace_name
		google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

		logging.info('processing namespace_name=%s' % namespace_name)
		ok_to_start_rebuild = True
		if not sateraito_func.checkTimeLastLogin(google_apps_domain):
			logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
			ok_to_start_rebuild = False

		if sateraito_func.isDomainDisabled(google_apps_domain):
			# skip this domain
			logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
			ok_to_start_rebuild = False

		if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE and ok_to_start_rebuild:
			try:

				namespace_manager.set_namespace(namespace_name)
				self.updateClient()

			except Exception as ex:
				logging.info(str(ex))

		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': namespace_name
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdateclient',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			countdown=10
		)
		que.add(task)

		return make_response('', 200)


class StartUpdateWorkflowDoc(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('start update doc')
		# kick start
		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': ''
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdateworkflowdoc',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			countdown=1
		)
		que.add(task)

class TqStartUpdateWorkflowDoc(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def updateWorkflowDoc(self, google_apps_domain, app_id):

		q_doc = sateraito_db.WorkflowDoc.query()
		for key in q_doc.iter(keys_only=True):
			row_doc = key.get()

			row_doc.author_name = sateraito_func.getUserName(google_apps_domain, row_doc.author_email)
			row_doc.updated_author_name = sateraito_func.getUserName(google_apps_domain, row_doc.updated_author_email)
			row_doc.put()

	def doAction(self):

		namespace_name_bigger_than = self.request.get('namespace_name_bigger_than')
		if namespace_name_bigger_than is None:
			namespace_name_bigger_than = ''
		# seek all namespace
		row_ns = None
		q_ns = Namespace.all()
		q_ns.order('__key__')
		if namespace_name_bigger_than != '' and namespace_name_bigger_than is not None:
			q_ns.filter('__key__ >', Namespace.key_for_namespace(namespace_name_bigger_than))
			row_ns = q_ns.get()
			if row_ns is None:
				logging.info('NO NAMESPACE bigger than ' + namespace_name_bigger_than)
				logging.info('FINISHED REBUILDING SEARCH INDEX')
				sateraito_db.BatchTimeLog.registerTime('REBUILD_ALL_SEARCH_INDEX_FINISH')

				return make_response('', 200)
		else:
			rows = q_ns.fetch(2)
			for row in rows:
				if row.namespace_name != '':
					row_ns = row
					break
		namespace_name = row_ns.namespace_name
		google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

		logging.info('processing namespace_name=%s' % namespace_name)
		ok_to_start_rebuild = True
		if not sateraito_func.checkTimeLastLogin(google_apps_domain):
			logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
			ok_to_start_rebuild = False

		if sateraito_func.isDomainDisabled(google_apps_domain):
			# skip this domain
			logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
			ok_to_start_rebuild = False

		if not sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain, domain_dict=None):
			# skip this domain
			logging.info('skip domain ' + str(google_apps_domain) + ' is not SSO Gadget Tenant')
			ok_to_start_rebuild = False

		if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE and ok_to_start_rebuild:
			try:

				namespace_manager.set_namespace(namespace_name)
				self.updateWorkflowDoc(google_apps_domain, app_id)

			except Exception as ex:
				logging.info(str(ex))

		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': namespace_name
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdateworkflowdoc',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			countdown=3
		)
		que.add(task)

		return make_response('', 200)


class StartUpdateCsvImportLog(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('StartUpdateCsvImportLog')
		# kick start
		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': ''
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdatecsvimportlog',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
		)
		que.add(task)

		return make_response('', 200)

class TqStartUpdateCsvImportLog(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def updateCsvImportLog(self):
		q = sateraito_db.CsvImportLog.query()
		for key in q.iter(keys_only=True):
			row = key.get()

			row.import_kind = 'user_import'
			row.put()

	def doAction(self):

		namespace_name_bigger_than = self.request.get('namespace_name_bigger_than')
		if namespace_name_bigger_than is None:
			namespace_name_bigger_than = ''
		# seek all namespace
		row_ns = None
		q_ns = Namespace.all()
		q_ns.order('__key__')
		if namespace_name_bigger_than != '' and namespace_name_bigger_than is not None:
			q_ns.filter('__key__ >', Namespace.key_for_namespace(namespace_name_bigger_than))
			row_ns = q_ns.get()
			if row_ns is None:
				logging.info('NO NAMESPACE bigger than ' + namespace_name_bigger_than)
				logging.info('FINISHED REBUILDING SEARCH INDEX')
				sateraito_db.BatchTimeLog.registerTime('REBUILD_ALL_SEARCH_INDEX_FINISH')

				return make_response('', 200)
		else:
			rows = q_ns.fetch(2)
			for row in rows:
				if row.namespace_name != '':
					row_ns = row
					break
		namespace_name = row_ns.namespace_name
		google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

		logging.info('processing namespace_name=%s' % namespace_name)
		ok_to_start_rebuild = True
		if not sateraito_func.checkTimeLastLogin(google_apps_domain):
			logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
			ok_to_start_rebuild = False

		if sateraito_func.isDomainDisabled(google_apps_domain):
			# skip this domain
			logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
			ok_to_start_rebuild = False

		if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE and ok_to_start_rebuild:
			try:

				namespace_manager.set_namespace(namespace_name)
				self.updateCsvImportLog()

			except Exception as ex:
				logging.info(str(ex))

		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': namespace_name
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdatecsvimportlog',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			countdown=10
		)
		que.add(task)

		return make_response('', 200)


class StartUpdateCategories(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):
		logging.info('start update Categories')
		# kick start
		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': ''
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdatecategories',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
		)
		que.add(task)

		return make_response('', 200)

class TqStartUpdateCategories(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def updateCategories(self):
		# update Categories
		q = sateraito_db.Categories.query()
		q = q.filter(sateraito_db.Categories.is_tag == False)
		# q = q.filter(sateraito_db.Categories.del_flag == False)
		q = q.order(-sateraito_db.Categories.updated_date)

		for index, row_category in enumerate(q):
			row_category.sort_order = index + 1
			row_category.put()

	def doAction(self):

		namespace_name_bigger_than = self.request.get('namespace_name_bigger_than')
		if namespace_name_bigger_than is None:
			namespace_name_bigger_than = ''
		# seek all namespace
		row_ns = None
		q_ns = Namespace.all()
		if namespace_name_bigger_than != '' and namespace_name_bigger_than is not None:
			q_ns.filter('__key__ >', Namespace.key_for_namespace(namespace_name_bigger_than))
			row_ns = q_ns.get()
			if row_ns is None:
				logging.info('NO NAMESPACE bigger than ' + namespace_name_bigger_than)
				logging.info('FINISHED REBUILDING SEARCH INDEX')
				sateraito_db.BatchTimeLog.registerTime('REBUILD_ALL_SEARCH_INDEX_FINISH')

				return make_response('', 200)
		else:
			rows = q_ns.fetch(2)
			for row in rows:
				if row.namespace_name != '':
					row_ns = row
					break
		namespace_name = row_ns.namespace_name
		google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)

		logging.info('processing namespace_name=%s' % namespace_name)
		ok_to_start_rebuild = True
		if not sateraito_func.checkTimeLastLogin(google_apps_domain):
			logging.debug('google_apps_domain: ' + str(google_apps_domain) + ' not login in more than 3 months')
			ok_to_start_rebuild = False

		if sateraito_func.isDomainDisabled(google_apps_domain):
			# skip this domain
			logging.info('skip domain ' + str(google_apps_domain) + ' is disabled')
			ok_to_start_rebuild = False

		if namespace_name != '' and namespace_name != sateraito_db.DOWNLOAD_CSV_NAMESPACE and ok_to_start_rebuild:
			try:

				namespace_manager.set_namespace(namespace_name)
				self.updateCategories()

			except Exception as ex:
				logging.info(str(ex))

		que = taskqueue.Queue('default')
		params = {
			'namespace_name_bigger_than': namespace_name
		}
		task = taskqueue.Task(
			url='/batch/tq/startupdatecategories',
			params=params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			# countdown=10
		)
		que.add(task)

		return make_response('', 200)


class StartSetCancelDateToAllGWSNonFree(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def doAction(self):

		logging.info('start set cancel date to all GWS non free tenants')

		# kick start
		que = taskqueue.Queue('default')
		task = taskqueue.Task(
							url='/batch/tq/setcanceldatetoallgwsnonfreetenants',
							target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
							countdown=1
							)
		que.add(task)

		# set response header
		# self.response.out.write('Finished')
		return 'Start setting cancel date to all GWS non free tenants'


class TqStartSetCancelDateToAllGWSNonFree(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	# 全GWS有償版テナントに過去日の解約日をセット
	def _set_cancel_date_to_all_gws_nonfree_tenants(self):
		logging.info('_set_cancel_date_to_all_gws_nonfree_tenants...')

		q = Namespace.all()
		namespace_list = []
		for row in q:
			if row.namespace_name != '':
				namespace_list.append(row.namespace_name)

		for namespace_name in namespace_list:
			tenant_or_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)
			if app_id == '' or app_id == sateraito_func.DEFAULT_APP_ID:
				sateraito_func.setNamespace(tenant_or_domain, app_id)

				q = sateraito_db.GoogleAppsDomainEntry.query()
				q = q.filter(sateraito_db.GoogleAppsDomainEntry.google_apps_domain == tenant_or_domain.lower())
				rows = q.fetch()
				for entry in rows:
					# GWS版のみ処理（LINE WORKS版などを除外、すでに日付がセットされているレコードも除外）
					if entry is not None and (entry.oem_company_code is None or entry.oem_company_code == '' or entry.oem_company_code == 'sateraito') and (entry.sp_code is None or entry.sp_code == '' or entry.sp_code == 'apps') and (entry.cancel_date is None or entry.cancel_date == ''):
						# 一律過去日でも良いのだが一応作成日から３０日をセット
						dt_expire = UcfUtil.add_days(entry.created_date, 30)		# 当日を入れて31日（厳密でなくてもよいとは思うが...）
						entry.available_start_date = entry.created_date.strftime('%Y/%m/%d')
						entry.charge_start_date = dt_expire.strftime('%Y/%m/%d')
						entry.cancel_date = dt_expire.strftime('%Y/%m/%d')
						entry.put()
						logging.info('domain=%s cancel_date=%s' % (entry.google_apps_domain, entry.cancel_date))

		logging.info('fin.')
	
	def doAction(self):

		logging.info('tq start set cancel date to all GWS non free tenants')

		# 全GWS有償版テナントに過去日の解約日をセット
		self._set_cancel_date_to_all_gws_nonfree_tenants()

		# set response header
		# self.response.out.write('Finished')
		return 'Finished'


def add_url_rules(app):
	app.add_url_rule('/batch/cron/startupdatetotalfilesize', view_func=StartUpdateNumPublishedDocs.as_view('BatchCronStartUpdateNumPublishedDocs'))
	app.add_url_rule('/batch/tq/updatetotalfilesize', view_func=TqUpdateTotalFileSize.as_view('BatchCronTqUpdateTotalFileSize'))

	app.add_url_rule('/batch/cron/startupdateaccessibleinfo', view_func=StartUpdateAccessibleInfo.as_view('BatchCronStartUpdateAccessibleInfo'))
	app.add_url_rule('/batch/tq/updateaccessibleinfo', view_func=TqUpdateAccessibleInfo.as_view('BatchCronTqUpdateAccessibleInfo'))

	app.add_url_rule('/batch/cron/startupdatedomainandappidlist', view_func=StartUpdateDomainAndAppIdList.as_view('BatchCronStartUpdateDomainAndAppIdList'))
	app.add_url_rule('/batch/tq/updatedomainandappidlist', view_func=TqUpdateDomainAndAppIdList.as_view('BatchCronTqUpdateDomainAndAppIdList'))

	app.add_url_rule('/batch/cron/startrebuildallindex', view_func=StartRebuildAllIndex.as_view('BatchCronStartRebuildAllIndex'))
	app.add_url_rule('/batch/tq/rebuildallindex', view_func=TqRebuildAllIndex.as_view('BatchCronTqRebuildAllIndex'))

	app.add_url_rule('/batch/cron/startdeleteoldsession', view_func=StartDeleteOldSession.as_view('BatchCronStartDeleteOldSession'))
	# app.add_url_rule('/batch/tq/deleteoldsession', view_func=TqDeleteOldSession.as_view('TqDeleteOldSession'))

	app.add_url_rule('/batch/cron/startupdateclient', view_func=StartUpdateClient.as_view('BatchCronStartUpdateClient'))
	app.add_url_rule('/batch/tq/startupdateclient', view_func=TqStartUpdateClient.as_view('BatchCronTqStartUpdateClient'))

	app.add_url_rule('/batch/cron/startupdateworkflowdoc', view_func=StartUpdateWorkflowDoc.as_view('StartUpdateWorkflowDoc'))
	app.add_url_rule('/batch/tq/startupdateworkflowdoc', view_func=TqStartUpdateWorkflowDoc.as_view('BatchCronTqStartUpdateWorkflowDoc'))

	app.add_url_rule('/batch/cron/startupdatecsvimportlog', view_func=StartUpdateCsvImportLog.as_view('BatchCronStartUpdateCsvImportLog'))
	app.add_url_rule('/batch/tq/startupdatecsvimportlog', view_func=TqStartUpdateCsvImportLog.as_view('BatchCronTqStartUpdateCsvImportLog'))

	app.add_url_rule('/batch/cron/startupdatecategories', view_func=StartUpdateCategories.as_view('BatchCronStartUpdateCategories'))
	app.add_url_rule('/batch/tq/startupdatecategories', view_func=TqStartUpdateCategories.as_view('BatchCronTqStartUpdateCategories'))

	# app.add_url_rule('/batch/cron/startupdatenoticeusesdoc', view_func=StartUpdateNoticeUsesDoc.as_view('StartUpdateNoticeUsesDoc'))
	# app.add_url_rule('/batch/tq/updatenoticeusesdoc', view_func=TqUpdateNoticeUsesDoc.as_view('TqUpdateNoticeUsesDoc'))

	app.add_url_rule('/batch/cron/setcanceldatetoallgwsnonfreetenants', view_func=StartSetCancelDateToAllGWSNonFree.as_view('StartSetCancelDateToAllGWSNonFree'))
	app.add_url_rule('/batch/tq/setcanceldatetoallgwsnonfreetenants', view_func=TqStartSetCancelDateToAllGWSNonFree.as_view('TqStartSetCancelDateToAllGWSNonFree'))
