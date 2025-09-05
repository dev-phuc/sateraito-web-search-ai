#!/usr/bin/python
# coding: utf-8

'''
sateraito_page.py

@since: 2023-02-20
@version: 2023-02-20
@author: Akitoshi Abe
'''

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

# g2対応
import flask
from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request, current_app
from flask.views import View, MethodView

from functools import wraps
from ucf.utils.ucfutil import UcfUtil
from ucf.config.ucfconfig import UcfConfig

import os, sys, traceback
import urllib, io, gzip
import jinja2
import base64
import json
import datetime, time
import dateutil.parser		# GAE Gen2対応
import urllib
import random

from http import cookies
from ucf.utils.ucfutil import UcfUtil
from ucf.utils.ssofunc import *  # GAEGEN2対応：SAML、SSO連携対応
from Crypto.Cipher import AES

# GAEGEN2対応:独自ロガー
import sateraito_logger as logging

from googleapiclient import errors
from google.appengine.ext import blobstore
from oauthlib.oauth2 import WebApplicationClient
from google.appengine.api import urlfetch, memcache, namespace_manager, users, taskqueue

import sateraito_db
import sateraito_inc
import sateraito_func

urlfetch.set_default_fetch_deadline(sateraito_inc.URLFETCH_TIMEOUT_SECOND)

cwd = os.path.dirname(__file__)
path = os.path.join(cwd, 'templates')
bcc = jinja2.MemcachedBytecodeCache(client=memcache.Client(), prefix='jinja2/bytecode/', timeout=None)
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path), auto_reload=False, bytecode_cache=bcc)

OPENID_COOKIE_NAME = 'SATEID2'
URLFETCH_TIMEOUT_SECOND = 30
MAX_OPENID_SESSION_AGE_DAYS = 31  # 31 days

_CONTENT_DISPOSITION_FORMAT = b'%s; filename="%s"'
_CONTENT_DISPOSITION_FORMAT_UTF8 = "%s; filename*=UTF-8''%s"

# GETでリクエストして結果を取得
def HttpGetAccess(url):
	body = None
	req = urllib.request.Request(url)
	with urllib.request.urlopen(req) as res:
		body = res.read()
	return body


# POSTでリクエストして結果を取得
def HttpPostAccess(url, values, headers):
	body = None
	req = urllib.request.Request(url, urllib.parse.urlencode(values).encode(), headers)  # ２番目のdataパラメータを指定するとPOSTになる
	with urllib.request.urlopen(req) as res:
		body = res.read()
	return body


# POSTでリクエストして結果を取得(クエリが ○○＝×× じゃなくて  △△△△△△ 状態の場合に使う)
def HttpPostAccessRow(url, values, headers):
	result = urlfetch.fetch(url=url, method=urlfetch.POST, payload=values, headers=headers, deadline=sateraito_inc.URLFETCH_TIMEOUT_SECOND)
	return result


# GAEGEN2対応
# ビューメソッド（get, post など）戻り値が None のときに b'' に変換するデコレーター
def convert_result_none_to_empty_str(func):
	@wraps(func)
	def _wrapper(*args, **keywords):
		oResult = func(*args, **keywords)
		if (oResult is None):
			oResult = b''
		return oResult

	return _wrapper


def removeItemFromQueryString(query_string, item):
	if query_string is None or query_string == '':
		return query_string
	splited = str(query_string).split('&')
	while item in splited:
		splited.remove(item)
	return '&'.join(splited)


# GAEGEN2対応
# csrf チェック用デコレータ
def check_csrf(func):
	@wraps(func)
	def _wrapper1(*args, **keywords):
		if (sateraito_func.checkCsrf(args[0].request) == False):
			logging.warn('CSRF Error.')
			return Response('', status=403)

		return func(*args, **keywords)

	return _wrapper1


# GAEGEN2対応
# OpenIDConnect 認証チェック用デコレータ
def check_oid_request(func):
	@wraps(func)
	def _wrapper1(*args, **keywords):
		google_apps_domain = keywords.get('google_apps_domain')
		logging.info('check_oid_request: google_apps_domain=' + google_apps_domain)

		if not _BasePage.checkOidRequest(google_apps_domain):
			logging.warn('OID Request Error.')
			return Response('OID Request Error.', status=403)

		return func(*args, **keywords)

	return _wrapper1


# GAEGEN2対応
class DummyClass():
	pass


# GAEGEN2対応
# request.headers を処理するためのクラス
class HeadersWrapperClass(dict):
	def __init__(self, environ):
		dict.__init__(self)
		self.environ = environ

	def add_header(self, strKey, strValue):
		self[strKey] = strValue


# /healthなど一般的なページのベースクラス（多重継承して使います）
class Handler_Basic_Request(MethodView):

	@convert_result_none_to_empty_str
	def get(self, *args, **keywords):
		logging.debug('Handler_Basic_Request:get...')
		# 実際の処理
		return self.doAction(*args, **keywords)

	@convert_result_none_to_empty_str
	def post(self, *args, **keywords):
		logging.debug('Handler_Basic_Request:post...')
		# 実際の処理
		return self.doAction(*args, **keywords)

	@convert_result_none_to_empty_str
	def put(self, *args, **keywords):
		logging.debug('Handler_Basic_Request:put...')
		# 実際の処理
		return self.doAction(*args, **keywords)
	
	@convert_result_none_to_empty_str
	def delete(self, *args, **keywords):
		logging.debug('Handler_Basic_Request:delete...')
		# 実際の処理
		return self.doAction(*args, **keywords)

