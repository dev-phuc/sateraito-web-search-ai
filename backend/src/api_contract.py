#!/usr/bin/python
# coding: utf-8

__author__ = 'T.ASAO <asao@sateraito.co.jp>'
# from flask import Flask, Response, render_template, request, make_response, session, redirect, after_this_request
from flask import render_template, request, make_response
# import urllib
# import csv
# import random
import datetime
import sateraito_logger as logging
import json
from google.appengine.ext.db.metadata import Namespace
from google.appengine.api import namespace_manager
from google.appengine.api import taskqueue
# from google.appengine.api import memcache
# from google.appengine.ext import db
from google.appengine.api import urlfetch
# import google.appengine.api.runtime
import sateraito_inc
import sateraito_func
import sateraito_page
import sateraito_db

import oem_func
# import gc
from ucf.utils.ucfutil import UcfUtil

'''
api_contract.py

@since: 2016-04-17
@version: 2016-04-17
@author: T.ASAO
'''

class _ContractPage(sateraito_page._APIPage):

	# 認証APIのMD5SuffixKey（サテライトサポート窓口アプリ）
	MD5_SUFFIX_KEY_APPSSUPPORT = '0234b04994db475facdc22e5a0351676'
	#ENCODE_KEY_APPSSUPPORT = '2a229fe1'
	#APPLICATIONID_APPSSUPPORT = 'APPSSUPPORT'

	def checkCheckKey(self, check_key, addon_id):

		md5_suffix_key = self.MD5_SUFFIX_KEY_APPSSUPPORT

		is_ok = False
		# チェックキーチェック
		if check_key != '' and md5_suffix_key != '':

			check_keys = []
			now = UcfUtil.getNow()	# 標準時
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, -5).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, -4).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, -3).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, -2).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, -1).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(now.strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, 1).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, 2).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, 3).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))
			check_keys.append(UcfUtil.md5(UcfUtil.add_minutes(now, 4).strftime('%Y%m%d%H%M') + md5_suffix_key + addon_id))

			is_ok = False
			for ck in check_keys:
				if ck.lower() == check_key.lower():
					is_ok = True
					break

		return is_ok

	def outputResult(self, return_code, params=None):
		params = {} if params is None else params

		msg = ''
		if params.has_key('errors'):
			for err in params['errors']:
				if msg != '':
					msg += '\n'
				msg += err.get('message', '')

		result = {
			'code':str(return_code)
			,'msg':msg
		}
		logging.info(result)
		return json.JSONEncoder().encode(result)


###########################################################
# API：導入テナント、ドメイン数＋ユーザー数を集計
###########################################################
class ContractAggregateGet(_ContractPage):

	def _process(self):

		return_code = 999
		params = {}
		params['errors'] = []
		try:
			check_key = self.request.get('ck', '')
			status_url = self.request.get('status_url', '')
			task_id = self.request.get('task_id', '')
			addon_id = self.request.get('addon_id', '')

			logging.info('addon_id=' + addon_id)
			logging.info('ck=' + check_key)
			logging.info('status_url=' + status_url)
			logging.info('task_id=' + task_id)

			# チェックキーチェック
			if self.checkCheckKey(check_key, addon_id) == False:
				return_code = 403
				params['errors'].append({'code': return_code, 'message': 'invalid check_key.', 'validate': ''})
				return self.outputResult(return_code, params)

			params = {
				'addon_id':addon_id,
				'status_url':status_url,
				'task_id':task_id,
			}

			# taskに追加 まるごと
			import_q = taskqueue.Queue('contract-queue')
			import_t = taskqueue.Task(
					url='/api/contract/tq/aggregate/get',
					params=params,
					target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
					countdown='0'
			)
			logging.info('run task')
			import_q.add(import_t)

			return_code = 0
			return self.outputResult(return_code, params)

		except BaseException as e:
			self.outputErrorLog(e)
			try:
				return_code = 999
				params['errors'].append({'code': return_code, 'message': 'System error occured.', 'validate': ''})
				return self.outputResult(return_code, params)
			except BaseException as e2:
				self.outputErrorLog(e2)
				return

	def doAction(self):
		return self._process()


