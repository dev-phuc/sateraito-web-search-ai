#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

# set default encodeing to utf-8
# from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request
from flask import request, make_response
import json
from sateraito_logger import logging
import datetime
import random
import os
import jinja2
from ucf.utils import jinjacustomfilters

from google.appengine.api import namespace_manager, datastore_errors
from google.appengine.ext import ndb
from google.appengine.api.urlfetch import DownloadError
from apiclient.errors import HttpError

import sateraito_inc
import sateraito_func
import sateraito_db

from sateraito_page import Handler_Basic_Request, _BasePage, _BaseAPI, _OidBasePage

from sateraito_inc import flask_docker
if flask_docker:
	import memcache, taskqueue
else:
	from google.appengine.api import memcache, taskqueue

'''
user.py

@since: 2012-11-27
@version: 2013-09-09
@author: Akitoshi Abe
'''

GET_USER_LIST_CACHE_MINUTES = 60

class _GetUser(Handler_Basic_Request, _BasePage):
	def fetch_google_data(self, google_apps_domain, viewer_email, return_by_object=False):
		""" 
            Get user list data from google
        """
		# OAuth Token(gdata.auth)
		# if you get email correctry, you can get his calendar data even if he has not log on to this script or other user's request

		app_service = sateraito_func.fetch_google_app_service(viewer_email, google_apps_domain)
		user_entry = app_service.users().get(userKey=viewer_email, fields="primaryEmail,isAdmin,name,thumbnailPhotoUrl").execute()

		user_rec = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, str(viewer_email).lower())
		if user_rec is not None:
			user_rec.is_apps_admin = user_entry["isAdmin"]
			user_rec.put()

		thumbnailPhotoUrl = ''
		if 'thumbnailPhotoUrl' in user_entry:
			thumbnailPhotoUrl = user_entry["thumbnailPhotoUrl"]
        
		user_info = {
			'user_email': user_entry["primaryEmail"],
			'family_name': user_entry["name"]["familyName"],
			'given_name': user_entry["name"]["givenName"],
			'photo_url': thumbnailPhotoUrl,
        }

		if return_by_object:
			return user_info

		# return json data
		jsondata = json.JSONEncoder().encode(user_info)
		return jsondata

	def process(self, google_apps_domain, app_id):
		try:
			# SSOGadget対応
			if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain, domain_dict=None):
				jsondata = sateraito_func.fetch_user_data_SSOGadget(google_apps_domain, app_id, self.viewer_email)
			elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain, domain_dict=None):
				jsondata = sateraito_func.fetch_user_data_SSiteGadget(google_apps_domain, self.viewer_email)
			else:
				jsondata = self.fetch_google_data(google_apps_domain, self.viewer_email)
		except DownloadError as instance:
			logging.warn('Gdata request timeout')
			return
			
		# Set header
		self.setResponseHeader('Content-Type', 'application/json')
		# Export json data
		return jsondata

class GetUser(_GetUser):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check openid login
		if not self.checkGadgetRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)

class OidGetUser(_GetUser):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)

class TokenGetUser(_GetUser):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check token login
		if not self.checkTokenOrOidRequest(google_apps_domain):
			return
		self.process(google_apps_domain, app_id)

		return self.process(google_apps_domain, app_id)