class _BasePage():
	viewer_email_raw = None  # 大文字小文字をそのままにしたもの
	viewer_email = None  # 小文字統一のもの
	viewer_user_id = None
	viewer_id = None
	mode = ''  # sharepoint or ssite or ...

	def __init__(self, *args, **kwargs):
		logging.debug(self.__class__.__name__ + '_BasePage.init() start.')

		super().__init__(*args, **kwargs)
		self.session = flask.session

		self.request = flask.request
		self.request.get = self._requestGet
		self.request.referer = self.request.referrer

		self._response_text = []
		self._response_status_code = -1
		self._redirect_url = None

		self.response = DummyClass()
		self.response.set_status = self._response_set_status
		self.response.headers = HeadersWrapperClass(self.request.environ)
		self.response.status = None  # self.response.status = 403 のような記述に対応

		self.response.out = DummyClass()
		self.response.out.write = self._response_write
		self.response.write = self._response_write

		# GAEGEN2対応
		@after_this_request
		def _updateResponseStatus(response):
			if (len(self._response_text) > 0):
				if (response.calculate_content_length()):
					# 念のため既にレスポンステキストが設定されている場合は例外を発生させる
					# 実装によってはこのチェックは無い方が良いかも。。
					logging.error('response.calculate_content_length() = ' + str(response.calculate_content_length()))
					logging.error('response.get_data() = ' + str(response.get_data()))
					raise Exception('_updateResponseStatus: content is not empty.')
				response.set_data(b''.join(self._response_text))

			if (self.response.status is not None):
				response.status = str(self.response.status)

			if (self._response_status_code > 0):
				response.status_code = self._response_status_code

			response.headers.update(self.response.headers)

			if (self._redirect_url):
				response = flask.redirect(self._redirect_url)

			return response

	def _requestGet(self, strName, defaultValue=''):
		result = self.request.args.get(strName, None)
		if (result is None) and (not isinstance(self, blobstore.BlobstoreUploadHandler)):
			# BlobstoreUploadHandler では request.form, request.files にアクセスするとアップロードしたファイルを取得できなくなるので注意が必要
			result = self.request.form.get(strName, None)

			if (result is None):
				result = self.request.files.get(strName, None)

		if (result is None):
			result = defaultValue

		return result

	# GAEGEN2対応
	def _response_write(self, output_text):
		if (isinstance(output_text, str)):
			output_text = output_text.encode()

		self._response_text.append(output_text)

	# GAEGEN2対応
	def _response_set_status(self, status_code):
		self._response_status_code = status_code

	def json_response(self, obj, status=200):
		self.setResponseHeader('Content-Type', 'application/json; charset=utf-8')
		self.setResponseHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
		self.setResponseHeader('Pragma', 'no-cache')
		self.setResponseHeader('Expires', '0')
		self._response_status_code = status
		return obj

	# GAEGEN2対応
	def error(self, status_code):
		self._response_text.clear()
		self._response_status_code = status_code

	# GAEGEN2対応
	def redirect(self, redirect_rul):
		self._redirect_url = redirect_rul

	# GAEGEN2対応
	# Responseヘッダーセット
	@classmethod
	def setResponseHeader(cls, name, value):
		@after_this_request
		def _setResponseHeader(response):
			response.headers[name] = value
			return response

	# ワークフロー管理者かどうかを判定
	def isWorkflowAdmin(self, user_email, tenant_or_domain, app_id=None, do_not_include_additional_admin=False):
		# if self.mode == sateraito_func.MODE_SSITE:
		if sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(tenant_or_domain):
			return sateraito_func.isWorkflowAdminForSSite(user_email, tenant_or_domain, app_id, do_not_include_additional_admin=do_not_include_additional_admin)
		elif sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(tenant_or_domain):
			return sateraito_func.isWorkflowAdminForSSOGadget(user_email, tenant_or_domain, app_id, do_not_include_additional_admin=do_not_include_additional_admin)
		elif self.mode == sateraito_func.MODE_SHAREPOINT:
			return sateraito_func.isWorkflowAdminForSharePoint(user_email, tenant_or_domain, app_id,  do_not_include_additional_admin=do_not_include_additional_admin)
		else:
			return sateraito_func.isWorkflowAdmin(user_email, tenant_or_domain, app_id, do_not_include_additional_admin=do_not_include_additional_admin)

	def setNamespace(self, tenant_or_domain, app_id):
		"""	Args: tenant_or_domain
							app_id
		Return: True is app_id is correct, false is not
		"""
		return sateraito_func.setNamespace(tenant_or_domain, app_id)

	def getUserEntryByTokenForSharePoint(self, tenant_or_domain, user_token):

		if user_token is None or user_token == '':
			return None

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')

		# token check
		q = sateraito_db.GoogleAppsUserEntry.query()
		q = q.filter(sateraito_db.GoogleAppsUserEntry.user_token_for_sharepoint == user_token)
		user_entry = q.get()
		if user_entry is not None and (user_entry.token_expire_date_for_sharepoint is None or user_entry.token_expire_date_for_sharepoint < datetime.datetime.now()):
			user_entry = None
		namespace_manager.set_namespace(old_namespace)
		return user_entry

	def checkToken(self, tenant_or_domain, is_without_error_response_status=False, user_token=None):  # g2対応：user_tokenを渡せるように対応
		# set namespace
		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')
		# get parameter
		if user_token is None:
			user_token = self.request.get('token')
		logging.info('token=' + user_token)

		self.mode = ''

		# SSITE対応…GoogleAppsDomainEntryからSSITEのドメイン（テナント）かを判定 2016.08.24
		if sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(tenant_or_domain):

			# SSiteモードフラグをセット
			self.mode = sateraito_func.MODE_SSITE
			user_entry = None
			if user_entry is None:
				q = sateraito_db.GoogleAppsUserEntry.query()
				q = q.filter(sateraito_db.GoogleAppsUserEntry.user_token == user_token)
				user_entry = q.get()

		else:

			self.mode = ''

			# token check
			q = sateraito_db.GoogleAppsUserEntry.query()
			q = q.filter(sateraito_db.GoogleAppsUserEntry.user_token == user_token)
			user_entry = q.get()

			if user_entry is None:
				# q = sateraito_db.GoogleAppsUserEntry.all()
				# q.filter('user_token_for_sharepoint =', user_token)
				q = sateraito_db.GoogleAppsUserEntry.query()
				q = q.filter(sateraito_db.GoogleAppsUserEntry.user_token_for_sharepoint == user_token)
				user_entry = q.get()
				if user_entry is not None:
					# SharePointモードフラグをセット
					self.mode = sateraito_func.MODE_SHAREPOINT

		logging.info('mode=' + str(self.mode))

		if user_entry is None:
			logging.warning('user token not matched')
			# user token not matched
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False
		if (self.mode != sateraito_func.MODE_SHAREPOINT and user_entry.token_expire_date < datetime.datetime.now()) or (self.mode == sateraito_func.MODE_SHAREPOINT and user_entry.token_expire_date_for_sharepoint < datetime.datetime.now()):
			logging.warning('token found, but expired')
			# token found, but expired
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False

		self.viewer_email = user_entry.user_email.lower() if user_entry.user_email is not None else None
		self.viewer_email_raw = user_entry.user_email
		self.viewer_user_id = user_entry.user_id
		namespace_manager.set_namespace(old_namespace)
		logging.info('viewer_email=' + str(self.viewer_email))
		return True

	def checkTokenOrOidRequest(self, google_apps_domain):
		# get parameter
		user_token = self.request.get('token')
		logging.info('token=' + user_token)

		# token check
		user_dict = sateraito_db.GoogleAppsUserEntry.getDictByToken(google_apps_domain, user_token)

		check_token_ok = True
		if user_dict is None:
			# user token not matched
			logging.warn('user token not matched')
			check_token_ok = False
			if not self.checkOidRequest(google_apps_domain):
				return False
		elif user_dict['token_expire_date'] < datetime.datetime.now():
			# token found, but expired
			logging.warn('token found, but expired')
			check_token_ok = False
			if not self.checkOidRequest(google_apps_domain):
				return False

		if check_token_ok:
			self.viewer_email = str(user_dict['user_email']).lower()
			self.viewer_user_id = user_dict['user_id']
		return True

	def checkOneTimeToken(self, tenant_or_domain, is_without_error_response_status=False):
		# set namespace
		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')
		# get parameter
		user_token = self.request.get('ot_token')
		logging.info('token=' + user_token)

		# ワンタイムトークンを取得＆チェック
		q = sateraito_db.OneTimeUserToken.query()
		q = q.filter(sateraito_db.OneTimeUserToken.user_token == user_token)
		entry = q.get()
		if entry is None:
			# token not matched
			logging.info('token not matched')
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False
		if entry.token_expire_date < datetime.datetime.now():
			# token found, but expired
			logging.info('token found, but expired')
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False

		# SharePointモードフラグをセット
		if entry.is_sharepoint_mode:
			self.mode = sateraito_func.MODE_SHAREPOINT
		# SSITE対応…GoogleAppsDomainEntryからSSITEのドメイン（テナント）かを判定 2016.08.24
		elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(tenant_or_domain):
			self.mode = sateraito_func.MODE_SSITE
		else:
			self.mode = ''
		logging.info('mode=' + str(self.mode))

		# 本来の checkToken の処理
		q = sateraito_db.GoogleAppsUserEntry.query()
		q = q.filter(sateraito_db.GoogleAppsUserEntry.user_email.IN([entry.user_email, entry.user_email.lower()]))
		user_entry = q.get()

		if user_entry is None:
			logging.debug('** user_entry is none')
			# user token not matched
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False
		if user_entry.token_expire_date < datetime.datetime.now():
			# token found, but expired
			logging.debug('** token found, but expired user_entry.token_expire_date=' + str(
				user_entry.token_expire_date) + ' datetime.datetime.now()=' + str(datetime.datetime.now()))
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False

		self.viewer_email = user_entry.user_email.lower() if user_entry.user_email is not None else None
		self.viewer_email_raw = user_entry.user_email
		self.viewer_user_id = user_entry.user_id

		namespace_manager.set_namespace(old_namespace)
		return True

	def checkGadgetRequest(self, tenant_or_domain, is_with_check_csrf_token=False):
		# if sateraito_inc.developer_mode:
		# 	self.viewer_email = 'admin@vn2.sateraito.co.jp'
		# 	self.viewer_email_raw = 'admin@vn2.sateraito.co.jp'
		# 	self.viewer_user_id = 'admin@vn2.sateraito.co.jp'
		# 	return True

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')

		checker = sateraito_func.RequestChecker()
		if not sateraito_inc.flask_docker and not checker.checkContainerSign(self.request):
			logging.exception('Illegal access')
			self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False

		self.mode = checker.mode
		logging.info('mode=' + str(self.mode))
		logging.info('opensocial_viewer_id=' + str(checker.opensocial_viewer_id))

		# domain matching
		if checker.google_apps_domain != tenant_or_domain and checker.google_apps_domain_from_gadget_url != tenant_or_domain:
			logging.exception('google_apps_domain does not match: user email domain=' + str(checker.google_apps_domain) + ' accessing domain=' + tenant_or_domain)
			self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False

		# csrfトークンチェック
		# if False:
		if is_with_check_csrf_token:
			user_token = self.request.get('token')
			logging.debug('check_csrf_token...')
			logging.debug(user_token)
			if user_token is None or user_token == '':
				self.response.set_status(403)
				namespace_manager.set_namespace(old_namespace)
				return False
			q = sateraito_db.GoogleAppsUserEntry.query(keys_only=True)
			if self.mode == sateraito_func.MODE_SHAREPOINT:
				q = q.filter(sateraito_db.GoogleAppsUserEntry.opensocial_viewer_id_for_sharepoint == checker.opensocial_viewer_id)
			else:
				q = q.filter(sateraito_db.GoogleAppsUserEntry.opensocial_viewer_id == checker.opensocial_viewer_id)
			user_entry = sateraito_db.GoogleAppsUserEntry.getByKey(q.get())
			# token check
			if user_entry is None:
				# user token not matched
				logging.exception('Invalid token')
				self.response.set_status(403)
				namespace_manager.set_namespace(old_namespace)
				return False
			if self.mode == sateraito_func.MODE_SHAREPOINT:
				if user_entry.user_token_for_sharepoint != user_token or user_entry.token_expire_date_for_sharepoint is None or user_entry.token_expire_date_for_sharepoint < datetime.datetime.now():
					# token found, but expired
					logging.exception('Invalid token')
					self.response.set_status(403)
					namespace_manager.set_namespace(old_namespace)
					return False
			else:
				if user_entry.user_token != user_token or user_entry.token_expire_date is None or user_entry.token_expire_date < datetime.datetime.now():
					# token found, but expired
					logging.exception('Invalid token')
					self.response.set_status(403)
					namespace_manager.set_namespace(old_namespace)
					return False

		self.viewer_email = checker.viewer_email.lower() if checker.viewer_email is not None else None
		self.viewer_email_raw = checker.viewer_email
		self.viewer_user_id = checker.viewer_user_id

		namespace_manager.set_namespace(old_namespace)
		return True

	def checkOidRequest(self, tenant_or_domain, is_without_error_response_status=False, is_without_check_csrf_token=False):
		# if sateraito_inc.developer_mode:
		# 	self.viewer_email = 'admin@vn2.sateraito.co.jp'
		# 	self.viewer_email_raw = 'admin@vn2.sateraito.co.jp'
		# 	self.viewer_user_id = 'admin@vn2.sateraito.co.jp'
		# 	return True

		mode = self.request.get('mode')
		logging.info('mode=' + mode)

		# SSITE対応…GoogleAppsDomainEntryからSSITEのドメイン（テナント）かを判定 2016.08.24
		if sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(tenant_or_domain):
			# できるだけAppsにインタフェースを合わせるため変更 2016.12.15
			return self._checkOIDCRequestForSSite(tenant_or_domain, is_without_error_response_status=is_without_error_response_status, is_without_check_csrf_token=is_without_check_csrf_token)
		# SSOGadget対応
		elif sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(tenant_or_domain):
			# できるだけAppsにインタフェースを合わせるため変更 2016.12.15
			return self._checkOIDCRequestForSSOGadget(tenant_or_domain, is_without_error_response_status=is_without_error_response_status, is_without_check_csrf_token=is_without_check_csrf_token)
		elif mode == sateraito_func.MODE_SHAREPOINT:
			is_ok, user_entry = self.checkOidRequestAndGetUserEntryForSharePoint(tenant_or_domain, is_without_error_response_status=is_without_error_response_status, is_check_with_sharepoint_auth_url=is_without_check_csrf_token)
			return is_ok
		elif sateraito_func.isOauth2Domain(tenant_or_domain):
			return self._checkOIDCRequest(tenant_or_domain, is_without_error_response_status=is_without_error_response_status, is_without_check_csrf_token=is_without_check_csrf_token)
		else:
			return self._checkOidRequest(tenant_or_domain, is_without_error_response_status=is_without_error_response_status, is_without_check_csrf_token=is_without_check_csrf_token)

	def _checkOidRequest(self, tenant_or_domain, is_without_error_response_status=False, is_without_check_csrf_token=False):

		# CSRFトークンチェック
		if not is_without_check_csrf_token and sateraito_func.checkCsrf(self.request) == False:
			logging.exception('Invalid token')
			self.response.set_status(403)
			return False

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')
		# check openid login
		user = users.get_current_user()
		if user is None:
			logging.info('current user is None.')
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False

		viewer_email = user.email()
		if not sateraito_func.isCompatibleDomain(tenant_or_domain, sateraito_func.getDomainPart(viewer_email)):
			self.response.out.write('unmatched google apps domain and login user')
			logging.info('unmatched google apps domain "' + tenant_or_domain + '" and login user "' + str(viewer_email) + '"')
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False

		self.viewer_email = viewer_email.lower() if viewer_email is not None else None
		self.viewer_email_raw = viewer_email
		self.viewer_user_id = user.user_id()
		namespace_manager.set_namespace(old_namespace)
		return True

	def _checkOIDCRequest(self, tenant_or_domain, skip_domain_compatibility=False, is_without_error_response_status=False, is_without_check_csrf_token=False, check_domain_compatibility_both_side=False):

		# CSRFトークンチェック
		if not sateraito_inc.flask_docker and not is_without_check_csrf_token and sateraito_func.checkCsrf(self.request) == False:
			logging.error('Invalid token')
			self.response.set_status(403)
			return False

		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')

		# check if openid connect login
		viewer_email = self.session.get('viewer_email')
		logging.info('viewer_email=' + str(viewer_email))
		is_oidc_loggedin = self.session.get('is_oidc_loggedin')
		logging.debug('is_oidc_loggedin=' + str(is_oidc_loggedin))

		# if is_oidc_loggedin is None or not is_oidc_loggedin or viewer_email is None:
		if is_oidc_loggedin is None or not is_oidc_loggedin or viewer_email is None or viewer_email == '':
			# logging.error('_checkOIDCRequest:user not logged in')
			logging.warning('_checkOIDCRequest:user not logged in')
			if not is_without_error_response_status:
				self.response.set_status(403)
			return False

		viewer_email_domain = sateraito_func.getDomainPart(viewer_email)
		if not skip_domain_compatibility and viewer_email_domain != tenant_or_domain:
			if check_domain_compatibility_both_side:
				if not sateraito_func.isCompatibleDomain(tenant_or_domain, viewer_email_domain):
					logging.warning('unmatched google apps domain and login user')
					self.response.out.write('unmatched google apps domain and login user')
					if not is_without_error_response_status:
						self.response.set_status(403)
					return False
			else:
				if not sateraito_func.isCompatibleDomain(tenant_or_domain, viewer_email_domain):
					logging.warning('unmatched google apps domain and login user')
					self.response.out.write('unmatched google apps domain and login user')
					if not is_without_error_response_status:
						self.response.set_status(403)
					return False
		self.viewer_email = viewer_email.lower() if viewer_email is not None else None
		self.viewer_email_raw = viewer_email
		namespace_manager.set_namespace(old_namespace)
		return True

	# サテライトサイト対応：ログインチェック（チェックのみ）
	def _checkOIDCRequestForSSite(self, tenant_or_domain, is_without_error_response_status=False, is_without_check_csrf_token=False):
		is_ok = self._checkOIDCRequest(tenant_or_domain, is_without_error_response_status=is_without_error_response_status, is_without_check_csrf_token=is_without_check_csrf_token)
		self.mode = sateraito_func.MODE_SSITE
		return is_ok

	# SSOGadget対応：ログインチェック（チェックのみ）
	def _checkOIDCRequestForSSOGadget(self, tenant_or_domain, is_without_error_response_status=False, is_without_check_csrf_token=False):
		is_ok = self._checkOIDCRequest(tenant_or_domain, skip_domain_compatibility=True, is_without_error_response_status=is_without_error_response_status, is_without_check_csrf_token=is_without_check_csrf_token)
		self.mode = sateraito_func.MODE_SSOGADGET
		return is_ok

	def checkOidRequestAndGetUserEntryForSharePoint(self, tenant_or_domain, is_without_error_response_status=False, is_use_request_token=False, is_check_with_sharepoint_auth_url=False):

		# このアプリケーションID環境の設定を取得（↓のnamespace設定の前に取得）
		other_setting = sateraito_db.AdminConsoleSetting.getInstance(auto_create=True)
		old_namespace = namespace_manager.get_namespace()
		sateraito_func.setNamespace(tenant_or_domain, '')

		# 認証トークンを取得
		if not is_use_request_token:
			user_token = self.request.cookies.get('auth_token')
		else:
			user_token = self.request.get('token')
		logging.info('user_token=' + str(user_token))

		user_entry = self.getUserEntryByTokenForSharePoint(tenant_or_domain, user_token)
		if user_entry is None:
			logging.info('current user is None.')

			# 有効なトークンがない場合、SharePointアプリパーツ経由で認証を取る（擬似的OpenID）2015/02/15
			if is_check_with_sharepoint_auth_url and self.request.get('spauth') != '1':
				sharepoint_auth_url = other_setting.sharepoint_auth_url
				if sharepoint_auth_url is not None and sharepoint_auth_url != '':
					boolShowError = False
					# リダイレクト前に返ってくるべきURLをセッションに入れておく（パラメータを渡せないので苦肉の策）
					self.session['sharepoint_auth_redirect_url'] = UcfUtil.appendQueryString(self.request.url, 'spauth', '1')  # spauth…リダイレクトループ防止用
					# リダイレクト
					self.redirect(sharepoint_auth_url.encode('utf-8'))
					return False, None

			if not is_without_error_response_status:
				self.response.set_status(403)
			return False, None

		viewer_email = user_entry.user_email

		if not sateraito_func.isCompatibleDomain(tenant_or_domain, sateraito_func.getDomainPart(viewer_email)):
			# self.response.out.write('unmatched available domain and login user')
			logging.info('unmatched google_apps_domain "' + tenant_or_domain + '" and login user "' + str(viewer_email) + '"')
			if not is_without_error_response_status:
				self.response.set_status(403)
			namespace_manager.set_namespace(old_namespace)
			return False, None

		self.viewer_email = viewer_email.lower() if viewer_email is not None else None
		self.viewer_email_raw = viewer_email
		self.viewer_user_id = user_entry.user_id
		namespace_manager.set_namespace(old_namespace)
		# SharePointモードフラグをセット
		self.mode = sateraito_func.MODE_SHAREPOINT
		return True, user_entry

	def removeAppsCookie(self):
		self.removeCookie(OPENID_COOKIE_NAME)

	def removeCookie(self, cookie_name):
		# set past date to cookie --> cookie will be deleted
		# SameSite対応 2019.12.23（secure属性必須）
		if sateraito_func.isSameSiteCookieSupportedUA(self.request.headers.get('User-Agent')):
			self.response.headers.add_header('Set-Cookie', cookie_name + '=deleted; expires=Fri, 31-Dec-2000 23:59:59 GMT; path=/;SameSite=None;secure;')
		else:
			self.response.headers.add_header('Set-Cookie', cookie_name + '=deleted; expires=Fri, 31-Dec-2000 23:59:59 GMT; path=/;secure;')

	# クッキーの値をセット（期限指定無しの場合は無期限）
	@classmethod
	def setCookie(cls, name, value, expires=None, path='/', secure='secure', domain='', httpOnly=False, living_sec=None, samesite='None'):

		# SameSiteをU/Aで判別して自動付与する対応
		samesite = 'none' if (secure == 'secure') and sateraito_func.isSameSiteCookieSupportedUA(flask.request.headers.get('User-Agent')) else ''

		if (not expires):
			if (living_sec) and (living_sec > 0):
				expires = UcfUtil.add_seconds(UcfUtil.getNow(), living_sec).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
			else:
				expires = None

		@after_this_request
		def _setCookie(response):
			dictParam = {
				'secure': (secure == 'secure'),
				'httponly': httpOnly,
			}

			if (expires): dictParam['expires'] = expires
			if (path): dictParam['path'] = path
			if (domain): dictParam['domain'] = domain
			if (samesite): dictParam['samesite'] = samesite

			response.set_cookie(
				name,
				value=value,
				**dictParam
			)
			return response

	def getAppIdFromNamespace(self, namespace_name):
		splited = namespace_name.split(sateraito_func.DELIMITER_NAMESPACE_DOMAIN_APP_ID)
		num_splited = len(splited)
		app_id = sateraito_func.DEFAULT_APP_ID
		if num_splited > 1:
			app_id = splited[num_splited - 1]
		return app_id

	def getGoogleAppsDomainFromNamespace(self, namespace_name):
		splited = namespace_name.split(sateraito_func.DELIMITER_NAMESPACE_DOMAIN_APP_ID)
		num_splited = len(splited)
		if num_splited > 1:
			return splited[0]
		else:
			return namespace_name

	@classmethod
	def _decryptoForCookie(cls, enc_value):
		try:
			return UcfUtil.deCrypto(enc_value, UcfConfig.COOKIE_CRYPTOGRAPIC_KEY)
		except Exception as e:
			logging.warning('enc_value=' + enc_value)
			logging.warning(e)
			return enc_value

	@classmethod
	def _encryptoForCookie(cls, value):
		return UcfUtil.enCrypto(str(value), UcfConfig.COOKIE_CRYPTOGRAPIC_KEY)

	# クッキーの値を取得（なければNone）
	@classmethod
	def getCookie(cls, name, with_enc=False):
		raw_value = request.cookies.get(name, None)
		if with_enc and raw_value is not None:
			# 復号化
			try:
				value = cls._decryptoForCookie(UcfUtil.urlDecode(raw_value))
			except Exception as e:
				logging.exception(e)
				value = raw_value
			return value
		else:
			return raw_value

	# SSOGadget対応：SAML連携設定を取得
	def getSamlSettings(self, tenant_or_domain, domain_row):
		return sateraito_func.getSamlSettings(sateraito_func.getMySiteURL(tenant_or_domain, self.request.url), tenant_or_domain, domain_row.sso_entity_id, domain_row.sso_login_endpoint, domain_row.sso_public_key)

	# 2020.06.26 新Googleサイト用添付ファイル対応
	# クエリパラメータuse_iframe_dlを見て必要ならiframeを埋め込んだhtml文をレスポンスする関数
	def showIFrameIfParamIsSet(self):
		use_iframe_dl = sateraito_func.strToBool(self.request.get('use_iframe_dl'))
		logging.debug('use_iframe_dl=' + str(use_iframe_dl))
		if use_iframe_dl:
			# get user language
			hl = self.request.get('hl')
			user_language = sateraito_func.getUserLanguage(self.viewer_email, hl=hl)
			my_lang = sateraito_func.MyLang(user_language)
			# export iframe html
			iframe_src = str(self.request.url).replace('&use_iframe_dl=true', '').replace('&use_iframe_dl=1', '')
			message = my_lang.getMsg('DOWNLOADING')
			ret_contents = '''<html>
													<head>
														<title>{message}</title>
													</head>
													<body>{message}<iframe id="dummy_frame" style="width:0px;height:0px;display:none;" src="{iframe_src}"></iframe>
													</body>
												</html>
												'''.format(message=message,iframe_src=iframe_src)
			return True, ret_contents
		return False, ''

	# 2020.06.26 新Googleサイト用添付ファイル対応
	# クエリパラメータfile_downloaded_tokenを見てトークンをレスポンスクッキーにセットする関数
	def setCookieFileDownloadTokenFromParam(self):
		file_downloaded_token = self.request.get('file_downloaded_token')
		if file_downloaded_token is not None and file_downloaded_token != '':
			self.setCookie('file_downloaded_token', str(file_downloaded_token))

	def checkAllowedIPAddressToDownload(self, other_setting=None):
		""" check IP address by OtherSetting
		"""
		if other_setting is None:
			other_setting = sateraito_db.OtherSetting.getInstance()
		access_ip_address_list = other_setting.access_ip_address_to_download_new
		# edit at 2020.12.30 By t.ASAO
		if access_ip_address_list is not None and len(access_ip_address_list) > 0:
			ok_access_ip_address = sateraito_func.CheckIpAddressAccess().run(self.request, access_ip_address_list)
			if ok_access_ip_address is False:
				logging.info('Ip is not access')
				return False
		return True

	# ログイン処理後、self.viewer_emailがGoogleAppsUserEntryに存在しなかった場合、GoogleAppsUserEntryを追加する
	# self.viewr_emailのドメインがtenant_or_domainと違う場合、DirectoryAPIをコールしてユーザーの存在確認をしてから追加する
	def createUserEntryIfNotExist(self, tenant_or_domain, app_id):
		# GoogleAppsUserEntry
		row_u = None

		# check domain: raise error for another domain user
		viewer_email_domain = sateraito_func.getDomainPart(self.viewer_email)
		logging.debug('** viewer_email_domain=' + str(viewer_email_domain))
		domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)

		if viewer_email_domain == 'gmail.com':
			if domain_row.is_ssite_tenant:
				# ssiteテナントの場合はOK
				pass
			else:
				# he is NOT subdomain user: raise error
				logging.error('gmail user cannot use')
				self.response.out.write('wrong request')
				self.response.set_status(403)
				return False

		if viewer_email_domain != tenant_or_domain:
			# sub-domain user?
			if not sateraito_func.isCompatibleDomain(tenant_or_domain, viewer_email_domain):  # ワークフローはこっち
				logging.info('unmatched Google Workspace domain and login user')
				# check GoogleAppsUserEntry exists
				row_u = sateraito_db.GoogleAppsUserEntry.getInstance(tenant_or_domain, self.viewer_email)
				if row_u is None:
					# GoogleAppsUserEntry NOT exists --> Check he is sub-domain user by getting info using impersonating_user setting

					directory_service = sateraito_func.get_directory_service(self.viewer_email, tenant_or_domain)
					user_found = False
					try:
						user_entry = directory_service.users().get(userKey=self.viewer_email).execute()
					except errors.HttpError as e:
						logging.info('class name:' + e.__class__.__name__ + ' message=' + str(e))
						user_found = False
					else:
						# user found: register new GoogleAppsUserEntry
						if user_entry is not None:
							logging.info('user successfully get by impersonate_mail: ' + str(self.viewer_email) + ' is subdomain user: user_entry=' + str(user_entry))
							user_found = True
							# register new GoogleAppsUserEntry
							checker = sateraito_func.RequestChecker()
							is_admin = False
							try:
								is_admin = checker.checkAppsAdmin(self.viewer_email, tenant_or_domain)  # ※ここでセットするドメインはnamespaceのドメイン（それによってOAuth2かどうかを判定するので）
								logging.debug('is_admin=' + str(is_admin))
							except Exception as instance:
								logging.error(instance)
							# add new GoogleAppsUserEntry
							logging.info('registering new GoogleAppsUserEntry')
							row_u = checker.putNewUserEntry(
								self.viewer_email,
								sateraito_func.getDomainPart(self.viewer_email),
								'__not_set',
								sateraito_func.OPENSOCIAL_CONTAINER_GOOGLE_SITE,
								self.viewer_user_id,
								is_admin
							)
						else:
							user_found = False

					if not user_found:
						# he is NOT subdomain user: raise error
						logging.error('unmatched Google Workspace domain and login user')
						self.response.out.write('wrong request')
						self.response.set_status(403)
						return False

		# add GoogleAppsUserEntry if not exist
		if row_u is None:
			row_u = sateraito_db.GoogleAppsUserEntry.getInstance(tenant_or_domain, self.viewer_email)
			if row_u is None:
				# register new GoogleAppsUserEntry
				checker = sateraito_func.RequestChecker()
				is_admin = False
				try:
					is_admin = checker.checkAppsAdmin(self.viewer_email, tenant_or_domain)  # ※ここでセットするドメインはnamespaceのドメイン（それによってOAuth2かどうかを判定するので）
					logging.debug('is_admin=' + str(is_admin))
				except Exception as instance:
					logging.error(instance)
				# add new GoogleAppsUserEntry
				logging.info('registering new GoogleAppsUserEntry')
				row_u = checker.putNewUserEntry(
					self.viewer_email,
					sateraito_func.getDomainPart(self.viewer_email),
					self.viewer_id if self.viewer_id is not None and self.viewer_id != '' else '__not_set',
					sateraito_func.OPENSOCIAL_CONTAINER_GOOGLE_SITE,
					self.viewer_user_id,
					is_admin
				)

		return row_u

	def checkClientSideViewerEmail(self):
		# 同一ブラウザで、ユーザーをログアウト／ログインして切り替えて使っているケースの問題
		# 別タブで新規作成画面を開いたままユーザーを切り替え、もとのタブに戻ってきて
		# 開いたままの新規作成画面を申請すると、申請書を別ユーザーで申請できてしまう
		# それを阻止するためクライアント側JavaScriptでのLoginMgr.viewerEmailとユーザーセッション上のself.viewer_emailをつきあわせ
		# 違っていたら申請や下書き保存をエラーとする

		# check client side viewer email
		client_side_viewer_email = self.request.get('client_side_viewer_email')
		logging.info('client_side_viewer_email=' + str(client_side_viewer_email))
		if client_side_viewer_email is not None and client_side_viewer_email != '':
			if self.viewer_email != client_side_viewer_email:
				# エラーにする
				jsondata = json.JSONEncoder().encode({'status': 'error', 'error_code': 'viewer_email_not_match'})
				self.response.out.write(jsondata)
				# jsondata = None
				return False
		return True

	@classmethod
	def createContentDisposition(cls, filename, type='attachment'):
		return (_CONTENT_DISPOSITION_FORMAT % (type, filename))

	@classmethod
	def createContentDispositionUtf8(cls, filename, type='attachment'):
		return (_CONTENT_DISPOSITION_FORMAT_UTF8 % (type, urllib.parse.quote(filename)))

	@classmethod
	def send_blob_file(cls, send_blob, blob_key, save_as=None, content_type=None, options={}):
		logging.debug('==========send_blob_file==============')
		try:
			if save_as:
				blob_info = blobstore.get(blob_key)
				if not blob_info:
					return "File not found", 404
				headers = send_blob(request.environ, blob_info, content_type=content_type, save_as=save_as)
			else:
				headers = send_blob(request.environ, blob_key, content_type=content_type)
			# add more property header
			for k, v in options.items():
				headers[k] = v
			return "", headers
		except Exception as e:
			return make_response(e, 500)

	@classmethod
	def setResponseHeaderForDownload(cls, file_name, mime_type=None, type='attachment'):
		if mime_type:
			cls.setResponseHeader('Content-Type', str(mime_type) + '; charset=utf-8')
		cls.setResponseHeader('Content-Disposition', "{0}; filename*=UTF-8''".format(type) + urllib.parse.quote(file_name))

	@classmethod
	def get_file_uploads(self, self_page, field_name=None):
		logging.debug('========get_file_uploads=========')
		# GAEGEN2対応：BlobStore経由のファイルアップロード対応
		# Blobstoreからのファイル取得. request.form、request.get_data() などの前に↓を実施する必要がある
		envDummy = request.environ.copy()
		envDummy['wsgi.input'] = io.BytesIO(self_page.get_data)
		return self_page.get_uploads(envDummy, field_name=field_name)

	# セッション取得
	# @classmethod
	def getSession(self, key, default=None):
		# flask_sessionライブラリをカスタマイズしてnamespaceをセットするようにしたのでここでのnamespace処理は不要
		# → gaesessionsを使ったDB版の場合は必要
		value = session.get(key, default)
		logging.debug('getsession key=%s value=%s' % (key, value))
		return value

	# セッションに値セット
	# @classmethod
	def setSession(cls, key, value):
		# flask_sessionライブラリをカスタマイズしてnamespaceをセットするようにしたのでここでのnamespace処理は不要
		# → gaesessionsを使ったDB版の場合は必要
		session[key] = value
		logging.debug('setsession key=%s value=%s' % (key, value))


