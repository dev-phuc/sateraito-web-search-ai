#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

# set default encodeing to utf-8
# set default encodeing to utf-8
from flask import render_template, request, make_response, redirect
# import time
import json
import datetime
from sateraito_logger import logging
import random

from google.appengine.api import memcache, taskqueue, namespace_manager, datastore_errors, urlfetch
from google.appengine.ext import ndb
# from google.appengine.ext.ndb.google_imports import datastore_errors
# from google.appengine.api import namespace_manager
# import gdata.apps.groups
# from gdata.service import RequestError
# from google.appengine.api.urlfetch import DownloadError
# from gdata.apps.service import AppsForYourDomainException
from apiclient.errors import HttpError

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page


'''
group.py

@since: 2013-01-23
@version: 2013-07-04
@author: Akitoshi Abe
'''


# mark in description not to show this group on sateraito calendar gadget
MARK_SATERAITO_HIDE = '[sateraito-hide]'
MARK_SATERAITO_SHOW = '[sateraito-show]'
# getgrouplist cache expires in 60 min
GET_GROUP_LIST_CACHE_MINUTES = 60


class _LoadAllGroupOfUser(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
	""" Just load user joining groups in memcache
	  not return to client, for use in serverside only
	"""

	def process(self, google_apps_domain, app_id):
		# set header
		self.setResponseHeader('Content-Type','application/json')

		# check group and update user info if group is changed
		if sateraito_func.checkGroupUpdated(google_apps_domain, app_id, self.viewer_email):
			# update accessible info
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
			# re-check after 15 min
			sateraito_func.addCheckAccessibleInfoQueue(google_apps_domain, app_id, self.viewer_email, countdown=(60 * 15))
# 			task2 = taskqueue.Task(
# 				url='/' + google_apps_domain + '/' + app_id + '/textsearch/tq/checkaccessibleinfo',
# 				params={
# 					'user_email': self.viewer_email
# 					},
# 				countdown=(60 * 15)
# 			)
# 			queue.add(task2)

		# export json data
		jsondata = json.JSONEncoder().encode({'status': 'ok'})
		return jsondata

class LoadAllGroupOfUser(_LoadAllGroupOfUser):
	""" Just load user joining groups in memcache
	  not return to client, for use in serverside only
	"""
	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkGadgetRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)

class LoadAllGroupOfUserOid(_LoadAllGroupOfUser):
	""" Just load user joining groups in memcache
	  not return to client, for use in serverside only
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)


class _GetGroupList(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage):
	# memcache entry expires in 20 min
	memcache_expire_secs = 60 * GET_GROUP_LIST_CACHE_MINUTES

	def _memcache_key(self, viewer_email):
		google_apps_domain = sateraito_func.getDomainPart(viewer_email)
		return 'script=getgrouplist&google_apps_domain=' + str(google_apps_domain) + '&g=2'

	def _fetch_google_data_oauth2(self, viewer_email, google_apps_domain):
		""" fetch group list data from google
"""
		ret_groups = []
		directory_service = sateraito_func.fetch_google_app_service(viewer_email, google_apps_domain)
		page_token = None
		while True:
			group_list_feed = sateraito_func.getGroupListAll(directory_service, page_token, do_not_retry=True)
			groups = group_list_feed.get('groups', None)
			if groups is None:
				break
			for each_group in groups:
				description = str(each_group['description'])
				#
				# [sateraito-hide]
				#
				# hide this group on gadget screen
				#
				hide_group = None
				# step1 check mark in description
				if MARK_SATERAITO_HIDE in description:
					hide_group = True
					# address only hide mark
				# step2 set sateraito setting groups to hide
				group_id = str(each_group['email']).lower()
				group_id_splited = group_id.split('@')
				if group_id_splited[0] == sateraito_inc.DOMAIN_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.TIMECARD_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.MYPORTAL_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.ADDRESS_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.GARAKEITAI_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.WORKFLOW_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.BROWSER_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.PASSWORD_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.GOSOUSHIN_SETTING_GROUP_ID:
					hide_group = True

				if hide_group:
					pass
				else:
					ret_groups.append({
						'group_id': each_group['email'],
						'group_name': each_group['name'],
						})
			page_token = group_list_feed.get('nextPageToken')
			if page_token is None:
				break
		return ret_groups

	def fetch_google_data_ssite(self, viewer_email, google_apps_domain, return_by_object=False):
		""" fetch group list data from ssite