##############################
# API：導入テナント、ドメイン数＋ユーザー数を集計（タスクキュー）
##############################
class TqContractAggregateGet(_ContractPage):

	def doAction(self):

		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return

		# 実際の連携処理
		# サテライトサポート窓口への連携

		status_url = self.request.get('status_url', '')
		addon_id = self.request.get('addon_id', '')
		task_id = self.request.get('task_id', '')
		logging.info('addon_id=' + addon_id)
		logging.info('status_url=' + status_url)
		logging.info('task_id=' + task_id)

		# seek all namespace
		lstNames = []
		q_ns = Namespace.all()
		NUM_PER_PAGE = 1000
		MAX_PAGES = 1000
		for i in range(MAX_PAGES):
			rows = q_ns.fetch(limit=NUM_PER_PAGE, offset=(i * NUM_PER_PAGE))
			if len(rows) == 0:
				break
			for row in rows:
				lstNames.append(row.namespace_name)

		# first loop
		input_users_dict = {}
		logging.info('** first loop')
		for strName in lstNames:
			logging.info('processing namespace=%s' % strName)
			if strName != '':
				namespace_manager.set_namespace(strName)
				q_users_info = sateraito_db.UserInfo.query()
				num_input_users = q_users_info.count()
				google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(strName)
				if input_users_dict.get(google_apps_domain, 0) < num_input_users:
					input_users_dict[google_apps_domain] = num_input_users

		datas = []
		num_domains = 0
		num_users_total = 0
		input_users_total = 0
		biggest_users_total = 0

		for strName in lstNames:
			google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(strName)
			if app_id is None or app_id == '' or app_id == sateraito_func.DEFAULT_APP_ID:
				logging.info('processing namespace=%s' % strName)
				sateraito_func.setNamespace(google_apps_domain, '')

				q_domain = sateraito_db.GoogleAppsDomainEntry.query()

				num_users = 0
				available_users = 0
				last_login_month = ''
				created_date = None
				# available_published_docs = ''
				available_start_date = ''
				charge_start_date = ''
				cancel_date = ''
				max_total_file_size = sateraito_db.DEFAULT_MAX_TOTAL_FILE_SIZE
				is_exist_domain = False
				for row_domain in q_domain:
					if row_domain.google_apps_domain == google_apps_domain:
						last_login_month = row_domain.last_login_month
						created_date = row_domain.created_date

						if row_domain.max_total_file_size <= sateraito_db.DEFAULT_MAX_TOTAL_FILE_SIZE:
							max_total_file_size = sateraito_db.DEFAULT_MAX_TOTAL_FILE_SIZE
						else:
							max_total_file_size = row_domain.max_total_file_size
						max_total_file_size = max_total_file_size/(1024 * 1024 * 1024)
						
						available_users = row_domain.available_users if row_domain.available_users is not None else 0
						# available_published_docs = row_domain.available_published_docs
						available_start_date = '' if row_domain.available_start_date is None or row_domain.available_start_date == '' else UcfUtil.getDateTime(row_domain.available_start_date).strftime('%Y/%m/%d')
						charge_start_date = '' if row_domain.charge_start_date is None or row_domain.charge_start_date == '' else UcfUtil.getDateTime(row_domain.charge_start_date).strftime('%Y/%m/%d')
						cancel_date = '' if row_domain.cancel_date is None or row_domain.cancel_date == '' else UcfUtil.getDateTime(row_domain.cancel_date).strftime('%Y/%m/%d')
						is_exist_domain = True
					if row_domain.google_apps_domain != '':
						num_domains += 1
					num_users += row_domain.num_users if row_domain.num_users is not None else 0
				input_users = input_users_dict.get(google_apps_domain, 0)
				biggest_users = num_users if num_users > input_users else input_users

				if is_exist_domain:
					data = {}
					data['tenant_or_domain'] = google_apps_domain
					data['created_date'] = created_date.strftime('%Y/%m/%d %H:%M:%S')
					data['num_users'] = UcfUtil.nvl(num_users)
					data['input_users'] = UcfUtil.nvl(input_users)
					data['biggest_users'] = UcfUtil.nvl(biggest_users)
					data['available_users'] = UcfUtil.nvl(available_users)
					data['available_start_date'] = available_start_date
					data['charge_start_date'] = charge_start_date
					data['cancel_date'] = cancel_date
					data['last_login_month'] = UcfUtil.nvl(last_login_month)
					# data['doc_save_terms'] = available_published_docs
					data['max_total_file_size'] = UcfUtil.nvl(max_total_file_size)
					datas.append(data)

					num_users_total += num_users
					input_users_total += input_users
					biggest_users_total += biggest_users

		results = {
			'status':'ok',
			'msg':'',
			'summary':{
					'num_domains':num_domains,
					'num_users':num_users_total,
					'input_users':input_users_total,
					'biggest_users':biggest_users_total,
				},
			'datas':datas,
		}

		now = datetime.datetime.now()
		check_key = UcfUtil.md5(addon_id + now.strftime('%Y%m%d%H%M') + self.MD5_SUFFIX_KEY_APPSSUPPORT)
		url = status_url + '?addon_id=%s&ck=%s&task_id=%s' % (UcfUtil.urlEncode(addon_id), UcfUtil.urlEncode(check_key), UcfUtil.urlEncode(task_id))

		logging.info(results)
		payload = json.JSONEncoder().encode(results)
		headers={'Content-Type': 'application/json'}
		logging.info(url)
		result = urlfetch.fetch(url=url, payload=payload, headers=headers, method='post', deadline=30, follow_redirects=True)
		if result.status_code != 200:
			logging.error(result.status_code)
		# else:
		# 	jsondata = json.JSONDecoder().decode(result.content)
		# 	logging.info(jsondata)
		#logging.info(result.content)
		logging.info('fin.')
		return make_response('',200)