class _BaseAPI(_BasePage):
	def __init__(self, *args, **kwargs):
		super(_BaseAPI, self).__init__()

	def responseUnauthorized(self, message=None):
		if message is None:
			message = 'Unauthorized'

		self.response.status = 401
		self.setResponseHeader('Content-Type', 'application/json; charset=utf-8')

		json_data = {'status': 'error', 'error_code': 'unauthorized', 'message': message}
		return json_data

	def responseForbidden(self, message=None):
		if message is None:
			message = 'Forbidden'

		self.response.status = 403
		self.setResponseHeader('Content-Type', 'application/json; charset=utf-8')

		json_data = {'status': 'error', 'error_code': 'forbidden', 'message': message}
		return json_data

	def responseDataSuccess(self, json_data=None):

		self.response.status = 200
		self.setResponseHeader('Content-Type', 'application/json; charset=utf-8')

		if json_data is None:
			json_data = {}

		return json_data

	def responseBadRequest(self, message=None):
		if message is None:
			message = 'Bad Request'

		self.response.status = 400
		self.setResponseHeader('Content-Type', 'application/json; charset=utf-8')

		json_data = {'status': 'error', 'error_code': 'bad_request', 'message': message}
		return json_data

	def responseDataError(self, error_code=None, message=None):

		if error_code is None:
			error_code = 'error'

		self.response.status = 500
		self.setResponseHeader('Content-Type', 'application/json; charset=utf-8')

		json_data = {'status': 'error', 'error_code': error_code, 'message': message}
		return json_data