"""
		# google_apps_domain = sateraito_func.getDomainPart(viewer_email)

		ret_groups = []

		service, access_token = sateraito_func.getAccessTokenSSite(google_apps_domain, viewer_email)
		if access_token and service is not None:
			groups_feed = service.getGroupListInfo(access_token)
			logging.info(groups_feed)
			for entry in groups_feed:
				# if group's description have mark not to show on sateraito calendar, do not send
				description = str(entry['description'])

				#
				# [sateraito-hide]
				#
				# hide this group on gadget screen
				#
				hide_group = None
				# step1 check mark in description
				if MARK_SATERAITO_HIDE in description:
					hide_group = True
				# address only hide mark
				# step2 set sateraito setting groups to hide
				group_id = str(entry['group_id']).lower()
				group_id_splited = group_id.split('@')
				if group_id_splited[0] == sateraito_inc.DOMAIN_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.TIMECARD_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.MYPORTAL_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.ADDRESS_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.GARAKEITAI_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.WORKFLOW_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.BROWSER_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.PASSWORD_SETTING_GROUP_ID:
					hide_group = True
				if group_id_splited[0] == sateraito_inc.GOSOUSHIN_SETTING_GROUP_ID:
					hide_group = True

				if hide_group:
					pass
				else:
					ret_groups.append({
						'group_id': group_id,
						'group_name': entry['group_name'],
					})

		# for batch cacheing process
		if return_by_object:
			return ret_groups
		return ret_groups

	def fetch_google_data(self, viewer_email, google_apps_domain):
		# SSITE＆SSOGadget対応
		if sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
			groups = self.fetch_google_data_ssite(viewer_email, google_apps_domain)
		elif sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain):
			groups = sateraito_func.getGroupListSSOGadget(google_apps_domain, viewer_email)
		else:
			groups = self._fetch_google_data_oauth2(viewer_email, google_apps_domain)
			# json data
		jsondata = json.JSONEncoder().encode(groups)
		groups = None  # for GC
		return jsondata

	def addLTCacheTask(self, google_apps_domain, app_id, viewer_email):
		# schedule LTCacheGroupList create task
		logging.info('Adding LTCache create task...')
		target_class = sateraito_func.getBackEndsModuleNameDeveloper('commonprocess')
		queue = taskqueue.Queue('default')
		task = taskqueue.Task(
			url='/' + google_apps_domain + '/' + app_id + '/group/tq/savegrouplist',
			params={
				'user_email': viewer_email,
				'target_class': target_class,
				},
			target=target_class,
			countdown=random.randint(1, 60)
		)
		queue.add(task)

	def process(self, google_apps_domain, app_id):
		# set header
		self.setResponseHeader('Content-Type','application/json')

		# step1. check if cached data exists
		cached_data = memcache.get(self._memcache_key(self.viewer_email))
		if cached_data is not None:
			# cached data found
			if random.randint(1, 100) <= 97:
				# # 97% case, use cached data
				# self.response.out.write(cached_data)
				logging.info('found and respond cached data')
				return cached_data
			else:
				# 3% case, refresh cached data even if not expired
				logging.info('** cache found, but ignoring by random')

		# step2: check LTCacheGroupList
		jsondata_lt, created_date = sateraito_db.LTCacheGroupList.getJsondata(google_apps_domain)
		if jsondata_lt is None or jsondata_lt == '':
			pass
		else:
			expire_date = created_date + datetime.timedelta(minutes=GET_GROUP_LIST_CACHE_MINUTES)
			logging.info('created_date=' + str(created_date) + ' expire_date=' + str(expire_date))
			if sateraito_func.isBiggerDate(datetime.datetime.now(), expire_date):
				# expired
				logging.info('LTCache expired, ignore jsondat_lt')
			else:
				logging.info('** recently created, OK to return LTCache')
				# export json data
				logging.info(jsondata_lt)
				# add data to cache
				if len(jsondata_lt) < memcache.MAX_VALUE_SIZE:
					if not memcache.set(key=self._memcache_key(self.viewer_email), value=jsondata_lt, time=self.memcache_expire_secs):
						logging.warning("Memcache set failed.")
				if sateraito_func.isBiggerDate(datetime.datetime.now() + datetime.timedelta(minutes=10), expire_date):
					# LTCache soon expire: add task to re-create new LTCache
					logging.info('** LTCache soon expire: Adding task...')
					self.addLTCacheTask(google_apps_domain, app_id, self.viewer_email)
				return jsondata_lt

		# schedule LTCacheGroupList create task
		self.addLTCacheTask(google_apps_domain, app_id, self.viewer_email)

		jsondata = None
		try:
			jsondata = self.fetch_google_data(self.viewer_email, google_apps_domain)
		except HttpError as e:
			logging.error('class name:' + e.__class__.__name__ + ' message=' + str(e))
			# Load Json body
			logging.info('e.content=' + str(e.content))
			error = json.JSONDecoder().decode(e.content).get('error', None)
			if error is not None:
				error_code = error.get('code')
				logging.info('error_code:' + str(error_code))
				error_message = error.get('message')
				logging.info('error_message:' + str(error_message))
				errors = error.get('errors')
				if isinstance(errors, list):
					error_reason = errors[0].get('reason')
					logging.info('error_reason:' + str(error_reason))
					if error_code == 403 and error_reason in ['rateLimitExceeded', 'userRateLimitExceeded', 'quotaExceeded']:
						logging.error('** userRateLimitExceeded')

		# export json data
		if jsondata is not None:
			logging.info(jsondata)
			# add data to cache
			if len(jsondata) < memcache.MAX_VALUE_SIZE:
				if not memcache.set(key=self._memcache_key(self.viewer_email), value=jsondata, time=self.memcache_expire_secs):
					logging.warning("Memcache set failed.")
			return jsondata

		# error case
		if jsondata_lt is not None and jsondata_lt != '':
			logging.warn('Error when fetching group data, exporting expired LTCache data...')
			return jsondata_lt
		
		return json.JSONEncoder().encode({})

class GetGroupList(_GetGroupList):
	""" Getting Group List """
	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check gadget request
		if not self.checkGadgetRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)

class GetGroupListOid(_GetGroupList):
	""" Getting Group List """
	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check login
		if not self.checkOidRequest(google_apps_domain):
			return
		
		return self.process(google_apps_domain, app_id)


class TqSaveGroupList(_GetGroupList):

	def doAction(self, google_apps_domain, app_id):
		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return

		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# set header
		self.setResponseHeader('Content-Type','application/json')

		user_email = self.request.get('user_email')
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		if domain_dict is not None:
			user_email = domain_dict.get('impersonate_email')

		# check updating flag
		if sateraito_db.LTCacheGroupListUpdating.isUpdating(google_apps_domain):
			logging.info('** now other task is updating, stop this task')
			return make_response('',200)

		# check data expiration
		jsondata, created_date = sateraito_db.LTCacheGroupList.getJsondata(google_apps_domain)
		if jsondata is None or jsondata == '':
			# NO LTCache: CREATE OK
			pass
		else:
			expire_date = created_date + datetime.timedelta(minutes=GET_GROUP_LIST_CACHE_MINUTES)
			logging.info('created_date=' + str(created_date) + ' expire_date=' + str(expire_date))
			if sateraito_func.isBiggerDate(datetime.datetime.now() + datetime.timedelta(minutes=10), expire_date):
				# LTCache soon expire in 10 minutes: OK to update
				pass
			else:
				# LTCache not expire: NO NEED TO UPDATE
				logging.info('** LTCache NO NEED TO UPDATE')
				return make_response('', 200)

				# set updating flag
			#		sateraito_db.LTCacheGroupListUpdating.setUpdating(google_apps_domain, True)
			# save json data
		while True:
			try:
				ndb.transaction(lambda: sateraito_db.LTCacheGroupListUpdating.setUpdating(google_apps_domain, True))
				break
			except datastore_errors.TransactionFailedError as e:
				logging.warning(e)
				pass

		try:
			jsondata = self.fetch_google_data(user_email, google_apps_domain)
		except HttpError as e:
			logging.error('class name:' + e.__class__.__name__ + ' message=' + str(e))

			#			sateraito_db.LTCacheGroupListUpdating.setUpdating(google_apps_domain, False)
			# save json data
			while True:
				try:
					ndb.transaction(lambda: sateraito_db.LTCacheGroupListUpdating.setUpdating(google_apps_domain, False))
					break
				except datastore_errors.TransactionFailedError as e:
					logging.warning(e)
					pass
			logging.info('** task finished')

			# Load Json body
			logging.info('e.content=' + str(e.content))
			error = json.JSONDecoder().decode(e.content).get('error', None)
			if error is not None:
				error_code = error.get('code')
				logging.info('error_code:' + str(error_code))
				error_message = error.get('message')
				logging.info('error_message:' + str(error_message))
				errors = error.get('errors')
				if isinstance(errors, list):
					error_reason = errors[0].get('reason')
					logging.info('error_reason:' + str(error_reason))
					# Implementing exponential backoff
					if error_code == 403 and error_reason in ['rateLimitExceeded', 'userRateLimitExceeded', 'quotaExceeded']:
						logging.error('** userRateLimitExceeded')
						raise e

		# save json data
		sateraito_db.LTCacheGroupList.saveJsondata(google_apps_domain, jsondata)

		# save json data
		while True:
			try:
				ndb.transaction(lambda: sateraito_db.LTCacheGroupListUpdating.setUpdating(google_apps_domain, False))
				break
			except datastore_errors.TransactionFailedError as e:
				logging.warning(e)
				pass
		logging.info('** task finished')

		#		sateraito_db.LTCacheGroupList.saveJsondata(google_apps_domain, jsondata)
		#		sateraito_db.LTCacheGroupListUpdating.setUpdating(google_apps_domain, False)
		logging.info('saved jsondata=' + str(jsondata))
		return make_response('', 200)


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/group/loadallgroupofuser',
									 view_func=LoadAllGroupOfUser.as_view('GroupLoadAllGroupOfUser'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/group/oid/loadallgroupofuser',
									 view_func=LoadAllGroupOfUserOid.as_view('GroupLoadAllGroupOfUserOid'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/group/getgrouplist',
									 view_func=GetGroupList.as_view('GroupGetGroupList'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/group/oid/getgrouplist',
									 view_func=GetGroupListOid.as_view('GroupGetGroupListOid'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/group/tq/savegrouplist',
									 view_func=TqSaveGroupList.as_view('GroupTqSaveGroupList'))

