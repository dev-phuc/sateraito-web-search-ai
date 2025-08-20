#!/usr/bin/python
# coding: utf-8

__author__ = 'T.ASAO <asao@sateraito.co.jp>'

# set default encodeing to utf-8
from flask import render_template, request, make_response
import os
# import urllib
# import csv
# import random
# import datetime
# from StringIO import StringIO
from sateraito_logger import logging
import json
import base64
# from dateutil import zoneinfo, tz
# from google.appengine.api import namespace_manager
# from google.appengine.api import taskqueue
# from google.appengine.api import memcache
from google.appengine.ext import blobstore
# from google.appengine.ext import ndb
import sateraito_inc
import sateraito_func
import sateraito_page
import sateraito_db
import oem_func

from ucf.utils.ucfutil import UcfUtil

'''
api.py

@since: 2012-10-17
@version: 2014-03-02
@author: T.ASAO
'''

###########################################################
# API：契約管理システムからの契約情報を受けてセット
# …利用開始日、課金開始日、解約日
###########################################################
class SetContractInfo(sateraito_page._APIPage):
	MD5_SUFFIX_KEY = '6a8a0a5a5bf94c95aa0f39d0eedbe71e'    # 全アドオン共通.変更不可

	# チェックキーチェック
	def _checkCheckKey(self, google_apps_domain, check_key):
		is_ok = False

		# MD5SuffixKey
		md5_suffix_key = self.MD5_SUFFIX_KEY

		# チェックキーチェック
		if google_apps_domain != '' and check_key != '' and md5_suffix_key != '':
			google_apps_domain = google_apps_domain.lower()
			domain_check_keys = []
			now = UcfUtil.getNow()  # 標準時
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, -5).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, -4).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, -3).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, -2).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, -1).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(UcfUtil.md5(google_apps_domain + now.strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, 1).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, 2).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, 3).strftime('%Y%m%d%H%M') + md5_suffix_key))
			domain_check_keys.append(
				UcfUtil.md5(google_apps_domain + UcfUtil.add_minutes(now, 4).strftime('%Y%m%d%H%M') + md5_suffix_key))

			is_ok = False
			for domain_check_key in domain_check_keys:
				if domain_check_key.lower() == check_key.lower():
					is_ok = True
					break
		return is_ok

	def _process(self, google_apps_domain):
		# set namespace
		sateraito_func.setNamespace(google_apps_domain, '')

		return_code = 999
		params = {'errors': []}

		try:
			#			self._approot_path = os.path.dirname(__file__)

			check_key = self.request.get('ck', '')
			available_start_date = self.request.get('available_start_date', '')  # 利用開始日（YYYY/MM/DD 形式）
			charge_start_date = self.request.get('charge_start_date', '')  # 課金開始日（YYYY/MM/DD 形式）
			cancel_date = self.request.get('cancel_date', '')  # 解約日（YYYY/MM/DD 形式）
			doc_save_terms = self.request.get('doc_save_terms', '')  # 文書保存年数（1～、、、Unlimited=999）
			contract_platform = self.request.get('contract_platform', '')  # 種別（APPS or O365 or SALESFORCE or EXCLUSIVE or ...)
			guarantee_trial_term = self.request.get('guarantee_trial_term', '')  # トライアル期間を保証する場合…on
			is_no_oem = self.request.get('is_no_oem', '') == 'on'  # GWS版契約管理対応…OEM版アドオンのサテライト直契約パターンフラグ 直契約…on
			logging.info('is_no_oem=%s' % (is_no_oem))

			# チェックキーチェック
			is_check_ok = self._checkCheckKey(google_apps_domain, check_key)
			if not is_check_ok:
				return_code = 403
				params['errors'].append({'code': return_code, 'message': 'invalid check_key.', 'validate': ''})
				return self.outputResult(return_code, params)

			# ドメインエントリー取得
			q = sateraito_db.GoogleAppsDomainEntry.query()
			q = q.filter(sateraito_db.GoogleAppsDomainEntry.google_apps_domain == google_apps_domain.lower())
			domain_row = q.get()
			if domain_row is None:
				return_code = 403
				params['errors'].append({'code': return_code, 'message': 'invalid google apps domain.', 'validate': ''})
				return self.outputResult(return_code, params)

			# platformチェック: サテライトポータルサイト、SSO認証版契約情報をGoogle Workspace 版にセットしないようにする制御
			if not oem_func.isValidSPCodeByContractPlatform(contract_platform, domain_row.sp_code):
				return_code = 403
				params['errors'].append(
					{'code': return_code, 'message': 'this tenant or domain is not on the platform.', 'validate': ''})
				return self.outputResult(return_code, params)
			# OEM版アドオンの直契約対応…サテライト直契約のG Suiteアドオンは契約管理で管理しないためKDDI版契約管理からの情報がセットされないようにスキップ（KDDI版のLINE WORKSアドオンなどはないが一応sp_codeもチェック） 2021.02.19

			# TODO GWS版契約管理対応…OEM版アドオンのサテライト直契約パターンも契約管理で管理するようになるのでタイミングを見てここのロジックを変更
			# if sateraito_inc.appspot_domain == 'kddi-electronic-storage' and domain_row.is_no_oem and (domain_row.sp_code is None or domain_row.sp_code == '' or domain_row.sp_code == oem_func.SP_CODE_GSUITE):
			if sateraito_inc.appspot_domain == 'kddi-electronic-storage' and is_no_oem != sateraito_func.noneToFalse(domain_row.is_no_oem) and (domain_row.sp_code is None or domain_row.sp_code == '' or domain_row.sp_code == oem_func.SP_CODE_GSUITE):
				return_code = 403
				params['errors'].append({'code': return_code, 'message': 'no_oem_tenant.', 'validate': ''})
				return self.outputResult(return_code, params)

			# 課金開始日から有償モード、無償モードを自動切り替え（契約管理システムから連携していないドメイン、テナントは制御したくないため、ここでフラグを上書き）
			if charge_start_date != '':
				domain_row.is_free_mode = UcfUtil.set_time(UcfUtil.getNowLocalTime(), 0, 0, 0) < UcfUtil.set_time(UcfUtil.getDateTime(charge_start_date), 0, 0, 0)

			# 契約管理から連携される解約日にかかわらず、インストールから30日間は使えるようにする対応 2017.10.20
			if guarantee_trial_term == 'on' and cancel_date != '':
				trial_expire = UcfUtil.set_time(UcfUtil.add_days(domain_row.created_date, 30), 0, 0, 0)
				if trial_expire > UcfUtil.getDateTime(cancel_date):
					cancel_date = trial_expire.strftime('%Y/%m/%d')
			logging.info('cancel_date=' + cancel_date)

			# 文書保存期間を更新
			if doc_save_terms != '':
				domain_row.doc_save_terms = UcfUtil.toInt(doc_save_terms)

			domain_row.available_start_date = available_start_date
			domain_row.charge_start_date = charge_start_date
			domain_row.cancel_date = cancel_date
			domain_row.is_no_oem = is_no_oem					# TODO GWS版契約管理対応…OEM版アドオンのサテライト直契約パターンも契約管理で管理するようになるのでタイミングを見てコメントアウトを外す
			domain_row.put()

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

	def outputResult(self, return_code, params=None):
		params = {} if params is None else params

		msg = ''
		if 'errors' in params:
			for err in params['errors']:
				if msg != '':
					msg += '\n'
				msg += err.get('message', '')

		result = {
			'code': str(return_code),
			'msg': msg
		}
		return json.JSONEncoder().encode(result)

	@sateraito_func.convert_result_none_to_empty_str
	def post(self, google_apps_domain):
		return self._process(google_apps_domain)