class BlobFileInfo():
	def __init__(self, file_storage):
		self._file_storage = file_storage

	def name(self):
		if self._file_storage is None:
			return None
		return self._file_storage.name

	def key(self):
		if self._file_storage is None:
			return None
		if 'blob-key' in self._file_storage.mimetype_params:
			return self._file_storage.mimetype_params.get('blob-key', None)
		return None

	def getFile(self):
		return self._file_storage

	def getBlob(self):
		key = self.key()
		if key is None:
			return None
		return blobstore.BlobInfo.get(key)


class _OidBasePage(_BasePage):

	#	viewer_email = None
	#	viewer_user_id = None

	def removeOEqualKm(self, query_string):
		return removeItemFromQueryString(query_string, 'o=km')

	def isOidLoggedIn(self):
		# check openid login
		user = users.get_current_user()
		if user is None:
			# not oid logged in
			return False
		return True

	# ※ガジェット外での新規申請機能対応：add_querys引数追加 2016.03.04
	# モバイル版でログアウト直後のログイン時にG Suite側のアカウント選択画面を出すことで自動再ログインを防ぐ 2020.02.21
	def oidAutoLogin(self, google_apps_domain, is_multi_domain=False, true_redirecting=False, kozukasan_method=False,
										kozukasan_redirect_to=None, skip_domain_compatibility=False, with_error_page=False,
										with_none_prompt=False, with_select_account_prompt=False, is_force_auth=False, hl=None,
										add_querys=None):
		"""
		Returns
			is_ok: boolean
				True .. user already logged in
				False .. user not logged in, processing oid login
			body_for_not_ok: str
				html or plain text data to respond if not ok case
		"""

		# SSITE対応…GoogleAppsDomainEntryからSSITEのドメイン（テナント）かを判定 2016.08.24
		if sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
			return self._OIDCAutoLoginForSSite(google_apps_domain, skip_domain_compatibility=skip_domain_compatibility,
																					with_error_page=with_error_page, with_none_prompt=with_none_prompt,
																					is_force_auth=is_force_auth, hl=hl, add_querys=add_querys)
		# SSOGadget対応
		elif sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain):
			return self._OIDCAutoLoginForSSOGadget(google_apps_domain, skip_domain_compatibility=skip_domain_compatibility,
																							with_error_page=with_error_page, with_none_prompt=with_none_prompt,
																							is_force_auth=is_force_auth, hl=hl, add_querys=add_querys)
		# Apps
		else:
			return self._OIDCAutoLogin(google_apps_domain, skip_domain_compatibility=skip_domain_compatibility,
																	with_error_page=with_error_page, with_none_prompt=with_none_prompt,
																	with_select_account_prompt=with_select_account_prompt, is_force_auth=is_force_auth,
																	hl=hl, add_querys=add_querys)

	def _OIDCAutoLogin(self, google_apps_domain, skip_domain_compatibility=False, with_error_page=False,
											error_page_url='', with_none_prompt=False, with_select_account_prompt=False,
											with_admin_consent=False, with_regist_user_entry=False, is_force_auth=False, hl=None,
											url_to_go_after_oidc_login=None, add_querys=None, prompt_type=None):
		"""
		Returns
			is_ok: boolean
				True .. user already logged in
				False .. user not logged in, processing oid login
			body_for_not_ok: str
				html or plain text data to respond if not ok case
		"""

		if prompt_type == 'select_account':
			logging.info('force remove auth sessions...')
			self.session['viewer_email'] = ''
			self.session['loggedin_timestamp'] = None  # G Suiteのマルチログイン時にiframe内でOIDC認証ができなくなったので強制で少しだけ高速化オプションする対応＆SameSite対応 2019.10.28
			self.session['opensocial_viewer_id'] = ''
			self.session['is_oidc_loggedin'] = False
			self.session['is_oidc_need_show_signin_link'] = False
			self.removeAppsCookie()

		# 強制的に再認証をさせるためセッションを破棄（CookieのセッションIDの破棄ではなくセッションの値をそれぞれ個別に破棄） 2016.05.27
		if is_force_auth:
			# G Suiteのマルチログイン時にiframe内でOIDC認証ができなくなったので強制で少しだけ高速化オプションする対応 2019.10.28
			# SameSite対応…SameSite対応でもどっちにしてもこの対応は必要　→　強制高速化オプションを強制するようになったのでSameSite対応のためには不要
			loggedin_timestamp = self.session.get('loggedin_timestamp')
			# GAE Gen2対応
			if isinstance(loggedin_timestamp, str):
				loggedin_timestamp = dateutil.parser.parse(loggedin_timestamp)

			if loggedin_timestamp is None or loggedin_timestamp < UcfUtil.add_minutes(datetime.datetime.now(), -5):
				logging.info('force remove auth sessions...')
				self.session['viewer_email'] = ''
				self.session['loggedin_timestamp'] = None  # G Suiteのマルチログイン時にiframe内でOIDC認証ができなくなったので強制で少しだけ高速化オプションする対応＆SameSite対応 2019.10.28
				self.session['opensocial_viewer_id'] = ''
				self.session['is_oidc_loggedin'] = False
				self.session['is_oidc_need_show_signin_link'] = False

		# check openid connect login
		viewer_email = self.session.get('viewer_email')
		logging.info('viewer_email=' + str(viewer_email))
		opensocial_viewer_id = self.session.get('opensocial_viewer_id')
		logging.info('opensocial_viewer_id=' + str(opensocial_viewer_id))
		is_oidc_loggedin = self.session.get('is_oidc_loggedin')
		logging.info('is_oidc_loggedin=' + str(is_oidc_loggedin))
		is_oidc_need_show_signin_link = self.session.get('is_oidc_need_show_signin_link')
		logging.info('is_oidc_need_show_signin_link=' + str(is_oidc_need_show_signin_link))

		# エラーが返る場合は画面上に「認証する」を出すためにFalseを返す 2016.04.03
		if with_none_prompt and is_oidc_need_show_signin_link:
			return False, ''

		logging.info('_OIDCAutoLogin viewer_email=' + str(viewer_email))
		if is_oidc_loggedin is None or not is_oidc_loggedin or viewer_email is None or viewer_email == '':

			# iOSのX-Frame-Options:Deny対策…iOS、iPadOS、MacのSafari、FireFox、セキュリティブラウザの場合は認証するリンクからポップアップで認証する（Chromeは今のところ一応除外） 2021.04.15
			strAgent = self.request.headers.get('User-Agent', '').lower()
			logging.info('strAgent=' + str(strAgent))
			
			if with_none_prompt and strAgent.find('Macintosh;'.lower()) >= 0 and strAgent.find('/SateraitoSecurityBrowser'.lower()) >= 0:
				self.session['is_oidc_need_show_signin_link'] = True
				return False, ''
			# その他OSのFireFoxも追加（FireFoxESRという特殊なブラウザでブロックされるようになったため） 2021.04.28
			elif with_none_prompt and strAgent.find('FireFox'.lower()) >= 0:
				self.session['is_oidc_need_show_signin_link'] = True
				return False, ''

			# go login

			info = ''
			if with_error_page:
				info += '&wep=1&hl=' + sateraito_func.getActiveLanguage('', hl=hl)
			if with_admin_consent:
				info += '&wac=1'
			if with_regist_user_entry:
				info += '&wrue=1'

			# iOS13サードパーティーCookieブロック対策…テナント、ドメインを渡す 2019.09.26
			info += '&t=' + google_apps_domain

			info = info.lstrip('&')
			state = 'state-' + ((UcfUtil.base64Encode(info) + '-') if info != '' else '') + sateraito_func.dateString() + sateraito_func.randomString()

			logging.info('state=' + state)
			self.session['state'] = state
			# セッションでもいいのだがタイムラグが気になるのでCookieにする
			expires = UcfUtil.add_hours(UcfUtil.getNow(), 1).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
			self.setCookie('oidc_state', str(state), expires=expires)

			# 認証後にもどってくる用URLを設定	※ガジェット外での新規申請機能対応　2016.03.04
			# G Suite 版申込ページ対応…戻りURL指定対応 2017.06.05
			if url_to_go_after_oidc_login is None or url_to_go_after_oidc_login == '':
				url_to_go_after_oidc_login = self.request.url
			if add_querys is not None:
				for add_query in add_querys:
					url_to_go_after_oidc_login = UcfUtil.appendQueryString(url_to_go_after_oidc_login, add_query[0], add_query[1])
			self.session['url_to_go_after_oidc_login'] = url_to_go_after_oidc_login

			# for 'multiple iframe gadget in a page' case login
			self.setCookie(urllib.parse.quote(state), str(url_to_go_after_oidc_login), living_sec=30)

			# G Suite 版申込ページ対応…エラーページ対応 2017.06.05
			if with_error_page:
				self.setCookie(urllib.parse.quote(state + '-ep'), str(error_page_url), living_sec=300)

			# G Suite 版申込ページ対応…管理者チェック時はAdminSDKを含むスコープを指定 2017.06.05
			# Google+API、Scope廃止対応 2019.02.01
			scope = ['openid', 'email']
			if with_admin_consent:
				scope = sateraito_inc.OAUTH2_SCOPES
			dictParam = dict(
				scope=scope,  # G Suite 版申込ページ対応 2017.06.05
				redirect_uri=sateraito_func.getMySiteURL(google_apps_domain, self.request.url) + '/oidccallback',
				state=state,
				openid_realm=sateraito_func.getMySiteURL(google_apps_domain, self.request.url),
				access_type='online'
			)

			if with_none_prompt:
				# GAE Gen2対応
				dictParam['prompt'] = 'none'
			elif with_select_account_prompt:
				# GAE Gen2対応
				dictParam['prompt'] = 'select_account'

			# GAE Gen2対応
			client = WebApplicationClient(sateraito_inc.WEBAPP_CLIENT_ID)
			auth_uri = client.prepare_request_uri('https://accounts.google.com/o/oauth2/auth', **dictParam)

			logging.info('auth_uri=' + str(auth_uri))

			user_agent = str(self.request.headers.get('User-Agent'))
			logging.debug('** _OIDCAutoLogin user_agent=' + str(user_agent))
			is_opened_from_msoffice = False
			if 'ms-office' in user_agent and 'MSIE' in user_agent:
				is_opened_from_msoffice = True

			# go jump or redirect
			if is_opened_from_msoffice:
				logging.info('url opened by msoffice link click. jumping by html meta tag...')
				ret_datas = []
				ret_datas.append('<html><head>')
				ret_datas.append('<meta http-equiv="refresh" content="1;URL=' + str(auth_uri) + '">')
				ret_datas.append('</head><body></body></html>')
				return False, ''.join(ret_datas)
			else:
				self.redirect(auth_uri)
				return False, auth_uri

		# check domain
		viewer_email_domain = sateraito_func.getDomainPart(viewer_email)
		if viewer_email_domain != google_apps_domain:
			if not skip_domain_compatibility:
				if not sateraito_func.isCompatibleDomain(google_apps_domain, viewer_email_domain):
					logging.warning('unmatched google apps domain and login user')
					self.response.set_status(403)
					return False, 'wrong request'

		self.viewer_email = str(viewer_email).lower()
		self.viewer_id = str(opensocial_viewer_id)
		logging.info('self.viewer_email=' + self.viewer_email)
		logging.info('auth result=True')
		return True, ''

	# サテライトサイト用のOIDC認証
	def _OIDCAutoLoginForSSite(self, google_apps_domain, skip_domain_compatibility=False, with_error_page=False,
															with_none_prompt=False, is_force_auth=False, hl=None, add_querys=None):
		"""
		Returns
			is_ok: boolean
				True .. user already logged in
				False .. user not logged in, processing oid login
			body_for_not_ok: str
				html or plain text data to respond if not ok case
		"""

		# 強制的に再認証をさせるためセッションを破棄（CookieのセッションIDの破棄ではなくセッションの値をそれぞれ個別に破棄） 2016.05.27
		if is_force_auth:
			logging.info('force remove auth sessions...')
			self.session['viewer_email'] = ''
			self.session['opensocial_viewer_id'] = ''
			self.session['is_oidc_loggedin'] = False
			self.session['is_oidc_need_show_signin_link'] = False

		# check openid connect login
		viewer_email = self.session.get('viewer_email')
		logging.info('viewer_email=' + str(viewer_email))
		opensocial_viewer_id = self.session.get('opensocial_viewer_id')
		logging.info('opensocial_viewer_id=' + str(opensocial_viewer_id))
		is_oidc_loggedin = self.session.get('is_oidc_loggedin')
		logging.info('is_oidc_loggedin=' + str(is_oidc_loggedin))
		is_oidc_need_show_signin_link = self.session.get('is_oidc_need_show_signin_link')
		logging.info('is_oidc_need_show_signin_link=' + str(is_oidc_need_show_signin_link))

		# エラーが返る場合は画面上に「認証する」を出すためにFalseを返す 2016.04.03
		if with_none_prompt and is_oidc_need_show_signin_link:
			# return False  # g2対応
			return False, ''

		logging.info('_OIDCAutoLoginForSSite viewer_email=' + str(viewer_email))
		if is_oidc_loggedin is None or not is_oidc_loggedin or viewer_email is None or viewer_email == '':
			# go login

			# サードパーティCookie無効時に403ではなくメッセージを出す対応（stateに情報を含めてoidccallback側で制御）
			if with_error_page:
				info = 'wep=1&hl=' + sateraito_func.getActiveLanguage('', hl=hl)
				info_base64 = UcfUtil.base64Encode(info)
				state = 'state-' + info_base64 + '-' + sateraito_func.dateString() + sateraito_func.randomString()
			else:
				state = 'state-' + sateraito_func.dateString() + sateraito_func.randomString()
			logging.info('state=' + state)
			# セッションでもいいのだがタイムラグが気になるのでCookieにする
			expires = UcfUtil.add_hours(UcfUtil.getNow(), 1).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
			self.setCookie('oidc_state', str(state), expires=expires)

			# 認証後にもどってくる用URLを設定	※ガジェット外での新規申請機能対応　2016.03.04
			url_to_go_after_oidc_login = self.request.url
			if add_querys is not None:
				for add_query in add_querys:
					url_to_go_after_oidc_login = UcfUtil.appendQueryString(url_to_go_after_oidc_login, add_query[0], add_query[1])

			# セッションでもいいのだがタイムラグが気になるのでCookieにする
			self.setCookie(urllib.parse.quote(state), str(url_to_go_after_oidc_login), expires=expires)

			query_params = {}
			query_params['state'] = state
			# OIDCセキュリティ強化対応：nonceチェックを導入 2016.12.08
			nonce = UcfUtil.guid()
			self.session['nonce-' + state] = nonce
			query_params['nonce'] = nonce
			query_params['response_type'] = 'code id_token'
			query_params['client_id'] = sateraito_inc.SSITE_OIDC_CLIENT_ID
			query_params['redirect_uri'] = sateraito_inc.custom_domain_my_site_url + '/ssite/oidccallback'
			query_params['scope'] = 'openid'
			query_params['client_tenant'] = google_apps_domain  # SSITE独自クレーム. クライアント（アドオン）側のドメインをセット
			if with_none_prompt:
				query_params['prompt'] = 'none'
			else:
				query_params['prompt'] = 'login'
			tenant_id = sateraito_db.GoogleAppsDomainEntry.getSSiteTenantID(google_apps_domain)  # SSITEのテナントID
			url_to_go = sateraito_inc.SSITE_ROOT_URL + '/' + tenant_id + '/oauth2/authorize?' + urllib.parse.urlencode(query_params)
			auth_uri = str(url_to_go)
			logging.info('auth_uri=' + auth_uri)

			user_agent = str(self.request.headers.get('User-Agent'))
			is_opened_from_msoffice = False
			if 'ms-office' in user_agent and 'MSIE' in user_agent:
				is_opened_from_msoffice = True

			# go jump or redirect
			if is_opened_from_msoffice:
				logging.info('url opened by msoffice link click. jumping by html meta tag...')
				ret_datas = []
				ret_datas.append('<html><head>')
				ret_datas.append('<meta http-equiv="refresh" content="1;URL=' + str(auth_uri) + '">')
				ret_datas.append('</head><body></body></html>')
				return False, ''.join(ret_datas)
			else:
				self.redirect(auth_uri)
				return False, ''

		# check domain
		viewer_email_domain = sateraito_func.getDomainPart(viewer_email)
		if viewer_email_domain != google_apps_domain:
			if not skip_domain_compatibility:
				if not sateraito_func.isCompatibleDomain(google_apps_domain, viewer_email_domain):
					logging.warning('unmatched google apps domain and login user')
					self.response.set_status(403)
					return False, 'wrong request'

		self.viewer_email = str(viewer_email).lower()
		self.viewer_email_raw = str(viewer_email)
		self.viewer_user_id = str(opensocial_viewer_id)
		self.viewer_id = str(opensocial_viewer_id)
		self.mode = sateraito_func.MODE_SSITE
		return True, ''

	# SSOGadget対応：SSOとのSAML2.0認証 2017.01.10
	def _OIDCAutoLoginForSSOGadget(self, tenant_or_domain, skip_domain_compatibility=False, with_error_page=False,
																	with_none_prompt=False, is_force_auth=False, hl=None, add_querys=None):
		"""
		Returns
			is_ok: boolean
				True .. user already logged in
				False .. user not logged in, processing oid login
			body_for_not_ok: str
				html or plain text data to respond if not ok case
		"""

		# 強制的に際認証をさせるためセッションを破棄（CookieのセッションIDの破棄ではなくセッションの値をそれぞれ個別に破棄） 2016.05.27
		if is_force_auth:
			logging.info('force remove auth sessions...')
			self.session['viewer_email'] = ''
			self.session['is_admin'] = False
			self.session['opensocial_viewer_id'] = ''
			self.session['is_oidc_loggedin'] = False

		# check openid connect login
		viewer_email = self.session.get('viewer_email')
		logging.info('viewer_email=' + str(viewer_email))
		opensocial_viewer_id = self.session.get('opensocial_viewer_id')
		logging.info('opensocial_viewer_id=' + str(opensocial_viewer_id))
		is_admin = sateraito_func.noneToFalse(self.session.get('is_admin'))
		logging.info('is_admin=' + str(is_admin))

		domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
		logging.info('_OIDCAutoLoginForSSOGadget viewer_email=' + str(viewer_email))
		if viewer_email is None or viewer_email == '':
			# go login
			# シングルサインオンとのSAML連携
			samlsettings = self.getSamlSettings(tenant_or_domain, domain_row)
			saml_request = SamlAuthnRequest(samlsettings, force_authn=False, is_passive=False, set_nameid_policy=True)
			saml_request.redirect_to_idp(self, relay_state=self.request.url)
			return False, ''

		# check domain
		viewer_email_domain = sateraito_func.getDomainPart(viewer_email)
		if viewer_email_domain != tenant_or_domain:
			if not skip_domain_compatibility:
				if not sateraito_func.isCompatibleDomain(tenant_or_domain, viewer_email_domain):
					logging.warning('unmatched google apps domain and login user')
					self.response.set_status(403)
					return False, 'wrong request'

		self.viewer_email = str(viewer_email).lower()
		self.viewer_email_raw = str(viewer_email)
		self.viewer_user_id = opensocial_viewer_id
		self.viewer_id = opensocial_viewer_id
		# self.is_admin = is_admin
		self.mode = sateraito_func.MODE_SSOGADGET
		return True, ''


