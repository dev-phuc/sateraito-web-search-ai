#!/usr/bin/python
# coding: utf-8
__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'

# set default encodeing to utf-8
from flask import render_template, request, make_response

import base64
from sateraito_logger import logging
import datetime
import json
import io
import cgi

import sateraito_inc
import sateraito_func
import sateraito_page
import sateraito_db
import workflowdoc
from sateraito_func import none2ZeroStr

from google.appengine.ext import blobstore
# from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import app_identity, namespace_manager

if sateraito_inc.ES_SEARCH_MODE:
  from search_alt import search_replace as search
else:
  from google.appengine.api import search

from ucf.utils.ucfutil import UcfUtil

MAX_QUERY_STRING_LENGTH_FULLTEXT = 2000
MAX_SORT_LIMIT_FULLTEXT = 10000
MAX_QUERY_LIMIT = 1000
MAX_SIZE_FILE_UPLOAD = 1024 * 1024 * 200

###########################################################
# API：認証API
###########################################################
class Auth(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('Access-Control-Allow-Origin',  '*')

		params = {}
		api_key = self.request.get('api_key')
		impersonate_email = self.request.get('impersonate_email', '')
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('api_key=' + api_key)
		logging.info('impersonate_email=' + impersonate_email)

		# set namespace
		sateraito_func.setNamespace(tenant_or_domain, '')

		try:
			# パラメータチェック
			if api_key == '':
				return self.outputResult(return_code=100, error_code='invalid_api_key', error_msg='', params=params)
			if impersonate_email == '':
				return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)

			# テナント、ドメイン情報取得
			tenant_or_domain_row = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
			if tenant_or_domain_row is None:
				return self.outputResult(return_code=403, error_code='invalid_domain', error_msg='', params=params)

			# APIキーのチェック（スコープも将来はチェックしたい？？）
			q = sateraito_db.APIKey.query()
			q = q.filter(sateraito_db.APIKey.api_key == api_key)
			key = q.get(keys_only=True)
			api_key_entry = key.get() if key is not None else None
			if api_key_entry is None:
				return self.outputResult(return_code=403, error_code='invalid_api_key', error_msg='', params=params)

			# impersonate_emailの存在＆権限チェック必要
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			TOKEN_EXPIRE_SECONDS = 43200 # 12時間×60分×60秒    （とりあえず12時間）

			# アクセストークンの作成
			access_token = self.createNewAccessToken(tenant_or_domain)
			# 期限
			dt_now = datetime.datetime.now()
			token_expire_date = UcfUtil.add_seconds(dt_now, TOKEN_EXPIRE_SECONDS)
			token_entry = sateraito_db.APIAccessToken()
			token_entry.access_token = access_token
			token_entry.impersonate_email = impersonate_email
			token_entry.api_key = api_key
			token_entry.token_expire_date = token_expire_date
			token_entry.put()

			logging.info('access_token=' + access_token)
			logging.info('token_expire_date=' + str(token_expire_date))
			logging.info('expires_in=' + str(TOKEN_EXPIRE_SECONDS))

			params['access_token'] = access_token
			params['expires_in'] = TOKEN_EXPIRE_SECONDS      # 有効期限を秒数で返す（少し短めにする？）

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：ユーザー：一覧取得
###########################################################
class UsersList(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('Access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		max_results = self.request.get('max_results', '')  # 取得最大件数
		start_cursor = self.request.get('start_cursor', '')  # 追加の取得結果がある場合に、Responseで返されるトークン

		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)
		logging.info('max_results=' + max_results)
		logging.info('start_cursor=' + start_cursor)

		max_results_int = UcfUtil.toInt(max_results)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)
		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)
			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)
			# ユーザー一覧を取得
			datas = []
			q = sateraito_db.UserInfo.query()
			q = q.order(sateraito_db.UserInfo.email)

			NUM_PER_PAGE = sateraito_func.NUM_MAX_RESULTS if max_results_int <= 0 or max_results_int > sateraito_func.NUM_MAX_RESULTS else max_results_int
			if start_cursor is not None and start_cursor != '':
				each_rows, start_cursor, more = q.fetch_page(NUM_PER_PAGE, start_cursor=Cursor(urlsafe=start_cursor))
			else:
				each_rows, start_cursor, more = q.fetch_page(NUM_PER_PAGE)
			for row in each_rows:
				datas.append({
					'email': none2ZeroStr(row.email),
					'family_name': none2ZeroStr(row.family_name),
					'given_name': none2ZeroStr(row.given_name),
					'family_name_kana': none2ZeroStr(row.family_name_kana),
					'given_name_kana': none2ZeroStr(row.given_name_kana),
					'employee_id': none2ZeroStr(row.employee_id),
					'company_name': none2ZeroStr(row.company_name),
					'department_1': none2ZeroStr(row.department_1),
					'department_2': none2ZeroStr(row.department_2),
					'department_3': none2ZeroStr(row.department_3),
					'department_4': none2ZeroStr(row.department_4),
					'job_title': none2ZeroStr(row.job_title),
					'department_code': none2ZeroStr(row.department_code),
					'company_email_1': none2ZeroStr(row.company_email_1),
					'company_email_2': none2ZeroStr(row.company_email_2),
					'personal_email_1': none2ZeroStr(row.personal_email_1),
					'personal_email_2': none2ZeroStr(row.personal_email_2),
					'company_phone_number_1': none2ZeroStr(row.company_phone_number_1),
					'company_extension_number_1': none2ZeroStr(row.company_extension_number_1),
					'company_phone_number_2': none2ZeroStr(row.company_phone_number_2),
					'personal_phone_number_1': none2ZeroStr(row.personal_phone_number_1),
					'personal_phone_number_2': none2ZeroStr(row.personal_phone_number_2),
					'language': none2ZeroStr(row.language),
				})

			params['datas'] = datas
			logging.info(len(datas))
			# logging.info(start_cursor)
			logging.info(more)
			params['next_cursor'] = start_cursor.urlsafe().decode() if more and start_cursor is not None else ''

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：ユーザー：詳細取得
###########################################################
class UsersGet(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('Access-Control-Allow-Origin', '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		email = self.request.get('email', '')  # ユーザーID（email）
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)
		logging.info('email=' + email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30
		# if viewer_email == '':
		#  self.outputResult(return_code=100, error_code='invalid_viewer_email', error_msg='', params=params)
		#  return
		if email == '':
			return self.outputResult(return_code=100, error_code='invalid_email', error_msg='', params=params)
		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)
		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)
			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)
			# ユーザー詳細を取得
			data = {}
			row = sateraito_db.UserInfo.getInstance(email)
			if row is None:
				return self.outputResult(return_code=404, error_code='not_found', error_msg='not found target userinfo.', params=params)
			else:
				data = {
					'email': none2ZeroStr(row.email),
					'family_name': none2ZeroStr(row.family_name),
					'given_name': none2ZeroStr(row.given_name),
					'family_name_kana': none2ZeroStr(row.family_name_kana),
					'given_name_kana': none2ZeroStr(row.given_name_kana),
					'employee_id': none2ZeroStr(row.employee_id),
					'company_name': none2ZeroStr(row.company_name),
					'department_1': none2ZeroStr(row.department_1),
					'department_2': none2ZeroStr(row.department_2),
					'department_3': none2ZeroStr(row.department_3),
					'department_4': none2ZeroStr(row.department_4),
					'job_title': none2ZeroStr(row.job_title),
					'department_code': none2ZeroStr(row.department_code),
					'company_email_1': none2ZeroStr(row.company_email_1),
					'company_email_2': none2ZeroStr(row.company_email_2),
					'personal_email_1': none2ZeroStr(row.personal_email_1),
					'personal_email_2': none2ZeroStr(row.personal_email_2),
					'company_phone_number_1': none2ZeroStr(row.company_phone_number_1),
					'company_extension_number_1': none2ZeroStr(row.company_extension_number_1),
					'company_phone_number_2': none2ZeroStr(row.company_phone_number_2),
					'personal_phone_number_1': none2ZeroStr(row.personal_phone_number_1),
					'personal_phone_number_2': none2ZeroStr(row.personal_phone_number_2),
					'language': none2ZeroStr(row.language),
				}
			params['data'] = data

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class GetNewWorkflowDocID(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('Access-Control-Allow-Origin', '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			params['doc_id'] = sateraito_db.WorkflowDoc.getNewWorkflowDocID()

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class ClientInfoList(sateraito_page._PublicAPIPage):
	# memcache entry expires in 10 min
	memcache_expire_secs = 60 * 10

	def _memcache_key(self, google_apps_domain, master_code):
		memcache_key_value = 'script=getmasterdata&google_apps_domain=' + google_apps_domain + '&master_code=' + master_code
		return memcache_key_value

	def query_search_index_by_cursor(self, index, query_string, query_options, is_get_all=True):
		result_documents = []
		cursor = search.Cursor()

		try:
			if is_get_all:
				while cursor is not None:
					query_options._cursor = cursor
					query = search.Query(query_string=query_string, options=query_options)
					result = index.search(query)

					result_returned = len(result.results)
					cursor = result.cursor
					if result_returned > 0:
						result_documents.extend(result.results)

			else:
				query = search.Query(query_string=query_string, options=query_options)
				result = index.search(query)
				result_returned = len(result.results)
				if result_returned > 0:
					result_documents = result.results

		except search.Error:
			logging.exception('error get master list')
			return None

		return result_documents

	def getDataTextSearch(self, google_apps_domain, master_code, get_comment_also=False):
		query_string = '(master_code=' + master_code + ')'
		expressions = []
		expressions.append(search.SortExpression(expression='data_key', default_value='', direction=search.SortExpression.ASCENDING))

		sort_options = search.SortOptions(expressions=expressions, limit=MAX_SORT_LIMIT_FULLTEXT)
		query_options = search.QueryOptions(sort_options=sort_options, limit=MAX_QUERY_LIMIT)
		index = search.Index(name=sateraito_func.INDEX_SEARCH_MASTER_DATA)
		results = self.query_search_index_by_cursor(index, query_string, query_options)

		logging.info('documents.number_found=' + str(len(results)))
		ret_results = []
		for document in results:
			master_dict = {
				'id': document.doc_id
			}
			for field in document.fields:
				comment = ''
				master_code = ''
				data_key = ''
				created_date = ''
				if field.name == 'comment':
					if get_comment_also:
						comment = field.value
				if field.name == 'master_code':
					master_code = field.value
				if field.name == 'data_key':
					data_key = field.value

				for i in range(1, (sateraito_db.NUM_ATTRIBUTES_MASTER_DATA + 1)):
					master_dict['attribute_' + str(i)] = ''
					if field.name == 'attribute_' + str(i):
						if field.value != '' and field.value is not None:
							master_dict['attribute_' + str(i)] = sateraito_func.noneToZeroStr(field.value)

				if comment != '' and comment is not None:
					master_dict['comment'] = comment
				if master_code != '' and master_code is not None:
					master_dict['master_code'] = sateraito_func.noneToZeroStr(master_code)
				if data_key != '' and data_key is not None:
					master_dict['data_key'] = sateraito_func.noneToZeroStr(data_key)

			ret_results.append(master_dict)
		return ret_results

	def clientMasterDef(self, google_apps_domain):
		master_datas = []
		master_code = sateraito_func.CLIENT_INFO_MASTER_CODE

		md_row = sateraito_db.MasterDef.getInstance(master_code)
		if md_row is not None:

			if md_row.is_use_ltcache:
				master_data_dict = self.getDataTextSearch(google_apps_domain, master_code)
				for item in master_data_dict:
					master_dict = {
						'id': sateraito_func.noneToZeroStr(item['id']),
						'document_code': sateraito_func.noneToZeroStr(item['data_key']),
						'client_name': sateraito_func.noneToZeroStr(item['attribute_1']),
					}
					master_datas.append(master_dict)
			else:
				q = sateraito_db.MasterData.query()
				q = q.filter(sateraito_db.MasterData.master_code == master_code)
				rows = q.fetch(keys_only=True)

				for row in rows:
					logging.info(row)
					row_dict = row.get()
					logging.info(row_dict)
					master_dict = {
						'id': sateraito_func.noneToZeroStr(row.id()),
						'document_code': sateraito_func.noneToZeroStr(row_dict.data_key),
						'client_name': sateraito_func.noneToZeroStr(row_dict.attribute_1),
					}
					master_datas.append(master_dict)

		return master_datas

	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('Access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			# ユーザー一覧を取得
			datas = []
			is_use_master_ref = sateraito_func.isUseClientMasterDef(tenant_or_domain, app_id)

			# get data client from client master def
			if is_use_master_ref:
				datas = self.clientMasterDef(tenant_or_domain)
			else:
				# get child doc folders
				q = sateraito_db.ClientInfo.query()
				q = q.order(-sateraito_db.ClientInfo.name)
				for row in q:
					datas.append({
						'id': row.client_id,
						'document_code': row.document_code,
						'client_name': row.name,
					})

			params['datas'] = datas

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class CurrencyList(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('Access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			# ユーザー一覧を取得
			params['datas'] = sateraito_func.getCurrencyMasterDef(viewer_email)

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class TagsList(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			# ユーザー一覧を取得
			datas = []

			# get child doc folders
			q = sateraito_db.Categories.query()
			q = q.filter(sateraito_db.Categories.is_tag == True)
			q = q.filter(sateraito_db.Categories.del_flag == False)
			q = q.order(-sateraito_db.Categories.updated_date)

			for row in q:
				datas.append({
					'id': row.categorie_id,
					'name': row.name,
					'uploaded_date': str(sateraito_func.toShortLocalTime(row.uploaded_date))
				})
			params['datas'] = datas

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class CategorysList(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			# ユーザー一覧を取得
			datas = []

			# get child doc folders
			q = sateraito_db.Categories.query()
			q = q.filter(sateraito_db.Categories.is_tag == False)
			q = q.filter(sateraito_db.Categories.del_flag == False)
			q = q.order(-sateraito_db.Categories.updated_date)

			for row in q:
				datas.append({
					'id': row.categorie_id,
					'name': row.name,
					'text_color': row.txt_color,
					'background_color': row.bg_color,
					'uploaded_date': str(sateraito_func.toShortLocalTime(row.uploaded_date))
				})

			# when empty category -> auto create new category sample
			if len(datas) == 0:
				new_code = 'sample'
				new_row = sateraito_db.Categories(id=new_code)
				new_row.name = 'サンプル'
				new_row.categorie_id = new_code
				new_row.txt_color = '#FFFFFF'
				new_row.bg_color = '#2196F3'
				new_row.put()
				datas.append({
					'id': new_row.categorie_id,
					'name': new_row.name,
					'text_color': new_row.txt_color,
					'background_color': new_row.bg_color,
					'uploaded_date': str(sateraito_func.toShortLocalTime(new_row.uploaded_date))
				})

			params['datas'] = datas

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class FoldersList(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			# ユーザー一覧を取得
			datas = []

			# get child doc folders
			q = sateraito_db.DocFolder.query()
			q = q.filter(sateraito_db.DocFolder.del_flag == False)
			q = q.order(sateraito_db.DocFolder.folder_name)

			for row in q:
				# updadte full path folder
				if row.full_path_folder is None:
					row.full_path_folder = sateraito_func.getFolderNameFullpath(row.folder_code)
					row.put()

				datas.append({
					'folder_code': row.folder_code,
					'folder_name': row.folder_name,
					'parent_folder_code': row.parent_folder_code,
					'full_path_folder': row.full_path_folder,
					'folder_col_sort': row.folder_col_sort,
					'folder_type_sort': row.folder_type_sort,
					'is_downloadable': True,  # workflow is admin
					'is_uploadable': True,  # workflow is admin
					'is_subfolder_creatable': True,  # workflow is admin
					'is_deletable': True,  # workflow is admin
				})
			params['datas'] = datas

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class FoldersListChild(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		folder_code = self.request.get('folder_code')

		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		if folder_code == '':
			return self.outputResult(return_code=100, error_code='invalid_folder_code', error_msg='', params=params)
		# 管理者権限での全件取得機能に対応 2017.06.30

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			# ユーザー一覧を取得
			datas = []

			# get child doc folders
			q = sateraito_db.DocFolder.query()
			q = q.filter(sateraito_db.DocFolder.del_flag == False)
			q = q.filter(sateraito_db.DocFolder.parent_folder_code == str(folder_code))
			q = q.order(sateraito_db.DocFolder.folder_name)

			for row in q:
				# updadte full path folder
				if row.full_path_folder is None:
					row.full_path_folder = sateraito_func.getFolderNameFullpath(row.folder_code)
					row.put()

				datas.append({
					'folder_code': row.folder_code,
					'folder_name': row.folder_name,
					'parent_folder_code': row.parent_folder_code,
					'full_path_folder': row.full_path_folder,
					'folder_col_sort': row.folder_col_sort,
					'folder_type_sort': row.folder_type_sort,
					'notice_mails': ' '.join(row.notice_mails),
					'is_downloadable': True,  # workflow is admin
					'is_uploadable': True,  # workflow is admin
					'is_subfolder_creatable': True,  # workflow is admin
					'is_deletable': True,  # workflow is admin
				})
			params['datas'] = datas

			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class GetUrlUploadFiles(sateraito_page._PublicAPIPage):
	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')      # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')        # 実行アカウント
		application_id = self.request.get('application_id', '')        # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		viewer_email = self.request.get('viewer_email', '')        # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）

		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		if viewer_email == '':
			return self.outputResult(return_code=100, error_code='invalid_viewer_email', error_msg='', params=params)

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		folder_code = self.request.get('folder_code', '')
		if folder_code == '':
			return self.outputResult(return_code=100, error_code='invalid_folder_code', error_msg='', params=params)
		fodler_dict = sateraito_db.DocFolder.getDict(folder_code)
		if fodler_dict is None or fodler_dict['del_flag']:
			return self.outputResult(return_code=100, error_code='not_found_folder', error_msg='', params=params)

		try:
			## テナント、ドメイン情報取得
			#tenant_or_domain_row = sateraito_db.TenantEntry.getInstance(tenant_or_domain, cache_ok=True)
			#if tenant_or_domain_row is None:
			#  self.outputResult(return_code=403, error_code='invalid_tenant', error_msg='', params=params)
			#  return

			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			namespace_name = tenant_or_domain + sateraito_func.DELIMITER_NAMESPACE_DOMAIN_APP_ID + app_id
			gcs_bucket_name = app_identity.get_default_gcs_bucket_name()
			gcs_filename_sub = gcs_bucket_name + '/' + namespace_name + '/' + folder_code

			# BlobStore アップロード用URLを作成
			upload_url = blobstore.create_upload_url('/' + tenant_or_domain + '/api/public/handleruploadfiles', gs_bucket_name=gcs_filename_sub, max_bytes_per_blob=MAX_SIZE_FILE_UPLOAD)
			params['url'] = upload_url
			return self.outputResult(return_code=0, error_code='', error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class HandlerUploadFiles(sateraito_page._PublicAPIPage, blobstore.BlobstoreUploadHandler):
	def check_param(self):

		# 更にFlaskのrequest.values、request.formだと、マルチパートでのPOSTに値が空の情報があると値が正しく取れなくなるためcgiを使った方法に変更（cgiは非推奨、廃止予定だが現時点では使用可能）
		request_body_byte = request.get_data()
		fp = io.BytesIO(request_body_byte)
		fs = cgi.FieldStorage(fp=fp, environ=request.environ)

		workflow_doc_id = fs.getfirst('workflow_doc_id', '')
		logging.info('workflow_doc_id=' + str(workflow_doc_id))

		folder_code = fs.getfirst('folder_code', '')
		logging.info('folder_code=' + str(folder_code))

		screen = fs.getfirst('screen', '')
		logging.info('screen=' + str(screen))

		# Check param
		# screen
		if screen == '':
			return False, {'filed_error': 'screen'}, 'screen'
		# workflow_doc_id
		if workflow_doc_id == '':
			return False, {'filed_error': 'workflow_doc_id'}, 'workflow_doc_id'
		# folder_code
		if folder_code == '':
			return False, {'filed_error': 'folder_code'}, 'invalid_folder_code'

		fodler_dict = sateraito_db.DocFolder.getDict(folder_code)
		if fodler_dict is None or fodler_dict['del_flag']:
			return False, {'filed_error': 'folder_code'}, 'invalid_folder_code'

		param = {
			'workflow_doc_id': workflow_doc_id,
			'folder_code': folder_code,
			'screen': screen,
		}
		return True, param, ''

	def handler_upload_files(self, tenant_or_domain, app_id, viewer_email, params, lang=sateraito_inc.DEFAULT_LANGUAGE):

		files_uploaded = []

		try:
			my_lang = sateraito_func.MyLang(lang)

			# Blobstoreからのファイル取得. request.form、request.get_data() などの前に↓を実施する必要がある
			envDummy = request.environ.copy()
			envDummy['wsgi.input'] = io.BytesIO(request.get_data())
			blobs_info = self.get_uploads(envDummy, field_name='attach_file')
			logging.info(blobs_info)

			workflow_doc_id = params['workflow_doc_id']
			folder_code = params['folder_code']
			screen = params['screen']

			for blob_info in blobs_info:
				file_id = sateraito_func.createNewFileId(sateraito_db.FileflowDoc.name_field)

				blob_key = blob_info.key()
				new_blob_info = blobstore.BlobInfo.get(blob_key)
				file_name = new_blob_info.filename

				# save to datastore
				new_row = sateraito_db.FileflowDoc(id=file_id)
				new_row.workflow_doc_id = workflow_doc_id
				new_row.folder_code = folder_code
				new_row.file_id = file_id
				new_row.file_name = file_name
				new_row.blob_key = blob_key
				new_row.mime_type = blob_info.content_type
				new_row.attached_by_user_email = viewer_email
				new_row.file_size = blob_info.size
				new_row.publish_flag = False
				new_row.author_email = viewer_email
				new_row.author_name = sateraito_func.getUserName(tenant_or_domain, viewer_email)
				new_row.put()

				# add total file size
				sateraito_db.FileSizeCounterShared.increment(new_row.file_size)

				# # logging
				# doc_title = workflow_doc_id
				# detail = my_lang.getMsg('MSG_DETAIL_UPLOAD_FILE').format(new_row.file_name, new_row.author_name, doc_title)

				# user_entry_dict = sateraito_db.GoogleAppsUserEntry.getDict(tenant_or_domain, viewer_email)
				# sateraito_db.OperationLog.addLogForFile(user_entry_dict['user_id'], user_entry_dict['user_email'],
				# 																				sateraito_db.OPERATION_UPLOAD_FILE, screen, file_id, workflow_doc_id,
				# 																				detail=detail)

				# register blob pointer
				sateraito_db.BlobPointer.registerNew(blob_info, namespace_manager.get_namespace())

				files_uploaded.append({
					'file_id': file_id,
					'workflow_doc_id': new_row.workflow_doc_id,
					'folder_code': new_row.folder_code,
					'file_name': new_row.file_name,
					'mime_type': new_row.mime_type,
					'attached_by_user_email': new_row.attached_by_user_email,
					'file_size': new_row.file_size,
					'publish_flag': new_row.publish_flag,
					'author_email': new_row.author_email,
					'author_name': new_row.author_name,
					'uploaded_date': str(sateraito_func.toShortLocalTime(new_row.uploaded_date)),
				})

			sateraito_func.updateFreeSpaceStatus(tenant_or_domain)

			return True, files_uploaded, ''

		except BaseException as e:
			self.outputErrorLog(e)
			return False, files_uploaded, str(e)

	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('access-Control-Allow-Origin',  '*')

		# 更にFlaskのrequest.values、request.formだと、マルチパートでのPOSTに値が空の情報があると値が正しく取れなくなるためcgiを使った方法に変更（cgiは非推奨、廃止予定だが現時点では使用可能）
		request_body_byte = request.get_data()
		fp = io.BytesIO(request_body_byte)
		fs = cgi.FieldStorage(fp=fp, environ=request.environ)

		params = {}
		access_token = fs.getfirst('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = fs.getfirst('impersonate_email', '')  # 実行アカウント
		viewer_email = fs.getfirst('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		application_id = fs.getfirst('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		lang = fs.getfirst('lang', sateraito_inc.DEFAULT_LANGUAGE)

		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		if viewer_email == '':
			return self.outputResult(return_code=100, error_code='invalid_viewer_email', error_msg='', params=params)

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			submitter_email = viewer_email

			# ログインユーザー情報を取得
			viewer_info = sateraito_db.UserInfo.getUserInfo(viewer_email)
			if viewer_info is None:
				return self.outputResult(return_code=100, error_code='invalid_viewer', error_msg='', params=params)

			# 申請者情報を取得
			submitter_info = sateraito_db.UserInfo.getUserInfo(submitter_email)
			if submitter_info is None:
				return self.outputResult(return_code=100, error_code='invalid_submitter', error_msg='', params=params)

			# Check param
			param_valid, params, error_code = self.check_param()
			if not param_valid:
				return self.outputResult(return_code=100, error_code=error_code, error_msg='', params=params)

			# START MAIN HANDLER #
			is_success, files_uploaded, error_msg = self.handler_upload_files(tenant_or_domain, app_id, viewer_email, params, lang)

			if is_success:
				return self.outputResult(return_code=0, error_code=0,error_msg='', params={'files_uploaded': files_uploaded})
			else:
				return self.outputResult(return_code=100, error_code=error_code, error_msg=error_msg, params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


###########################################################
# API：
###########################################################
class SubmitCreateNewWorkflow(sateraito_page._PublicAPIPage):
	def check_param(self, tenant_or_domain, app_id, viewer_email, auto_create_client=False):

		# get params
		workflow_doc_id = self.request.get('workflow_doc_id', '')
		files_id_raw = self.request.get('files_id', '')
		title = self.request.get('title', '')
		categorie_id = self.request.get('categorie_id', '')
		tag_list_raw = self.request.get('tag_list', '')
		description = self.request.get('description', '')
		notice_users_raw = self.request.get('notice_users', '')
		folder_code = self.request.get('folder_code', '')
		need_preservation_doc = self.request.get('need_preservation_doc', 'false')
		client_id = self.request.get('client_id', '')
		client_name = self.request.get('client_name', '')
		document_code = self.request.get('document_code', '')
		transaction_date = self.request.get('transaction_date', '')
		transaction_amount = self.request.get('transaction_amount', '')
		currency = self.request.get('currency', '')
		screen = self.request.get('screen', '')
		key_split = self.request.get('key_split', sateraito_inc.KEY_SPLIT_RAW)
		mode_admin = True
		is_client_master_data = False

		tag_list = []
		if tag_list_raw != '':
			tag_list = tag_list_raw.split(key_split)

		notice_users = []
		if notice_users_raw != '':
			notice_users = notice_users_raw.split(key_split)

		files_id = []
		if files_id_raw != '':
			files_id = files_id_raw.split(key_split)

		need_preservation_doc = sateraito_func.strToBool(need_preservation_doc)

		# check capacity
		domain_dict = sateraito_db.GoogleAppsDomainEntry.getDict(tenant_or_domain)
		if domain_dict['is_capacity_over']:
			return False, {'filed_error': 'capacity_over'}, 'capacity_over'

		# Check param

		# files_id
		if len(files_id) == 0:
			return False, {'filed_error': 'files_id'}, 'invalid_files_id'
		else:
			for file_id_item in files_id:
				row_file = sateraito_db.FileflowDoc.getInstance(file_id_item)

				if row_file is None:
					return False, {'filed_error': file_id_item}, 'invalid_files_id'

		# workflow_doc_id
		if workflow_doc_id == '':
			return False, {'filed_error': 'workflow_doc_id'}, 'invalid_workflow_doc_id'

		# screen
		if screen == '':
			return False, {'filed_error': 'screen'}, 'invalid_screen'
		elif screen not in [sateraito_db.SCREEN_ADMIN_CONSOLE, sateraito_db.SCREEN_USER_CONSOLE, sateraito_db.SCREEN_POPUP_FILE_UPLOAD]:
			return False, {'filed_error': 'screen'}, 'invalid_screen'

		# folder_code
		if folder_code == '':
			return False, {'filed_error': 'folder_code'}, 'invalid_folder_code'
		else:
			fodler_dict = sateraito_db.DocFolder.getDict(folder_code)
			if fodler_dict is None or fodler_dict['del_flag']:
				return False, {'filed_error': 'folder_code'}, 'invalid_folder_code'

		# categorie_id
		if categorie_id == '':
			return False, {'filed_error': 'categorie_id'}, 'invalid_categorie_id'
		else:
			if sateraito_db.Categories.getDict(categorie_id) is None:
				return False, {'filed_error': 'categorie_id'}, 'not_found_categorie_id'

		# title
		if title == '':
			return False, {'filed_error': 'title'}, 'invalid_title'

		# notice_users
		if len(notice_users) > 0:
			list_apps_domain = sateraito_func.getListAppsDomain(tenant_or_domain)

			for user_email in notice_users:
				if not sateraito_func.isValidEmail(user_email):
					return False, {'filed_error': 'notice_users'}, 'invalid_notice_users'
				else:
					domain_email = str(user_email).split('@')[1]
					if domain_email not in list_apps_domain:
						return False, {'filed_error': 'notice_users'}, 'invalid_notice_users'

		# need_preservation_doc
		if need_preservation_doc:
			# transaction_date
			if transaction_date == '':
				return False, {'filed_error': 'transaction_date'}, 'invalid_transaction_date'
			else:
				try:
					datetime.datetime.strptime(transaction_date, sateraito_inc.FORMAT_TRANSACTION_DATE)
				except ValueError:
					return False, {'filed_error': 'transaction_date'}, 'invalid_transaction_date'

			# transaction_amount
			if transaction_amount == '':
				return False, {'filed_error': 'transaction_amount'}, 'invalid_transaction_amount'
			else:
				try:
					transaction_amount = float(transaction_amount)
				except BaseException as e:
					return False, {'filed_error': 'invalid_transaction_amount'}, 'invalid_transaction_amount'

			# currency
			if currency == '':
				return False, {'filed_error': 'currency'}, 'invalid_currency'
			else:
				if currency not in sateraito_func.getCurrencyMasterDef(viewer_email):
					return False, {'filed_error': 'invalid_currency'}, 'invalid_currency'

			# client_name
			if client_name == '' and client_id == '':
				return False, {'filed_error': 'client_name'}, 'invalid_client_name'

			is_client_master_data = sateraito_func.isUseClientMasterDef(tenant_or_domain, app_id)
			if is_client_master_data:
				md_row = None

				# Find by id client
				if client_id != '':
					md_row = sateraito_db.MasterData.getInstance('client_master', client_id)

				# # Find by id document code of client
				# if md_row is None and document_code != '':
				# 	md_row = sateraito_db.MasterData.loadClientMasterData(document_code)

				if md_row:
					# if client_name != '' and client_name != md_row.attribute_1:
					# 	return False, {'filed_error': 'document_code'}, 'invalid_client_name'
					# if document_code != '' and document_code != md_row.data_key:
					# 	return False, {'filed_error': 'document_code'}, 'invalid_document_code'

					client_name = md_row.attribute_1
					document_code = md_row.data_key
				else:
					return False, {'failed_error': 'document_code'}, 'not_found_client_in_data_master'
			else:
				row_client = sateraito_db.ClientInfo.getByName(client_name)
				if row_client is None and auto_create_client:
					# If the document code is not duplicate, create a new customer information with the customer name and document code
					client_id = sateraito_db.ClientInfo.getNewID()
					row_client = sateraito_db.ClientInfo(id=client_id)
					row_client.client_id = client_id
					row_client.name = client_name
					row_client.document_code = document_code
					row_client.put()

				if row_client:
					client_id = row_client.client_id
					client_name = row_client.name
					document_code = row_client.document_code

		# check and create new tags
		ids_tag = []
		names_tag = []
		for tag_name_item in tag_list:
			tag_dict = sateraito_db.Categories.getTagByName(tag_name_item)
			if tag_dict is None:
				tag_id = sateraito_db.Categories.createNewCode()
				row_tag = sateraito_db.Categories(id=tag_id)
				row_tag.categorie_id = tag_id
				row_tag.name = tag_name_item
				row_tag.is_tag = True
				row_tag.put()
				ids_tag.append(row_tag.categorie_id)
				names_tag.append(row_tag.name)
			else:
				ids_tag.append(tag_dict.categorie_id)
				names_tag.append(tag_name_item)

		param = {
			'workflow_doc_id': workflow_doc_id,
			'folder_code': folder_code,
			'categorie_id': categorie_id,
			'title': title,
			'ids_tag': ids_tag,
			'names_tag': names_tag,
			'description': description,
			'notice_users': notice_users,
			# 'accessible_users': fodler_dict['accessible_users'],
			'need_preservation_doc': need_preservation_doc,
			'client_id': client_id,
			'client_name': client_name,
			'document_code': document_code,
			'transaction_date': transaction_date,
			'transaction_amount': transaction_amount,
			'currency': currency,
			'screen': screen,
			'is_client_master_data': is_client_master_data,
			'google_drive_folder_id': '',
			'list_id_file_delete': [],
			'is_upload_from_email': False,
			'viewer_email': viewer_email,
			'list_id_file_uploaded': files_id,
		}
		return True, param, ''

	def _process(self, tenant_or_domain):
		logging.info('**** requests *********************')
		logging.info(self.request)

		self.setResponseHeader('access-Control-Allow-Origin',  '*')

		params = {}
		access_token = self.request.get('access_token', '')  # auth APIで取得したアクセストークン（例：Ym1WNGRITmxkR1JsYlc4PTIwMTUwNTExMDMyMzM5dWtPN3A2YzNpREY2YkpvMg==）
		impersonate_email = self.request.get('impersonate_email', '')  # 実行アカウント
		viewer_email = self.request.get('viewer_email', '')  # データ取得対象アカウント…どのユーザーの権限で取得するか（GUI上のログインユーザーと同等）
		application_id = self.request.get('application_id', '')  # 仮想アプリケーションID  ※未指定ならデフォルト（default）扱い
		lang = self.request.get('lang', sateraito_inc.DEFAULT_LANGUAGE)

		logging.info('tenant_or_domain=' + tenant_or_domain)
		logging.info('access_token=' + access_token)
		logging.info('impersonate_email=' + impersonate_email)
		logging.info('application_id=' + application_id)
		logging.info('viewer_email=' + viewer_email)

		app_id = application_id
		if app_id is None or app_id == '':
			app_id = sateraito_func.DEFAULT_APP_ID

		# パラメータチェック
		if access_token == '':
			return self.outputResult(return_code=100, error_code='invalid_access_token', error_msg='', params=params)
		if impersonate_email == '':
			return self.outputResult(return_code=100, error_code='invalid_impersonate_email', error_msg='', params=params)
		if viewer_email == '':
			return self.outputResult(return_code=100, error_code='invalid_viewer_email', error_msg='', params=params)

		# set namespace
		if not sateraito_func.setNamespace(tenant_or_domain, app_id):
			return self.outputResult(return_code=100, error_code='invalid_application_id', error_msg='', params=params)

		try:
			# impersonate_emailの存在＆権限チェック必要（いるかなー？？）
			is_workflow_admin = self.isWorkflowAdmin(impersonate_email, tenant_or_domain)
			if not is_workflow_admin:
				return self.outputResult(return_code=403, error_code='invalid_impersonate_email', error_msg='', params=params)

			# アクセストークンのチェック（スコープも将来はチェックしたい？？）
			is_access_token_ok, error_code = self.checkAccessToken(tenant_or_domain, access_token)
			if not is_access_token_ok:
				return self.outputResult(return_code=403, error_code=error_code, error_msg='', params=params)

			submitter_email = viewer_email

			# ログインユーザー情報を取得
			viewer_info = sateraito_db.UserInfo.getUserInfo(viewer_email)
			if viewer_info is None:
				return self.outputResult(return_code=100, error_code='invalid_viewer', error_msg='', params=params)

			# 申請者情報を取得
			submitter_info = sateraito_db.UserInfo.getUserInfo(submitter_email)
			if submitter_info is None:
				return self.outputResult(return_code=100, error_code='invalid_submitter', error_msg='', params=params)

			# Check param
			param_valid, param, error_code = self.check_param(tenant_or_domain, app_id, viewer_email, auto_create_client=True)
			if not param_valid:
				return self.outputResult(return_code=100, error_code=error_code, error_msg='', params=params)

			my_workflowdoc = workflowdoc._CreateWorkflowDoc()
			my_workflowdoc.viewer_email = viewer_email
			is_success, new_row, error_code = my_workflowdoc.createDoc(tenant_or_domain, app_id, lang=lang, param=param)

			if is_success:
				return self.outputResult(return_code=0, error_code=0,error_msg='', params={'datas': new_row})
			else:
				return self.outputResult(return_code=100, error_code=error_code, error_msg='', params=params)

		except BaseException as e:
			self.outputErrorLog(e)
			return self.outputResult(return_code=999, error_code='fatal_error', error_msg=str(e), params=params)

	def doAction(self, tenant_or_domain):
		return self._process(tenant_or_domain)


# app = ndb.toplevel(webapp2.WSGIApplication([
# 	('/([^/]*)/api/public/auth', ),
#
# 	('/([^/]*)/api/public/users/list', ),
# 	('/([^/]*)/api/public/users/get', ),
#
# 	('/([^/]*)/api/public/workflowdoc/getnewdocid', ),
# 	('/([^/]*)/api/public/workflowdoc/submit', ),
#
# 	('/([^/]*)/api/public/clientinfo/list', ),
#
# 	('/([^/]*)/api/public/currency/list', ),
#
# 	('/([^/]*)/api/public/tags/list', ),
#
# 	('/([^/]*)/api/public/categories/list', ),
#
# 	('/([^/]*)/api/public/geturluploadfiles', ),
# 	('/([^/]*)/api/public/handleruploadfiles', ),
#
# 	('/([^/]*)/api/public/folders/list', ),
# 	('/([^/]*)/api/public/folders/listchild', ),
#
# ], debug=sateraito_inc.debug_mode, config=sateraito_page.config))
def add_url_rules(app):
	app.add_url_rule('/<string:tenant_or_domain>/api/public/auth',
									 view_func=Auth.as_view('ApiForPublicAuth'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/users/list',
									 view_func=UsersList.as_view('ApiForPublicUsersList'))
	app.add_url_rule('/<string:tenant_or_domain>/api/public/users/get',
									 view_func=UsersGet.as_view('ApiForPublicUsersGet'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/workflowdoc/getnewdocid',
									 view_func=GetNewWorkflowDocID.as_view('ApiForPublicGetNewWorkflowDocID'))
	app.add_url_rule('/<string:tenant_or_domain>/api/public/workflowdoc/submit',
									 view_func=SubmitCreateNewWorkflow.as_view('ApiForPublicSubmitCreateNewWorkflow'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/clientinfo/list',
									 view_func=ClientInfoList.as_view('ApiForPublicClientInfoList'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/currency/list',
									 view_func=CurrencyList.as_view('ApiForPublicCurrencyList'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/tags/list',
									 view_func=TagsList.as_view('ApiForPublicTagsList'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/categories/list',
									 view_func=CategorysList.as_view('ApiForPublicCategorysList'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/geturluploadfiles',
									 view_func=GetUrlUploadFiles.as_view('ApiForPublicGetUrlUploadFiles'))
	app.add_url_rule('/<string:tenant_or_domain>/api/public/handleruploadfiles',
									 view_func=HandlerUploadFiles.as_view('ApiForPublicHandlerUploadFiles'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/folders/list',
									 view_func=FoldersList.as_view('ApiForPublicFoldersList'))

	app.add_url_rule('/<string:tenant_or_domain>/api/public/folders/listchild',
									 view_func=FoldersListChild.as_view('ApiForPublicFoldersListChild'))