API_GET_ATTACH_FILE_ALLOWD_IP_ADDRESS = ['34.84.158.140', '::1']


class GetAttachFile(sateraito_page._APIPage, blobstore.BlobstoreDownloadHandler):

	def _process(self, tenant_or_domain, app_id, file_id, token):
		# set namespace
		sateraito_func.setNamespace(tenant_or_domain, app_id)

		# check remote address
		remote_addr = os.environ.get('REMOTE_ADDR', '')
		logging.info('remote_addr=' + str(remote_addr))
		if remote_addr not in API_GET_ATTACH_FILE_ALLOWD_IP_ADDRESS:
			logging.error('server ip address not allowd:' + str(remote_addr))
			return make_response('', 403)
		# get params
		logging.info('file_id=' + str(file_id))
		logging.info('token=' + str(token))

		# check attach keyword function enabled
		if not sateraito_func.isEnableAttachFileKeywordSearchFunction(tenant_or_domain, app_id):
			logging.error('attach file keyword search function not enabled')
			return make_response('', 403)
		# get AttachedFile2 entry and check token
		row = sateraito_db.FileflowDoc.getInstance(file_id)
		if row is None:
			logging.error('FileflowDoc not found')
			return make_response('', 403)

		if row.file_pull_url_expire_date is None or row.file_pull_url_token is None:
			logging.error('FileflowDoc not allowed api download file_pull_url_expire_date=' + str(row.file_pull_url_expire_date) + ' file_pull_url_token=' + str(row.file_pull_url_token))
			return make_response('', 403)
		if row.file_pull_url_token != token:
			logging.error('wrong token=' + str(token) + ' row.file_pull_url_token=' + str(row.file_pull_url_token))
			return make_response('', 403)
		# if sateraito_func.isBiggerDate(datetime.datetime.now(), row.file_pull_url_expire_date):
		# 	logging.error('token expired row.file_pull_url_expire_date=' + str(row.file_pull_url_expire_date))
		# 	self.response.status = 403
		# 	return

		file_name = row.file_name
		mime_type = row.mime_type

		# ファイル名の整備
		file_name = sateraito_func.normalizeFileName(file_name)

		# 機種依存文字対策 2017.11.02
		file_name = sateraito_func.removeInvalidUnicodeChar(file_name)
		filename = base64.b64encode(str(file_name).encode('utf8'))

		# set headers
		# self.setResponseHeader('Cache-Control', 'public')
		# self.setResponseHeader('Content-Control', 'public')
		# self.setResponseHeader('Content-Disposition', self.createContentDispositionUtf8(file_name, type='attachment'))  # 'attachment; filename="=?utf-8?B?' + str(filename) + '?="')
		# self.setResponseHeader('Content-Type', str(mime_type) + '; charset=utf-8')

		options = {
			'Cache-Control': 'public',
			'Content-Control': 'public',
			'Content-Disposition': 'attachment; filename="=?utf-8?B?' + filename.decode() + '?="',
			# 'Content-Disposition': self.createContentDispositionUtf8(file_name, type='attachment'),
			'Content-Type': str(mime_type) + '; charset=utf-8',
		}

		# export blob data
		blob_key = None
		if row.cloud_storage:
			blob_key = row.blob_key_cloud
			logging.info("blob_key_cloud=%s" % blob_key)
		else:
			blob_key = row.blob_key
			logging.info("blob_key=%s" % blob_key)

		return self.send_blob_file(self.send_blob, blob_key, options=options)

	def doAction(self, tenant_or_domain, app_id, file_id, token):
		return self._process(tenant_or_domain, app_id, file_id, token)


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/api/setcontractinfo',
									 view_func=SetContractInfo.as_view('ApiSetContractInfo'))
	app.add_url_rule('/<string:tenant_or_domain>/<string:app_id>/api/getattachfile/<string:file_id>/<string:token>',
									 view_func=GetAttachFile.as_view('ApiGetAttachFile'))