# SharePointガジェットの認証
# class _AuthSharePointGadget(webapp2.RequestHandler):
class _AuthSharePointGadget(Handler_Basic_Request, _BasePage):
	# 変数初期化
	_tenant = ''
	_tenant_id = ''
	_auth_url = ''
	_host_name = ''
	_sp_principal_id = ''
	_reflesh_token = ''
	_reflesh_token_expire = 0
	_site_url = ''
	_oauth_client_id = ''
	_oauth_client_secret = ''
	_token_type = ''
	_access_token = ''
	_access_token_expire = 0
	_app_principal_id = ''
	_authorization = ''
	_accept_encoding = ''
	_site_collection_host_name = ''
	_current_user_mail_address = ''
	_current_user_name_id = ''
	_current_user_is_admin = False

	# OpenIDのかわりに印刷ウインドウなどで認証に使うCookieをセット（有効期限…とりあえず1日）
	def setTokenToCookie(self, token):
		name = 'auth_token'
		value = str(token)
		expires = UcfUtil.add_days(UcfUtil.getNow(), 1).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
		path = '/'
		domain = ''
		secure = 'secure'  # 'secure'
		# SameSite対応 2019.10.12（secure属性必須）
		# self.response.headers.add_header('Set-Cookie', str(name) + '=' + value + ';' + 'expires=' + str(expires) + ';' + 'Path=' + str(path) + ';' + (('domain=' + str(domain) + ';') if domain != '' else '') + secure)
		if sateraito_func.isSameSiteCookieSupportedUA(self.request.headers.get('User-Agent')):
			self.response.headers.add_header('Set-Cookie', str(name) + '=' + value + ';' + 'expires=' + str(expires) + ';SameSite=None;' + 'Path=' + str(path) + ';' + (('domain=' + str(domain) + ';') if domain != '' else '') + secure)
		else:
			self.response.headers.add_header('Set-Cookie', str(name) + '=' + value + ';' + 'expires=' + str(expires) + ';' + 'Path=' + str(path) + ';' + (('domain=' + str(domain) + ';') if domain != '' else '') + secure)

	def _authSharePointGadget(self):

		if sateraito_inc.developer_mode:
			self._tenant = 'nextsetdemo'
			self._host_name = 'http://nextsetdemo.sharepoint.com'
			if self.request.get('uf') == 'user':
				self._current_user_mail_address = 'yoshida@nextsetdemo.onmicrosoft.com'
				self._current_user_name_id = '22222222222222222'
				self._current_user_is_admin = False
			else:
				self._current_user_mail_address = 'kuroda@nextsetdemo.onmicrosoft.com'
				self._current_user_name_id = '1234567890123457'
				self._current_user_is_admin = True
			return True

		# RequestパラメータにSPAppToken が存在したら次の処理
		valSPAppToken = self.request.get("SPAppToken")
		if valSPAppToken == None or valSPAppToken == '':
			self.response.out.write("No Token<br><br>")
			logging.error('No Token')
			return False
		else:
			logging.debug('valSPAppToken=' + valSPAppToken)
			self.DecodeSPAppToken(valSPAppToken)
			if self._tenant is None or self._tenant == '':
				self.response.out.write("Invalid Tenant<br><br>")
				logging.error('Invalid Tenant')
				return False
			self.getApplicationInfo()
			self.getAccessControl()
			self.getOAuthAccessToken()
			self.getCurrentUser()

		if self._current_user_mail_address == '':
			self.response.out.write("Failed get authed email address.<br><br>")
			logging.error('Failed get authed email address.')
			return False

		# self.response.out.write("EMailAddress : " + self._current_user_mail_address)
		return True

	# SPAppTokenをBase64デコードしつつ必要な値取得
	def DecodeSPAppToken(self, SPAppToken):
		# リクエストの値をピリオドで分割した２個目の値をセット

		# SPAppTokenをピリオドで分割して２個目の値をベース64デコードしてJSON型にセット
		SPAppTokenEnc = SPAppToken.split(".")[1]
		if not SPAppTokenEnc.endswith('='):
			SPAppTokenEnc = SPAppTokenEnc + '=='
		SPAppTokenDec = base64.b64decode(SPAppTokenEnc)
		logging.debug(SPAppTokenDec)
		jdata = json.loads(SPAppTokenDec)

		logging.debug("--------------   SPAppToken Base64 Decode --------------")
		for jkey in jdata:
			logging.debug(jkey + " : " + str(jdata[jkey]) + "")
		logging.debug("--------------   Pincup Parameter --------------")

		# JSON型の変数から必要な項目をピックアップ
		# SharePointのプリンシパルID (appctxsenderの@で分割した左側)
		self._sp_principal_id = str(jdata["appctxsender"]).split("@")[0]
		# Host名
		self._host_name = str(self.request.get("SPSiteUrl").split("/")[2])
		# Host名からテナント名を取得（Host名=サイトコレクションのURLだが、Publicページじゃない限りはカスタムURLにはできないのでここから取得してOK）
		self._tenant = self._host_name.replace('http://', '').replace('https://', '').split('.')[0].lower()
		# テナントID (appctxsenderの@で分割した右側)
		self._tenant_id = str(jdata["appctxsender"]).split("@")[1]
		# サイトコレクションのURL
		# 全角（unicode）のURLもあるので
		# self.strSiteCollectionName = str(self.request.get("SPHostUrl"))
		self.strSiteCollectionName = self.request.get("SPHostUrl")
		# リフレッシュトークン(B64値)
		self._reflesh_token = str(jdata["refreshtoken"])
		# リフレッシュトークンの有効期限
		self._reflesh_token_expire = int(jdata["exp"])
		# アプリのプリンシパルID
		self._app_principal_id = str(jdata["aud"]).split("/")[0]

		logging.debug("Principal ID : " + self._sp_principal_id + "")
		logging.debug("Local URL : " + self._host_name + "")
		logging.debug("Tenant Name : " + self._tenant + "")
		logging.debug("Tenant ID : " + self._tenant_id + "")
		logging.debug("SiteCollection URL : " + self.strSiteCollectionName + "")
		logging.debug("Reflesh Token : " + self._reflesh_token + "")
		logging.debug("Reflesh Token Expire: " + str(self._reflesh_token_expire) + "")
		logging.debug("Client ID : " + self._oauth_client_id + "")
		logging.debug("Client Secret : " + self._oauth_client_secret + "")
		logging.debug("Apprication Principal ID : " + self._app_principal_id + "")

	# 管理者がセットしておいたOAuth関連情報を取得
	def getApplicationInfo(self):
		row = sateraito_db.ApplicationEntry.getInstanceByClientId(self._app_principal_id)
		if row is not None:
			# クライアントID（=プリンシパルID）
			self._oauth_client_id = row.client_id
			# クライアントシークレット
			self._oauth_client_secret = row.client_secret
		else:
			# raise BaseException, 'Not ready.'
			raise Exception('Not ready.')

	# OAuth認証用URLを取得
	def getAccessControl(self):

		# URLFetch せずにURLを固定で作成するように変更
		self._auth_url = 'https://accounts.accesscontrol.windows.net/' + self._tenant_id + '/tokens/OAuth/2'
		logging.debug("_auth_url : " + self._auth_url)
		return

	# OAuthの認証
	def getOAuthAccessToken(self):

		memcache_key_access_token = 'oauth2_access_token?refresh_token=' + self._reflesh_token
		memcache_key_token_type = 'oauth2_token_type?refresh_token=' + self._reflesh_token

		# memcache からアクセストークンを取得するように対応（取得できなければ本来の処理）
		memcache_keys = [memcache_key_access_token, memcache_key_token_type]
		memcache_datas = memcache.get_multi(memcache_keys)

		access_token = memcache_datas.get(memcache_key_access_token)
		token_type = memcache_datas.get(memcache_key_token_type)
		if access_token is not None and token_type is not None:
			self._access_token = access_token
			self._token_type = token_type
			logging.debug("-------------- Get AccessToken by memcache --------------")
			logging.debug("_token_type : " + self._token_type + "")
			logging.debug("_access_token : " + self._access_token + "")
			return

		# POSTで対象URLにアクセスして情報取得
		# OAuthのURLをセット
		strUrl = self._auth_url
		# ポストする値をセット
		strValues = {	"grant_type": "refresh_token", "client_id": self._app_principal_id + "@" + self._tenant_id,
									"client_secret": self._oauth_client_secret, "refresh_token": self._reflesh_token,
									"resource": self._sp_principal_id + "/" + self._host_name + "@" + self._tenant_id}
		# 送信するヘッダーをセット
		strHeaders = {"Content-Type": "application/x-www-form-urlencoded", "Host": self._auth_url.split("/")[2],
									"Expect": "100-continue"}

		logging.debug("--------------   OAuth2 Request --------------")
		logging.debug("url : " + self._auth_url + "")

		logging.debug("--------------   OAuth2 Request Parameters --------------")
		for jkey in strValues:
			logging.debug(jkey + " : " + strValues[jkey] + "")

		logging.debug("--------------   OAuth2 Request Headers --------------")
		for jkey in strHeaders:
			logging.debug(jkey + " : " + strHeaders[jkey] + "")

		# OAuth認証
		logging.debug('url=' + strUrl)
		strReturn = HttpPostAccess(strUrl, strValues, strHeaders)

		logging.debug("--------------   OAuth2 Response Value --------------")
		logging.debug(strReturn)

		# レスポンスから必要項目を取得
		strJson = json.loads(strReturn)
		self._access_token = strJson["access_token"]
		self._token_type = strJson["token_type"]
		self._access_token_expire = int(strJson["expires_on"])

		logging.debug("--------------   Pincup Parameter --------------")
		logging.debug("_token_type : " + self._token_type + "")
		logging.debug("_access_token : " + self._access_token + "")
		logging.debug("_access_token_expire : " + str(self._access_token_expire) + "")

		# memcacheにアクセストークンをセット
		# リフレッシュトークンとアクセストークンの短いほう - 10分（保険的に）をmemcacheの期限とする
		expire_unixtime = self._access_token_expire if self._access_token_expire < self._reflesh_token_expire else self._reflesh_token_expire
		memcache_expire = int(expire_unixtime - time.mktime(datetime.datetime.now().timetuple()) - 600)
		logging.debug('memcache_expire : ' + str(memcache_expire))
		# datetime.datetime.fromtimestamp(unixtime)
		datas = {
			memcache_key_access_token: self._access_token,
			memcache_key_token_type: self._token_type
		}
		memcache.set_multi(datas, time=memcache_expire)
		logging.debug("Set access_token to memcache.")

	# SharePointから現在ログインしているユーザーを取得
	def getCurrentUser(self):
		# POSTで対象URLにアクセスして情報取得
		# strUrl = self.strSiteCollectionName + "/_vti_bin/client.svc/ProcessQuery"
		sp = self.strSiteCollectionName.split('/')
		strUrl = ''
		for i in range(len(sp)):
			v = sp[i]
			if i >= 3:  # FQDNより後ろを処理
				# 半角スペースが「+」に変換されるとエラーするので対応 2015.03.23
				# v = UcfUtil.urlEncode(v)
				v = UcfUtil.urlEncode(v, without_plus=True)
			strUrl += ('/' if i > 0 else '') + v
		strUrl = strUrl + "/_vti_bin/client.svc/ProcessQuery"

		# SharePoint上のデータを取得するクエリ（ログインしてるユーザー情報取得）をセット
		strValues = '<Request AddExpandoFieldTypeSuffix=\"true\" SchemaVersion=\"15.0.0.0\" LibraryVersion=\"15.0.0.0\" ApplicationName=\".NET Library\" xmlns=\"http://schemas.microsoft.com/sharepoint/clientquery/2009\"><Actions><ObjectPath Id=\"2\" ObjectPathId=\"1\" /><ObjectPath Id=\"4\" ObjectPathId=\"3\" /><Query Id=\"5\" ObjectPathId=\"3\"><Query SelectAllProperties=\"false\"><Properties><Property Name=\"CurrentUser\" SelectAll=\"true\"><Query SelectAllProperties=\"false\"><Properties /></Query></Property></Properties></Query></Query></Actions><ObjectPaths><StaticProperty Id=\"1\" TypeId=\"{3747adcd-a3c3-41b9-bfab-4a64dd2f1e0a}\" Name=\"Current\" /><Property Id=\"3\" ParentId=\"1\" Name=\"Web\" /></ObjectPaths></Request>'

		# ヘッダーをセット
		strHeaders = {"Authorization": self._token_type + " " + self._access_token, "Host": self._host_name,
									"Content-Type": "text/xml", "Expect": "100-continue", "Accept-Encoding": "gzip, deflate"}

		logging.debug("--------------   Get SharePoint Data --------------")
		logging.debug("url " + strUrl + "")

		logging.debug("--------------   Get SharePoint Data Request Parameters--------------")
		logging.debug("Payload : " + strValues.replace("<", "&lt;").replace(">", "&gt;") + "")

		logging.debug("--------------   Get SharePoint Data Request Headers--------------")
		for jkey in strHeaders:
			logging.debug(str(jkey) + " : " + str(strHeaders[str(jkey)]) + "")

		# SharePointサーバーからデータ取得
		logging.debug('strValues=' + str(strValues))
		logging.debug('strHeaders=' + str(strHeaders))
		result = HttpPostAccessRow(strUrl, strValues, strHeaders)

		logging.debug("--------------   Get SharePoint Data Response Headers --------------")

		logging.debug("http_status_code :" + str(result.status_code) + "")
		is_gzip = False
		for strKey in result.headers.keys():
			logging.debug(strKey + ":" + result.headers[strKey] + "")
			if strKey == 'content-encoding' and result.headers[strKey] == 'gzip':
				is_gzip = True
		logging.debug("--------------   Get SharePoint Data Response Data --------------")

		# 結果がgzipで圧縮されているので解凍
		# logging.debug(result.content)

		if is_gzip:
			# なぜかGZIPされてこないパターンがあるのでキャッチしてそのまま使う対応のまま、一応try、catchしておくが、is_gzipでちゃんと分岐できているはず
			try:
				# sf = StringIO.StringIO(result.content)  # g2対応result.contentはbytesのはずなので、io.BytesIOを使う
				sf = io.BytesIO(result.content)
				result_value = gzip.GzipFile(fileobj=sf).read()
			except IOError as e:
				logging.warning(e)
				result_value = result.content
		else:
			result_value = result.content

		# logging.debug(result_value)
		# クエリの結果からEメールアドレスを抽出
		logging.info('result_value=' + str(result_value))
		result_value_json = json.loads(result_value)

		for jdata_record in result_value_json:
			if isinstance(jdata_record, dict) and 'CurrentUser' in jdata_record:
				# example… {u'_ObjectType_': u'SP.Web', u'CurrentUser': {u'_ObjectType_': u'SP.User', u'LoginName': u'i:0#.f|membership|kuroda@nextsetdemo.onmicrosoft.com', u'IsSiteAdmin': False, u'Title': u'\u9ed2\u7530\u5b5d\u9ad8', u'_ObjectIdentity_': u'740c6a0b-85e2-48a0-a494-e0f1759d4aa7:site:d84a70cf-7afb-424a-af33-2625abf269f2:u:9', u'UserId': {u'_ObjectType_': u'SP.UserIdInfo', u'NameIdIssuer': u'urn:federation:microsoftonline', u'NameId': u'1003bffd85514b76'}, u'Email': u'kuroda@nextsetdemo.onmicrosoft.com', u'PrincipalType': 1, u'IsHiddenInUI': False, u'Id': 9}, u'_ObjectIdentity_': u'740c6a0b-85e2-48a0-a494-e0f1759d4aa7:site:d84a70cf-7afb-424a-af33-2625abf269f2:web:a2a0f6c2-2875-4fda-9fcc-9b64498bda5f'}
				current_user = jdata_record['CurrentUser']
				logging.debug(current_user)

				# Emailのほうは正しい認証アカウントが取得できない場合が発生したので、LoginNameを優先するように変更 2014.07.01
				# self._current_user_mail_address = current_user.get('Email', '')
				## Email から取得できない場合がなぜか時々あるのでその場合は、LoginName から取得
				# if self._current_user_mail_address is None or self._current_user_mail_address == '':
				#	login_name = current_user.get('LoginName', '')
				#	login_name_sp = login_name.split('|')
				#	self._current_user_mail_address = login_name_sp[len(login_name_sp) - 1]
				login_name = current_user.get('LoginName', '')
				login_name_sp = login_name.split('|')
				self._current_user_mail_address = login_name_sp[len(login_name_sp) - 1]
				if self._current_user_mail_address is None or self._current_user_mail_address == '':
					self._current_user_mail_address = current_user.get('Email', '')

				self._current_user_is_admin = current_user.get('IsSiteAdmin', False)
				user_id_dict = current_user.get('UserId', None)
				if user_id_dict is not None:
					# logging.debug(user_id_dict)
					self._current_user_name_id = user_id_dict.get('NameId', '')
				break

		if str(self._current_user_mail_address) == '':
			logging.debug(result_value_json)

		logging.info('current_user_mail_address=' + str(self._current_user_mail_address))
		logging.info('current_user_name_id=' + str(self._current_user_name_id))
		logging.info('current_user_is_admin=' + str(self._current_user_is_admin))


