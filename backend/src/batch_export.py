#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
batch_export.py

Morita batch export page and program

@since: 2023-09-13
@version: 2023-09-13
@author: Tran Minh Phuc
'''

from flask import Flask, Response, render_template, request, make_response
import json
import datetime
import random
from sateraito_logger import logging

from google.appengine.api import app_identity
from google.appengine.ext import blobstore
from google.cloud import storage

from google.appengine.api import namespace_manager
from google.appengine.ext import ndb
from google.appengine.api.urlfetch import DownloadError

import sateraito_inc
import sateraito_page
import sateraito_func
import sateraito_db
import mail_queue

from sateraito_func import noneToZeroStr


def createCsvDownloadId():
	""" create new csv download id string
	"""
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


def getUserList(google_apps_domain, app_id, viewer_email, return_by_object=False):
	# SSOGadget対応
	if sateraito_db.GoogleAppsDomainEntry.isSSOGadgetTenant(google_apps_domain):
		return sateraito_func.getUserListSSOGadget(google_apps_domain, app_id, viewer_email)
	elif sateraito_db.GoogleAppsDomainEntry.isSSiteTenant(google_apps_domain):
		return sateraito_func.getUserListSSiteGadget(google_apps_domain, viewer_email)
	else:
		return _getUserListOAuth2(google_apps_domain, viewer_email, return_by_object)


def _getUserListOAuth2(google_apps_domain, viewer_email, return_by_object=False):
	# google_apps_domain = sateraito_func.getDomainPart(viewer_email)

	# 対象のGoogleAppsドメイン一覧を取得（マルチドメイン用APIがOAuthに対応していないので1ドメインずつ回して取得）
	old_namespace = namespace_manager.get_namespace()
	namespace_manager.set_namespace(google_apps_domain)  # GoogleAppsDomainEntry only exists in default namespace
	models = sateraito_db.GoogleAppsDomainEntry.query()
	domain_list = []
	for model in models:
		domain_list.append(model.google_apps_domain)

	users = []

	for target_google_apps_domain in domain_list:
		# apps service / get users in gooogle apps domain
		directory_service = sateraito_func.get_directory_service(viewer_email, google_apps_domain)
		page_token = None
		while True:
			user_list = directory_service.users().list(domain=target_google_apps_domain, pageToken=page_token).execute()
			logging.info('user_list:' + str(user_list))
			# len(user_list['users'])
			if 'users' in user_list:
				for entry in user_list['users']:
					users.append({
						'user_email': entry["primaryEmail"],
						'family_name': entry["name"]["familyName"],
						'given_name': entry["name"]["givenName"],
					})
			page_token = user_list.get("nextPageToken")
			if page_token is None:
				break

	# たしかにせっかくセットできるタイミングではあるがここではやらない
	## set number of users in domain
	# sateraito_func.setNumDomainUser(num_users=len(users), google_apps_domain=target_google_apps_domain)

	if return_by_object:
		namespace_manager.set_namespace(old_namespace)
		return users
	# return json data
	jsondata = json.JSONEncoder().encode(users)
	namespace_manager.set_namespace(old_namespace)
	return jsondata


class TqCreateAllUsersCsv(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" Create csv file for importing UserInfo of all GoogleApps users
	"""

	def doAction(self, google_apps_domain, app_id, csv):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return

		admin_email = self.request.get('admin_email')

		other_setting = sateraito_db.OtherSetting.getInstance(auto_create=True)
		csv_fileencoding = sateraito_func.getFileEncoding(other_setting.csv_fileencoding)
		csv_download_id = createCsvDownloadId()

		logging.info('start creating csv admin_email=' + admin_email)

		csv_string = ''

		# csv header
		csv_string += sateraito_db.UserInfo.getExportCsvHeader()

		# get all users
		try:
			users = getUserList(google_apps_domain, app_id, admin_email, return_by_object=True)
		except DownloadError as instance:
			logging.warn('Gdata request timeout')
			return make_response('', 200)
		# create csv rows for each users
		for p in users:
			user_email_lower = str(p['user_email']).lower()

			q = sateraito_db.UserInfo.query()
			q = q.filter(sateraito_db.UserInfo.email == user_email_lower)


			row = q.get()
			if row is None:
				export_line = u'IU'
				export_line += u',' + str(p['user_email']).lower().decode()
				export_line += u',' + p['family_name'].decode()
				export_line += u',' + p['given_name'].decode()
				export_line += ','  # family_name_kana
				export_line += ','  # employee_id
				export_line += ','  # company_name
				export_line += ','  # department_1
				export_line += ','  # department_2
				export_line += ','  # department_3
				export_line += ','  # department_4
				export_line += ','  # job_title
				export_line += ','  # department_code
				export_line += ','  # company_email_1
				export_line += ','  # company_email_2
				export_line += ','  # personal_email_1
				export_line += ','  # personal_email_2
				export_line += ','  # company_phone_number_1
				export_line += ','  # company_extension_number_1
				export_line += ','  # company_phone_number_2
				export_line += ','  # personal_phone_number_1
				export_line += ','  # personal_phone_number_2
				export_line += ','  # mail_group
				export_line += ','  # language
				export_line += '\r\n'
				# export_line = washShiftJISErrorChar(export_line)
				export_line = sateraito_func.washErrorChar(export_line, csv_fileencoding)
			else:
				export_line = u'IU'
				export_line += ',' + noneToZeroStr(row.email)
				if row.family_name is not None and row.family_name != '':
					export_line += ',' + noneToZeroStr(row.family_name)
				else:
					export_line += ',' + p['family_name'].decode()
				if row.given_name is not None and row.given_name != '':
					export_line += ',' + noneToZeroStr(row.given_name)
				else:
					export_line += ',' + p['given_name'].decode()
				export_line += ',' + noneToZeroStr(row.family_name_kana)
				export_line += ',' + noneToZeroStr(row.given_name_kana)
				export_line += ',' + noneToZeroStr(row.employee_id)
				export_line += ',' + noneToZeroStr(row.company_name)
				export_line += ',' + noneToZeroStr(row.department_1)
				export_line += ',' + noneToZeroStr(row.department_2)
				export_line += ',' + noneToZeroStr(row.department_3)
				export_line += ',' + noneToZeroStr(row.department_4)
				export_line += ',' + noneToZeroStr(row.job_title)
				export_line += ',' + noneToZeroStr(row.department_code)
				export_line += ',' + noneToZeroStr(row.company_email_1)
				export_line += ',' + noneToZeroStr(row.company_email_2)
				export_line += ',' + noneToZeroStr(row.personal_email_1)
				export_line += ',' + noneToZeroStr(row.personal_email_2)
				export_line += ',' + noneToZeroStr(row.company_phone_number_1)
				export_line += ',' + noneToZeroStr(row.company_extension_number_1)
				export_line += ',' + noneToZeroStr(row.company_phone_number_2)
				export_line += ',' + noneToZeroStr(row.personal_phone_number_1)
				export_line += ',' + noneToZeroStr(row.personal_phone_number_2)
				export_line += ',' + noneToZeroStr(' '.join(row.mail_group))
				export_line += ',' + noneToZeroStr(row.language)
				export_line += '\r\n'
				# export_line = washShiftJISErrorChar(export_line)
				export_line = sateraito_func.washErrorChar(export_line, csv_fileencoding)
			# csv_string += export_line.encode('cp932')
			csv_string += export_line.encode(csv_fileencoding)

		### save csv data to datastore

		# devide csv data
		# CAUTION: Datastore entity can have only 1MB data per entity
		#          so you have to devide data if it is over 1MB
		csv_data_length = len(csv_string)
		csv_datas = []
		NUM_STRING_PER_ENTITY = 1000 * 900  # 800 KB
		number_of_entity = (csv_data_length // NUM_STRING_PER_ENTITY) + 1
		for i in range(0, number_of_entity):
			start_index = i * NUM_STRING_PER_ENTITY
			end_index = start_index + NUM_STRING_PER_ENTITY
			csv_datas.append(csv_string[start_index:end_index])

		# store data to datastore
		csv_filename = 'all-users-export-electronic-storage.csv'
		expire_date = datetime.datetime.now() + datetime.timedelta(days=1)  # csv download expires in 24 hours
		for i in range(0, number_of_entity):
			new_data = sateraito_db.CsvDownloadData()
			new_data.csv_data = csv_datas[i]
			new_data.data_order = i
			new_data.csv_download_id = csv_download_id
			new_data.expire_date = expire_date
			new_data.csv_filename = csv_filename
			new_data.csv_fileencoding = csv_fileencoding
			new_data.put()

		### send csv download url email to admin

		# register task queue to send email
		message_body = u''
		message_body += u'ダウンロード用の全ユーザーCSVファイルの準備が完了しました。\n'
		message_body += u'下記URLよりダウンロードすることができます。\n'
		message_body += u'\n'
		message_body += sateraito_func.getMySiteURL(google_apps_domain, request.url) + '/' + google_apps_domain + '/csv/downloadexportdata/' + csv_download_id
		message_body += u'\n'
		message_body += u'\n'
		message_body += u'このURLは24時間後に無効になります。\n'
		message_body += u'\n'
		message_body += u'\n'
		message_body += u'＜ご注意＞\n'
		message_body += u'このメールは行先予定/在席確認/伝言メモ/共有TODOのシステムメールアドレスより、自動\n'
		message_body += u'送信されております。このメールに返信されないようにお願いします。\n'
		message_body += u'\n'
		message_body += u'\n'
		message_body += u'===========================================\n'
		message_body += u'サテライトオフィス・行先予定/在席確認/伝言メモ/共有TODO for GSuite\n'
		message_body += u'   http://www.sateaito.jp/\n'
		message_body += u'===========================================\n'

		mail_queue.addQueue2(sender=sateraito_inc.MESSAGE_SENDER_EMAIL,
		                     subject='ダウンロード用CSVファイルの準備ができました',
		                     to=admin_email,
		                     body=message_body)

		return make_response('', 200)


class DownloadExportData(sateraito_page.Handler_Basic_Request, sateraito_page._OidBasePage, blobstore.BlobstoreDownloadHandler):
	""" download csv data which is stored in CsvDownloadData
	"""

	def doAction(self, google_apps_domain, app_id, csv, csv_download_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check openid request
		is_ok, body_for_not_ok = self.oidAutoLogin(google_apps_domain)
		if not is_ok:
			return body_for_not_ok

		q = sateraito_db.CsvDownloadData.query()
		q = q.filter(sateraito_db.CsvDownloadData.csv_download_id == csv_download_id)
		q = q.order(sateraito_db.CsvDownloadData.created_date)
		# q.filter('csv_download_id =', csv_download_id)
		# q.order('data_order')
		first_row = q.get()
		if first_row is None:
			logging.warn('wrong url to download csv viewer_email=' + self.viewer_email + ' csv_download_id=' + csv_download_id)
			return make_response('wrong url to download csv', 200)
		if first_row.expire_date < datetime.datetime.now():
			logging.warn('csv download data expired: viewer_email=' + self.viewer_email + ' csv_download_id=' + csv_download_id)
			return make_response('wrong url to download csv', 200)

		csv_file_encoding = sateraito_func.getFileEncoding(first_row.csv_fileencoding)
		csv_filename = first_row.csv_filename

		# data = []
		# rows = q.fetch(limit=1000)
		# if len(rows) > 0:
		# 	# set response headers
		# 	self.setResponseHeader('Cache-Control', 'public')
		# 	self.setResponseHeader('Content-Type', 'application/x-csv; charset=' + str(csv_fileencoding))
		# 	self.setResponseHeader('Content-Disposition', 'attachment; filename=' + str(rows[0].csv_filename))
		# 	for row in rows:
		# 		data.append(row.csv_data.decode())
		# 		data.append("\r\n")
		#
		# return ''.join(data)
	
		keys = q.fetch(keys_only=True)
		if len(keys) > 0:
			# set response headers
			self.setResponseHeader('Cache-Control', 'public')
			self.setResponseHeader('Content-Type', 'application/x-csv; charset=' + str(csv_file_encoding))
			self.setResponseHeader('Content-Disposition', 'attachment; filename=' + str(csv_filename))
			logging.info('filename=' + str(csv_filename))
			
			if len(keys) > 32:
				# big file case
				# self.response.out.write HAVE HARD LIMIT 32MB: unable to send response over 32MB
				# use Blobstore to export data over 32MB
				
				# # step1. create csv file on Google Cloud Storage
				filename = google_apps_domain + '_' + app_id + '_' + csv_download_id + '.csv'
				gcs_bucket_name = app_identity.get_default_gcs_bucket_name()
				gcs_filename = google_apps_domain + sateraito_func.DELIMITER_NAMESPACE_DOMAIN_APP_ID + app_id + '/csv_export_temp/' + filename
				blobstore_filename = '/gs/' + gcs_bucket_name + '/' + gcs_filename
				
				storage_client = storage.Client()
				bucket = storage_client.bucket(gcs_bucket_name)
				blob = storage.Blob(gcs_filename, bucket)
				
				with blob.open("wb") as gcs_file:
					for key in keys:
						row = key.get()
						gcs_file.write(row.csv_data)
				
				# step2. create key for blobstore_handlers and send response using seld_blob
				# Blobstore API requires extra /gs to distinguish against blobstore files.
				# blobstore_filename = '/gs' + fullpath_filename
				gcs_blob_key = blobstore.create_gs_key(blobstore_filename)
				return self.send_blob_file(self.send_blob, gcs_blob_key)
			else:
				# normal case
				for key in keys:
					row = key.get()
					self.response.out.write(row.csv_data)
			# return row.csv_data


class TqExportAllUsersCsv(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" Create csv file for importing UserInfo of all GoogleApps users
	"""

	def doAction(self, google_apps_domain, app_id, csv):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return

		admin_email = self.request.get('admin_email')
		request_token = self.request.get('request_token')
		logging.info('request_token=' + str(request_token))

		other_setting = sateraito_db.OtherSetting.getInstance(auto_create=True)
		csv_fileencoding = sateraito_func.getFileEncoding(other_setting.csv_fileencoding)
		csv_download_id = createCsvDownloadId()

		logging.info('start export csv admin_email=' + admin_email)

		tq_q = sateraito_db.CsvTaskQueue.query()
		tq_q = tq_q.filter(sateraito_db.CsvTaskQueue.request_token == request_token)
		tq_entry = tq_q.get()
		# TODO tq_entry存在チェック

		csv_string = ''

		# csv header
		csv_string += sateraito_db.UserInfo.getExportCsvHeader()

		# get all users
		try:
			users = getUserList(google_apps_domain, app_id, admin_email, return_by_object=True)
		except DownloadError as instance:
			logging.warn('Gdata request timeout')
			return
		# create csv rows for each users
		for p in users:
			user_email_lower = str(p['user_email']).lower()
			row = sateraito_db.UserInfo.getInstance(user_email_lower)
			if row is None:
				export_line = u'IU'
				export_line += ',' + noneToZeroStr(p['user_email'])
				export_line += ',' + noneToZeroStr(p['family_name'])
				export_line += ',' + noneToZeroStr(p['given_name'])
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += ','
				export_line += '\r\n'
				# export_line = washShiftJISErrorChar(export_line)
				export_line = sateraito_func.washErrorChar(export_line, sateraito_func.getFileEncoding(csv_fileencoding))
			else:
				export_line = u'IU'
				export_line += ',' + noneToZeroStr(row.email)
				if row.family_name is not None and row.family_name != '':
					export_line += ',' + noneToZeroStr(row.family_name)
				else:
					export_line += ',' + noneToZeroStr(p['family_name'])
				if row.given_name is not None and row.given_name != '':
					export_line += ',' + noneToZeroStr(row.given_name)
				else:
					export_line += ',' + noneToZeroStr(p['given_name'])
				export_line += ',' + noneToZeroStr(row.family_name_kana)
				export_line += ',' + noneToZeroStr(row.given_name_kana)
				export_line += ',' + noneToZeroStr(row.employee_id)
				export_line += ',' + noneToZeroStr(row.company_name)
				export_line += ',' + noneToZeroStr(row.department_1)
				export_line += ',' + noneToZeroStr(row.department_2)
				export_line += ',' + noneToZeroStr(row.department_3)
				export_line += ',' + noneToZeroStr(row.department_4)
				export_line += ',' + noneToZeroStr(row.job_title)
				export_line += ',' + noneToZeroStr(row.department_code)
				export_line += ',' + noneToZeroStr(row.company_email_1)
				export_line += ',' + noneToZeroStr(row.company_email_2)
				export_line += ',' + noneToZeroStr(row.personal_email_1)
				export_line += ',' + noneToZeroStr(row.personal_email_2)
				export_line += ',' + noneToZeroStr(row.company_phone_number_1)
				export_line += ',' + noneToZeroStr(row.company_extension_number_1)
				export_line += ',' + noneToZeroStr(row.company_phone_number_2)
				export_line += ',' + noneToZeroStr(row.personal_phone_number_1)
				export_line += ',' + noneToZeroStr(row.personal_phone_number_2)
				export_line += ',' + noneToZeroStr(' '.join(row.mail_group))
				export_line += ',' + noneToZeroStr(row.language)
				export_line += '\r\n'
				# export_line = washShiftJISErrorChar(export_line)
				export_line = sateraito_func.washErrorChar(export_line, sateraito_func.getFileEncoding(csv_fileencoding))
			# csv_string += export_line.encode('cp932')
			csv_string += export_line

		# save csv data to datastore
		# csv_string = str(csv_string)
		# csv_string = sateraito_func.washShiftJISErrorChar(csv_string)
		csv_string = sateraito_func.encodeString(csv_string, csv_fileencoding=csv_fileencoding, type_import=False)
		# csv_string = csv_string.encode('cp932')    #Shift_JIS変換

		csv_string = csv_string.encode(csv_fileencoding)  # Shift_JIS変換

		# devide csv data
		# CAUTION: Datastore entity can have only 1MB data per entity
		#          so you have to devide data if it is over 1MB
		csv_data_length = len(csv_string)
		csv_datas = []
		NUM_STRING_PER_ENTITY = 1000 * 900  # 800 KB
		number_of_entity = (csv_data_length // NUM_STRING_PER_ENTITY) + 1
		for i in range(0, number_of_entity):
			start_index = i * NUM_STRING_PER_ENTITY
			end_index = start_index + NUM_STRING_PER_ENTITY
			csv_datas.append(csv_string[start_index:end_index])

		# store data to datastore
		csv_filename = 'all-users-export-electronic-storage.csv'
		expire_date = datetime.datetime.now() + datetime.timedelta(days=1)  # csv download expires in 24 hours
		for i in range(0, number_of_entity):
			new_data = sateraito_db.CsvDownloadData()
			new_data.csv_data = csv_datas[i]
			new_data.data_order = i
			new_data.csv_download_id = csv_download_id
			new_data.expire_date = expire_date
			new_data.csv_filename = csv_filename
			new_data.csv_fileencoding = csv_fileencoding
			new_data.put()

		download_url = sateraito_func.getMySiteURL(google_apps_domain,
		                                           self.request.url) + '/' + google_apps_domain + '/' + app_id + '/exportcsv/' + csv_download_id

		if tq_entry:
			tq_entry.status = 'SUCCESS'
			tq_entry.deal_status = 'FIN'
			tq_entry.download_url = download_url
			tq_entry.expire_date = expire_date
			tq_entry.csv_download_id = csv_download_id
			tq_entry.put()

		# # logging
		# detail = u'csv_download_id=' + csv_download_id
		# detail += u' msg=export_csv_all_userinfo'
		# detail += u' success=true'
		# sateraito_db.OperationLog.addLogForImportCSV(admin_email, admin_email, sateraito_db.OPERATION_EXPORT_CSV, sateraito_db.SCREEN_ADMIN_CONSOLE, csv_download_id, detail=detail)

		return make_response('', 200)


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/<string:csv>/downloadexportdata/<string:csv_download_id>',
									 view_func=DownloadExportData.as_view('BatchExportDownloadExportData'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/<string:csv>/tq/createalluserscsv',
									 view_func=TqCreateAllUsersCsv.as_view('BatchExportTqCreateAllUsersCsv'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/<string:csv>/tq/exportalluserscsv',
									 view_func=TqExportAllUsersCsv.as_view('BatchExportTqExportAllUsersCsv'))