###########################################################
# API：管理ユーザー一覧を取得
###########################################################
class ContractAdminUsersGet(_ContractPage):

	def _process(self):

		return_code = 999
		params = {}
		params['errors'] = []
		try:
			check_key = self.request.get('ck', '')
			status_url = self.request.get('status_url', '')
			task_id = self.request.get('task_id', '')
			addon_id = self.request.get('addon_id', '')

			logging.info('addon_id=' + addon_id)
			logging.info('ck=' + check_key)
			logging.info('status_url=' + status_url)
			logging.info('task_id=' + task_id)

			# チェックキーチェック
			if self.checkCheckKey(check_key, addon_id) == False:
				return_code = 403
				params['errors'].append({'code': return_code, 'message': 'invalid check_key.', 'validate': ''})
				return self.outputResult(return_code, params)

			params = {
				'addon_id':addon_id,
				'status_url':status_url,
				'task_id':task_id,
			}

			# taskに追加 まるごと
			import_q = taskqueue.Queue('contract-queue')
			import_t = taskqueue.Task(
					url='/api/contract/tq/adminusers/get',
					params=params,
					target=sateraito_func.getBackEndsModuleNameDeveloper('commonprocess'),
					countdown='0'
			)
			logging.info('run task')
			import_q.add(import_t)

			return_code = 0
			return self.outputResult(return_code, params)

		except BaseException as e:
			self.outputErrorLog(e)
			try:
				return_code = 999
				params['errors'].append({'code': return_code, 'message': 'System error occured.', 'validate': ''})
				return self.outputResult(return_code, params)
			except BaseException as e2:
				self.outputErrorLog(e2)
				return

	def doAction(self):
		return self._process()