# サテライトサイトガジェットの認証
class _AuthSSiteGadget(Handler_Basic_Request, _OidBasePage):
	MD5_SUFFIX_KEY = 'eb58b02a34ed44ef83322caa687fc996'
	ENCODE_KEY = '804b86a56ccd46d39540123f4125d337'
	ENCODE_IV = '\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'

	# 変数初期化
	_tenant = ''
	# viewer_email = ''
	# viewer_email_raw = ''
	# viewer_user_id = ''
	# mode = sateraito_func.MODE_SSITE
	# _current_user_email = ''
	# _current_user_id = ''
	_current_user_is_admin = False
	_host_name = sateraito_func.OPENSOCIAL_CONTAINER_SSITE

	# SSITE：OpenIDConnect対応に伴い不要に
	#	# OpenIDのかわりに印刷ウインドウなどで認証に使うCookieをセット（有効期限…とりあえず1日）
	#	def setTokenToCookie(self, token):
	#		#name = 'auth_token_ssite'
	#		name = 'auth_token'
	#		value = str(token)
	#		expires = UcfUtil.add_days(UcfUtil.getNow(), 1).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
	#		path = '/'
	#		domain = ''
	#		secure = ''		# 'secure'
	#		self.response.headers.add_header('Set-Cookie', str(name) + '=' + value + ';' + 'expires=' + str(expires) + ';' + 'Path=' + str(path) + ';' + (('domain=' + str(domain) + ';') if domain != '' else '') + secure)

	def getCurrentUserEmail(self):
		encoded_user_email = self.request.get('email')
		user_email = ''
		if encoded_user_email != '':
			user_email = UcfUtil.deCryptoAESWithPKCS5(encoded_user_email, self.ENCODE_KEY, iv=self.ENCODE_IV, mode=AES.MODE_CBC)
		logging.info('user_email=' + user_email)
		return user_email

	# チェックキーチェック
	def _checkCheckKey(self, uid, tenant, check_key):

		is_ok = False

		# MD5SuffixKey
		md5_suffix_key = self.MD5_SUFFIX_KEY

		# チェックキーチェック
		if tenant != '' and uid != '' and check_key != '' and md5_suffix_key != '':
			tenant = tenant.lower()
			tenant_check_keys = []
			now = datetime.datetime.now()  # 標準時
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, -5).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, -4).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, -3).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, -2).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, -1).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + now.strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, 1).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, 2).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, 3).strftime('%Y%m%d%H%M') + md5_suffix_key))
			tenant_check_keys.append(UcfUtil.md5(tenant + uid + UcfUtil.add_minutes(now, 4).strftime('%Y%m%d%H%M') + md5_suffix_key))

			is_ok = False
			for tenant_check_key in tenant_check_keys:
				if tenant_check_key.lower() == check_key.lower():
					is_ok = True
					break
		if not is_ok:
			logging.warning('invalid check_key.')
		return is_ok

	# SSITE：サテライトサイト対応…ガジェットの認証（簡易認証）…TODO 標準高速化対応ができたら、OIDC認証に切り替えたい
	def _authSSiteGadget(self, tenant, domain_entry):
		uid = self.request.get('uid')
		logging.info('uid=' + uid)
		check_key = self.request.get('ck')
		logging.info('ck=' + check_key)
		is_admin = self.request.get('is_admin')
		logging.info('is_admin=' + is_admin)

		# if self._checkCheckKey(uid, tenant, check_key):  # キーのチェックは「ssite側のテナント名で」おこなうのでこれは間違い
		if self._checkCheckKey(uid, domain_entry.ssite_tenant_id, check_key):
			self._tenant = tenant
			self.viewer_user_id = uid
			self.viewer_email_raw = self.getCurrentUserEmail()
			self.viewer_email = self.viewer_email_raw.lower()
			self._current_user_is_admin = True if is_admin == '1' else False
			self.mode = sateraito_func.MODE_SSITE

		# if sateraito_inc.debug_mode:
		# 	self._tenant = '--ssite--sateraito'
		# 	self.viewer_user_id = 'admin@gv.sateraito.jp'
		# 	self.viewer_email_raw = 'admin@gv.sateraito.jp'
		# 	self.viewer_email = 'admin@gv.sateraito.jp'
		# 	self._current_user_is_admin = True if is_admin == '1' else False
		# 	self.mode = sateraito_func.MODE_SSITE

		# OIDC対応…認証側がCookieではなくセッションでチェックするので、簡易認証ではあるけど、ここでもセット

		if self.viewer_email is None or self.viewer_email == '' or self.viewer_user_id is None or self.viewer_user_id == '':
			self.response.out.write("Failed get authed account.<br><br>")
			logging.error('Failed get authed account.')

			self.session['viewer_email'] = ''
			self.session['opensocial_viewer_id'] = ''
			self.session['is_oidc_loggedin'] = False
			self.session['is_oidc_need_show_signin_link'] = True
			return False

		self.session['viewer_email'] = str(self.viewer_email)
		self.session['opensocial_viewer_id'] = str(uid)  # 使うかな？？
		self.session['is_oidc_loggedin'] = True
		self.session['is_oidc_need_show_signin_link'] = False

		return True