class _GetMe(Handler_Basic_Request, _BaseAPI):
	def fetch_google_data(self, google_apps_domain, viewer_email, return_by_object=False):
		"""Get user list data from google"""
		# OAuth Token(gdata.auth)
		# if you get email correctry, you can get his calendar data even if he has not log on to this script or other user's request

		app_service = sateraito_func.fetch_google_app_service(viewer_email, google_apps_domain)
		user_entry = app_service.users().get(userKey=viewer_email, fields="primaryEmail,isAdmin,name,thumbnailPhotoUrl").execute()

		logging.info('user_entry=' + str(user_entry))

		user_rec = sateraito_db.GoogleAppsUserEntry.getInstance(google_apps_domain, str(viewer_email).lower())
		if user_rec is not None:
			user_rec.is_apps_admin = user_entry["isAdmin"]
			user_rec.put()

		user_info = {
			'user_email': user_entry["primaryEmail"],
			'family_name': user_entry["name"]["familyName"],
			'given_name': user_entry["name"]["givenName"],
			'photo_url': user_entry["thumbnailPhotoUrl"],
		}

		return user_info

	def process(self, google_apps_domain, app_id):
		try:
			# Set namespace
			sateraito_func.setNamespace(google_apps_domain, app_id)

			if not self.viewer_email or not sateraito_func.isValidEmail(self.viewer_email):
				return self.responseUnauthorized('Unauthorized: Invalid email.')

			user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(google_apps_domain, self.viewer_email)
			if not user_entry_dict:
				return self.responseUnauthorized('Unauthorized: User not found or not authorized.')

			user_info_dict = sateraito_db.UserInfo.getDict(self.viewer_email, auto_create=True)
			if not user_info_dict:
				return self.responseUnauthorized('Unauthorized: User info not found.')

			# Check need fetch google data to update user info
			family_name = user_info_dict.get('family_name', None)
			given_name = user_info_dict.get('given_name', None)
			photo_url = user_info_dict.get('photo_url', None)
			language = user_info_dict.get('language')

			if not language or language == '':
				language = sateraito_inc.DEFAULT_LANGUAGE

			if not family_name or not given_name or not photo_url:
				user_info = self.fetch_google_data(google_apps_domain, self.viewer_email, return_by_object=True)
				if not user_info:
					return self.responseUnauthorized('Unauthorized: Failed to fetch user data from Google.')

				# Update user info in the database
				user_info_row = sateraito_db.UserInfo.getInstance(self.viewer_email)
				user_info_row.family_name = user_info.get('family_name', '')
				user_info_row.given_name = user_info.get('given_name', '')
				user_info_row.photo_url = user_info.get('photo_url', '')
				user_info_row.put()

				user_info_dict = user_info_row.to_dict()

			data_res = {
				'user_email': user_entry_dict.get('user_email'),
				'user_id': user_entry_dict.get('user_id'),
				'google_apps_domain': user_entry_dict.get('google_apps_domain'),
				'is_apps_admin': user_entry_dict.get('is_apps_admin'),
				'disable_user': user_entry_dict.get('disable_user'),

				'user_info': {
					'family_name': user_info_dict.get('family_name', ''),
					'given_name': user_info_dict.get('given_name', ''),
					'photo_url': user_info_dict.get('photo_url', ''),
					'language': language
				}
      }

			# Response data
			return self.responseDataSuccess(data_res)
      
		except Exception as e:
			return self.responseDataError(f'Error during logout: {str(e)}')

class GetMe(_GetMe):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check openid login
		if not self.checkGadgetRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)

class OidGetMe(_GetMe):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)


class _UserLogout(Handler_Basic_Request, _BaseAPI):
	def process(self, google_apps_domain, app_id):
		try:
			# Set namespace
			sateraito_func.setNamespace(google_apps_domain, app_id)

			# clear session value
			self.session['viewer_email'] = ''
			self.session['opensocial_viewer_id'] = ''
			self.session['is_oidc_loggedin'] = False
			self.session['is_oidc_need_show_signin_link'] = False

			# clear openid connect session
			self.removeCookie(OPENID_COOKIE_NAME)

			data_res = {
				'message': 'User logged out successfully.',
			}

			# Response data
			return self.responseDataSuccess(data_res)

		except Exception as e:
			return self.responseDataError(f'Error during logout: {str(e)}')

class UserLogout(_UserLogout):

	def doAction(self, google_apps_domain, app_id):
		# check openid login
		if not self.checkGadgetRequest(google_apps_domain):
			return
		return self.process(google_apps_domain, app_id)

class OidUserLogout(_UserLogout):

	def doAction(self, google_apps_domain, app_id):
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return
		return self.process(google_apps_domain, app_id)


class UserLogin(Handler_Basic_Request, _OidBasePage):

	def doAction(self, google_apps_domain, app_id):
		# Set namespace
		namespace_manager.set_namespace(google_apps_domain)

		prompt_type = self.request.get('prompt_type')

		logging.debug('============_OIDCAutoLogin==============')
		is_ok, auth_uri = self._OIDCAutoLogin(google_apps_domain, with_error_page=True, prompt_type=prompt_type,
																								 url_to_go_after_oidc_login=sateraito_inc.my_site_url + '/user/after-login',
																								 hl=sateraito_inc.DEFAULT_LANGUAGE)
		if is_ok:
			self.redirect(sateraito_inc.my_site_url + '/user/after-login')

class HandlerAfterLogin(Handler_Basic_Request, _OidBasePage):

	def doAction(self):

		cwd = os.path.dirname(__file__)
		path = os.path.join(cwd, 'templates')
		# bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
		jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False)
		jinjacustomfilters.registCustomFilters(jinja_environment)

		try:
			template_filename = 'ext_after_login.html'
			values = {
			}
			template = jinja_environment.get_template(template_filename)
			return template.render(values)
		except BaseException as e:
			return