##############################
# API：管理ユーザー一覧を取得（タスクキュー）
##############################
class TqContractAdminUsersGet(_ContractPage):

	def doAction(self):

		# check retry count
		retry_cnt = self.request.headers.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT']
		logging.info('retry_cnt=' + str(retry_cnt))
		if retry_cnt is not None:
			if (int(retry_cnt) > sateraito_inc.MAX_RETRY_CNT):
				logging.error('error over_' + str(sateraito_inc.MAX_RETRY_CNT) + '_times.')
				return

		# 実際の連携処理
		# サテライトサポート窓口への連携

		status_url = self.request.get('status_url', '')
		addon_id = self.request.get('addon_id', '')
		task_id = self.request.get('task_id', '')
		logging.info('addon_id=' + addon_id)
		logging.info('status_url=' + status_url)
		logging.info('task_id=' + task_id)

		# seek all namespace
		lstNames = []
		q_ns = Namespace.all()
		NUM_PER_PAGE = 1000
		MAX_PAGES = 1000
		for i in range(MAX_PAGES):
			rows = q_ns.fetch(limit=NUM_PER_PAGE, offset=(i * NUM_PER_PAGE))
			if len(rows) == 0:
				break
			for row in rows:
				lstNames.append(row.namespace_name)

		## メルマガ配信リスト取得
		#not_send_addresses, exchange_addresses_tmp = retrieveSateraitoMailMagazineList()
		## メルマガ宛先変換用ハッシュ作成
		#exchange_addresses = {}
		##for item in sateraito_mailmagazine_list.EXCHANGE_ADDRESSES:
		#for item in exchange_addresses_tmp:
		#	exchange_addresses[item[0].lower()] = item[1]

		datas = []
		for namespace_name in lstNames:
			google_apps_domain, app_id = sateraito_func.getDomainAndAppIdFromNamespaceName(namespace_name)
			if app_id is None or app_id == '' or app_id == sateraito_func.DEFAULT_APP_ID:
				logging.info('processing namespace=%s' % namespace_name)
				sateraito_func.setNamespace(google_apps_domain, '')

				# SSITE、SSOGadget対応（代理店経由のテナントにはメルマガ送らない対応）2017.01.30
				domain_entry = sateraito_db.GoogleAppsDomainEntry.getInstance(google_apps_domain)
				if domain_entry is not None and (
				domain_entry.oem_company_code is None or domain_entry.oem_company_code in oem_func.getMailMagazineTargetOEMCompanyCodes()):
					q_user = sateraito_db.GoogleAppsUserEntry.query()
					q_user = q_user.filter(sateraito_db.GoogleAppsUserEntry.is_apps_admin == True)
					for row_user in q_user:
						datas.append(row_user.user_email)

		results = {
			'status': 'ok',
			'msg': '',
			'datas': datas,
			}

		now = datetime.datetime.now()
		check_key = UcfUtil.md5(addon_id + now.strftime('%Y%m%d%H%M') + self.MD5_SUFFIX_KEY_APPSSUPPORT)
		url = status_url + '?addon_id=%s&ck=%s&task_id=%s' % (UcfUtil.urlEncode(addon_id), UcfUtil.urlEncode(check_key), UcfUtil.urlEncode(task_id))

		logging.info(results)
		payload = json.JSONEncoder().encode(results)
		headers={'Content-Type': 'application/json'}
		logging.info(url)
		result = urlfetch.fetch(url=url, payload=payload, headers=headers, method='post', deadline=30, follow_redirects=True)
		if result.status_code != 200:
			logging.error(result.status_code)
		# else:
		# 	jsondata = json.JSONDecoder().decode(result.content)
		# 	logging.info(jsondata)
		#logging.info(result.content)
		logging.info('fin.')
		return make_response('',200)


def add_url_rules(app):
	app.add_url_rule('/api/contract/aggregate/get', view_func = ContractAggregateGet.as_view('ApiContractContractAggregateGet')) # サテライトサポート窓口アプリからコール（ユーザ数などをまとめて返す）
	app.add_url_rule('/api/contract/tq/aggregate/get', view_func=TqContractAggregateGet.as_view('ApiContractTqContractAggregateGet'))
	app.add_url_rule('/api/contract/adminusers/get', view_func=ContractAdminUsersGet.as_view('ApiContractContractAdminUsersGet'))  # サテライトサポート窓口アプリからコール（管理者アドレス一覧を返す）
	app.add_url_rule('/api/contract/tq/adminusers/get', view_func=TqContractAdminUsersGet.as_view('ApiContractTqContractAdminUsersGet'))