class BpGetWFUserList(_BasePage):
	# memcache entry expires in 60 min
	memcache_expire_secs = 60 * 60

	def _memcache_key(self, google_apps_domain):
		return 'script=getwfuserlist&google_apps_domain=' + google_apps_domain + '&g=2'

	def clearMemcache(self, google_apps_domain):
		memcache.delete(self._memcache_key(google_apps_domain))


##############################################################
# CSV作成入口ページ：抽象クラス
##############################################################
class _ExportCsv(Handler_Basic_Request, _BasePage):
	def _create_request_token(self):
		return UcfUtil.guid()

	# タスクキューレコードを追加
	def _createCsvTaskQueue(self, google_apps_domain, task_type):
		# リクエストトークン作成（このキーでJSから照会）
		request_token = self._create_request_token()
		logging.info('request_token=' + str(request_token))

		tq_entry = sateraito_db.CsvTaskQueue(id=request_token)
		tq_entry.request_token = request_token
		tq_entry.task_type = task_type
		tq_entry.status = ''
		tq_entry.deal_status = 'PROCESSING'
		tq_entry.download_url = ''
		tq_entry.expire_date = datetime.datetime.now() + datetime.timedelta(days=1)  # csv download expires in 24 hours
		tq_entry.put()

		return tq_entry

	# CSV作成キューを登録
	def _addCsvTaskQueue(self, task_url, task_params, countdown=3):
		default_q = taskqueue.Queue('default')
		t = taskqueue.Task(
			url=task_url,
			params=task_params,
			target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
			countdown=countdown
		)
		default_q.add(t)