class _GetUserList(Handler_Basic_Request, _BasePage):
	""" Get User list
"""

	# memcache entry expires in 10 min
	memcache_expire_secs = 60 * 10

	def _memcache_key(self, viewer_email):
		google_apps_domain = sateraito_func.getDomainPart(viewer_email)
		return 'script=getuserlist&google_apps_domain=' + google_apps_domain + '&g=2'

	def addLTCacheTask(self, google_apps_domain, app_id, viewer_email):
		# schedule LTCacheUserList create task
		logging.info('Adding LTCache create task...')
		target_class = sateraito_func.getBackEndsModuleNameDeveloper('commonprocess')
		queue = taskqueue.Queue('default')
		task = taskqueue.Task(
			url='/' + google_apps_domain + '/' + app_id + '/user/tq/saveuserlist',
			params={
				'user_email': viewer_email,
				'target_class': target_class,
				},
			target=target_class,
			countdown=random.randint(1, 60)
		)
		queue.add(task)

	def fetch_google_data(self, google_apps_domain, app_id, viewer_email):
		# SSOGadget対応
		if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain):
			user_list = sateraito_func.getUserListSSOGadget(google_apps_domain, app_id, viewer_email)
			return json.JSONEncoder().encode(user_list)
		elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
			user_list = sateraito_func.getUserListSSiteGadget(google_apps_domain, viewer_email)
			return json.JSONEncoder().encode(user_list)
		else:
			row_d = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
			if row_d['multi_domain_setting']:
				logging.info('returning multi_domain_setting')
				user_list = []
				q = sateraito_db.GoogleAppsDomainEntry.query()
				for row in q:
					logging.info('row.google_apps_domain=' + str(row.google_apps_domain))
					if row.google_apps_domain is None or row.google_apps_domain == '':
						pass
					else:
						user_list += self._fetch_google_data(google_apps_domain, row.google_apps_domain, viewer_email, return_by_object=True)
				return json.JSONEncoder().encode(user_list)
			else:
				return self._fetch_google_data(google_apps_domain, google_apps_domain, viewer_email, return_by_object=False)

	def _fetch_google_data(self, google_apps_domain, target_google_apps_domain, viewer_email, return_by_object=False):
		""" Get user list data from google
"""
		# apps service / get users in gooogle apps domain
		users = []
		page_token = None
		app_service = sateraito_func.fetch_google_app_service(viewer_email, google_apps_domain)
		while True:
			user_list = app_service.users().list(pageToken=page_token, domain=target_google_apps_domain, fields="nextPageToken,users(name,primaryEmail,thumbnailPhotoUrl)").execute()
			if "users" in user_list:
				for each_user in user_list["users"]:
					thumbnailPhotoUrl = ''
					if 'thumbnailPhotoUrl' in each_user:
						thumbnailPhotoUrl = each_user["thumbnailPhotoUrl"]
					users.append({
						'user_email': each_user["primaryEmail"],
						'family_name': each_user["name"]["familyName"],
						'given_name': each_user["name"]["givenName"],
						'photo_url': thumbnailPhotoUrl,
						})
			page_token = user_list.get("nextPageToken")
			if page_token is None:
				break

		if return_by_object:
			return users

		# return json data
		return json.JSONEncoder().encode(users)

	def process(self, google_apps_domain, app_id):
		# set header
		self.setResponseHeader('Content-Type', 'application/json')
		# check if cached data exists
		cached_data = memcache.get(self._memcache_key(self.viewer_email))
		if cached_data is not None:
			# cached data found
			if random.randint(1, 100) <= 97:
				logging.info('found and respond cached data')
				return cached_data
			else:
				# 3% case, refresh cached data even if not expired
				logging.info('** cache found, but ignoring by random')

		# step2: check LTCacheUserList
		jsondata_lt, created_date = sateraito_db.LTCacheUserList.getJsondata(google_apps_domain)
		if jsondata_lt is None or jsondata_lt == '':
			pass
		else:
			expire_date = created_date + datetime.timedelta(minutes=GET_USER_LIST_CACHE_MINUTES)
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
					if not memcache.set(key=self._memcache_key(self.viewer_email), value=jsondata_lt,
						time=self.memcache_expire_secs):
						logging.warning("Memcache set failed.")
				if sateraito_func.isBiggerDate(datetime.datetime.now() + datetime.timedelta(minutes=10), expire_date):
					# LTCache soon expire: add task to re-create new LTCache
					logging.info('** LTCache soon expire: Adding task...')
					self.addLTCacheTask(google_apps_domain, app_id, self.viewer_email)
				return jsondata_lt

		# schedule LTCacheUserList create task
		self.addLTCacheTask(google_apps_domain, app_id, self.viewer_email)

		jsondata = None
		try:
			jsondata = self.fetch_google_data(google_apps_domain, app_id, self.viewer_email)
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
			logging.warn('Error when fetching user data, exporting expired LTCache data...')
			return jsondata_lt