##############################################################
# CSV作成処理タスクキュー：抽象クラス
##############################################################
class _TqExportCsv(Handler_Basic_Request, _BasePage):
	def _getUTCTimesForSearchDoc(self, from_date_localtime_raw, to_date_localtime_raw):
		# from_date
		from_date_utc = None
		if from_date_localtime_raw.strip() != '':
			from_date_localtime_arr = from_date_localtime_raw.split(" ")
			if len(from_date_localtime_arr) == 1:
				from_date_localtime = datetime.datetime.strptime(from_date_localtime_arr[0] + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
			else:
				from_date_localtime = datetime.datetime.strptime(
					from_date_localtime_arr[0] + ' ' + from_date_localtime_arr[1] + ':00', '%Y-%m-%d %H:%M:%S')
			from_date_utc = sateraito_func.toUtcTime(from_date_localtime)
		# to_date
		to_date_utc = None
		if to_date_localtime_raw.strip() != '':
			to_date_localtime_arr = to_date_localtime_raw.split(" ")
			if len(to_date_localtime_arr) == 1:
				to_date_localtime = datetime.datetime.strptime(to_date_localtime_arr[0] + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
			else:
				to_date_localtime = datetime.datetime.strptime(to_date_localtime_arr[0] + ' ' + to_date_localtime_arr[1] + ':00'
				                                               , '%Y-%m-%d %H:%M:%S')
			to_date_localtime = UcfUtil.add_days(to_date_localtime, 1)
			to_date_utc = sateraito_func.toUtcTime(to_date_localtime)
		#    older_than_utc = None
		#    if older_than != '':
		#      older_than_splited = older_than.split('+')
		#      local_time_older_than = datetime.datetime.strptime(older_than_splited[0], '%Y-%m-%d %H:%M:%S.%f')
		#      older_than_utc = sateraito_func.toUtcTime(local_time_older_than)

		return from_date_utc, to_date_utc

	def createCsvDownloadId(self):
		''' create new csv download id string
'''
		# create 8-length random string
		s = 'abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
		random_string = ''
		for j in range(8):
			random_string += random.choice(s)
		# create date string
		dt_now = datetime.datetime.now()
		date_string = dt_now.strftime('%Y%m%d%H%M%S')
		# create send_id
		return date_string + random_string

	def _saveCsv(self, google_apps_domain, app_id, tq_entry, csv_download_id, csv_filename, csv_string, is_api=False):
		### save csv data to datastore
		# csv_string = str(csv_string)
		# csv_string = sateraito_func.washShiftJISErrorChar(csv_string)
		csv_string = sateraito_func.encodeString(csv_string, type_import=False)
		# csv_string = csv_string.encode('cp932')    #Shift_JIS変換

		csv_file_encoding = 'cp932'
		row_dict = sateraito_db.OtherSetting.getDict()
		if 'csv_file_encoding' in row_dict and row_dict['csv_file_encoding'] is not None:
			csv_file_encoding = row_dict['csv_file_encoding']

		csv_string = csv_string.encode(csv_file_encoding)  # Shift_JIS変換

		# devide csv data
		# CAUTION: Datastore entity can have only 1MB data per entity
		#          so you have to devide data if it is over 1MB
		csv_data_length = len(csv_string)
		csv_datas = []
		NUM_STRING_PER_ENTITY = 1000 * 900  # 900 KB
		number_of_entity = (csv_data_length // NUM_STRING_PER_ENTITY) + 1
		for i in range(0, number_of_entity):
			start_index = i * NUM_STRING_PER_ENTITY
			end_index = start_index + NUM_STRING_PER_ENTITY
			csv_datas.append(csv_string[start_index:end_index])

		# store data to datastore
		expire_date = datetime.datetime.now() + datetime.timedelta(days=1)  # csv download expires in 24 hours
		for i in range(0, number_of_entity):
			new_data = sateraito_db.CsvDownloadData()
			new_data.csv_data = csv_datas[i]
			new_data.data_order = i
			new_data.csv_download_id = csv_download_id
			new_data.expire_date = expire_date
			new_data.csv_filename = csv_filename
			new_data.put()

		# ダウンロードURL
		if is_api:
			download_url = sateraito_func.getMySiteURL(google_apps_domain, request.url) + '/' + google_apps_domain + '/' + app_id + '/api/exportcsv/' + csv_download_id
		else:
			download_url = sateraito_func.getMySiteURL(google_apps_domain, request.url) + '/' + google_apps_domain + '/' + app_id + '/exportcsv/' + csv_download_id

		tq_entry.status = 'SUCCESS'
		tq_entry.deal_status = 'FIN'
		tq_entry.download_url = download_url
		tq_entry.expire_date = expire_date
		tq_entry.csv_download_id = csv_download_id
		tq_entry.put()

		return download_url

	def _saveCsv2(self, google_apps_domain, app_id, tq_entry, csv_download_id, csv_filename, csv_string, is_api=False):
		### save csv data to datastore
		# csv_string = str(csv_string)
		# csv_string = sateraito_func.washShiftJISErrorChar(csv_string)
		csv_string = sateraito_func.encodeString(csv_string, type_import=False)
		# csv_string = csv_string.encode('cp932')    #Shift_JIS変換

		csv_file_encoding = 'cp932'
		row_dict = sateraito_db.OtherSetting.getDict()
		if 'csv_file_encoding' in row_dict and row_dict['csv_file_encoding'] is not None:
			csv_file_encoding = row_dict['csv_file_encoding']

		csv_string = csv_string.encode(csv_file_encoding)  # Shift_JIS変換

		# devide csv data
		# CAUTION: Datastore entity can have only 1MB data per entity
		#          so you have to devide data if it is over 1MB
		csv_data_length = len(csv_string)
		csv_datas = []
		NUM_STRING_PER_ENTITY = 1000 * 900  # 900 KB
		number_of_entity = (csv_data_length // NUM_STRING_PER_ENTITY) + 1
		for i in range(0, number_of_entity):
			start_index = i * NUM_STRING_PER_ENTITY
			end_index = start_index + NUM_STRING_PER_ENTITY
			csv_datas.append(csv_string[start_index:end_index])

		# store data to datastore
		expire_date = datetime.datetime.now() + datetime.timedelta(days=1)  # csv download expires in 24 hours
		for i in range(0, number_of_entity):
			new_data = sateraito_db.CsvDownloadData()
			new_data.csv_data = csv_datas[i]
			new_data.data_order = i
			new_data.csv_download_id = csv_download_id
			new_data.expire_date = expire_date
			new_data.csv_filename = csv_filename
			new_data.put()

		# ダウンロードURL
		if is_api:
			download_url = sateraito_func.getMySiteURL(google_apps_domain,request.url) + '/' + google_apps_domain + '/' + app_id + '/api/exportcsv/' + csv_download_id
		else:
			download_url = sateraito_func.getMySiteURL(google_apps_domain,request.url) + '/' + google_apps_domain + '/' + app_id + '/exportcsv/' + csv_download_id

		# tq_entry.status = 'SUCCESS'
		tq_entry.status = ''
		# tq_entry.deal_status = 'FIN'
		tq_entry.deal_status = ''
		tq_entry.download_url = download_url
		tq_entry.expire_date = expire_date
		tq_entry.csv_download_id = csv_download_id
		tq_entry.put()

		return download_url

	def _updateErrorStatus(self, google_apps_domain, tq_entry, err=None):
		if tq_entry is not None:
			tq_entry.status = 'FAILED'
			tq_entry.deal_status = 'FIN'
			tq_entry.log_text = str(err) if err is not None else ''
			# tq_entry.csv_download_id = csv_download_id
			tq_entry.put()