class OidGetUserList(_GetUserList):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check openid login
		if not self.checkOidRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)

class TokenGetUserList(_GetUserList):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check login
		if not self.checkTokenOrOidRequest(google_apps_domain):
			return
		self.process(google_apps_domain, app_id)
		return self.process(google_apps_domain, app_id)

class GetUserList(_GetUserList):

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# check openid login
		if not self.checkGadgetRequest(google_apps_domain):
			return
		return self.process(google_apps_domain, app_id)


class TqSaveUserList(_GetUserList):

	def doAction(self, google_apps_domain, app_id):
		# check retry count
		retry_cnt = request.headers.get('HTTP_X_APPENGINE_TASKRETRYCOUNT',None)
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return

		# set namespace
		namespace_manager.set_namespace(google_apps_domain)
		# set header
		self.setResponseHeader('Content-Type', 'application/json')

		user_email = self.request.get('user_email')
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(google_apps_domain)
		if domain_dict is not None:
			user_email = domain_dict.get('impersonate_email')

		# check updating flag
		if sateraito_db.LTCacheUserListUpdating.isUpdating(google_apps_domain):
			logging.info('** now other task is updating, stop this task')
			return make_response('',200)

		# check data expiration
		jsondata, created_date = sateraito_db.LTCacheUserList.getJsondata(google_apps_domain)
		if jsondata is None or jsondata == '':
			# NO LTCache: CREATE OK
			pass
		else:
			expire_date = created_date + datetime.timedelta(minutes=GET_USER_LIST_CACHE_MINUTES)
			logging.info('created_date=' + str(created_date) + ' expire_date=' + str(expire_date))
			if sateraito_func.isBiggerDate(datetime.datetime.now() + datetime.timedelta(minutes=10), expire_date):
				# LTCache soon expire in 10 minutes: OK to update
				pass
			else:
				# LTCache not expire: NO NEED TO UPDATE
				logging.info('** LTCache NO NEED TO UPDATE')
				return make_response('', 200)

		# save json data
		while True:
			try:
				ndb.transaction(lambda: sateraito_db.LTCacheUserListUpdating.setUpdating(google_apps_domain, True))
				break
			except datastore_errors.TransactionFailedError as e:
				logging.warning(e)
				pass

		try:
			jsondata = self.fetch_google_data(google_apps_domain, app_id, user_email)
		except HttpError as e:
			logging.error('class name:' + e.__class__.__name__ + ' message=' + str(e))

			# save json data
			while True:
				try:
					ndb.transaction(lambda: sateraito_db.LTCacheUserListUpdating.setUpdating(google_apps_domain, False))
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
		sateraito_db.LTCacheUserList.saveJsondata(google_apps_domain, jsondata)

		# save json data
		while True:
			try:
				ndb.transaction(lambda: sateraito_db.LTCacheUserListUpdating.setUpdating(google_apps_domain, False))
				break
			except datastore_errors.TransactionFailedError as e:
				logging.warning(e)
				pass
		logging.info('** task finished')

		logging.info('saved jsondata=' + str(jsondata))
		return make_response('** task finished',200)


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/getuser',
									 view_func=GetUser.as_view('UserGetUser'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/oid/getuser',
									 view_func=OidGetUser.as_view('UserOidGetUser'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/token/getuser',
									 view_func=TokenGetUser.as_view('UserTokenGetUser'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/getme',
									 view_func=GetMe.as_view('GetMe'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/oid/getme',
									 view_func=OidGetMe.as_view('OidGetMe'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/logout',
									 view_func=UserLogout.as_view('UserLogout'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/oid/logout',
									 view_func=OidUserLogout.as_view('OidUserLogout'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/login',
									 view_func=UserLogin.as_view('UserLogin'))
	app.add_url_rule('/user/after-login',
									 view_func=HandlerAfterLogin.as_view('UserAfterLogin'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/getuserlist',
									 view_func=GetUserList.as_view('UserGetUserList'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/oid/getuserlist',
									 view_func=OidGetUserList.as_view('UserOidGetUserList'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/token/getuserlist',
									 view_func=TokenGetUserList.as_view('UserTokenGetUserList'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/user/tq/saveuserlist',
									 view_func=TqSaveUserList.as_view('UserTqSaveUserList'))
