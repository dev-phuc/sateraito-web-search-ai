#!/usr/bin/python
# coding: utf-8

__author__ = 'Akitoshi Abe <abe@baytech.co.jp>'

# set default encodeing to utf-8
import json
from sateraito_logger import logging
import datetime

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page

from google.appengine.api import namespace_manager

from sateraito_func import toUtcTime

'''
operationlog.py

@since: 2013-08-01
@version: 2013-09-14
@author: Akitoshi Abe
'''

def getNameOperation(key_name, my_lang):
	if key_name == 'download_file':
		return my_lang.getMsg('TXT_DOWNLOAD_FILE')
	elif key_name == 'upload_file':
		return my_lang.getMsg('TXT_UPLOAD_FILE')
	elif key_name == 'delete_file':
		return my_lang.getMsg('TXT_DELETE_FILE')
	elif key_name == 'create_folder':
		return my_lang.getMsg('TXT_CREATE_FOLDER')
	elif key_name == 'update_folder':
		return my_lang.getMsg('TXT_UPDATE_FOLDER')
	elif key_name == 'delete_folder':
		return my_lang.getMsg('TXT_DELETE_FOLDER')
	elif key_name == 'move_folder':
		return my_lang.getMsg('TXT_UPDATE_FOLDER')
	elif key_name == 'copy_folder':
		return my_lang.getMsg('TXT_UPDATE_FOLDER')
	elif key_name == 'create_categorie':
		return my_lang.getMsg('OPERATION_CREATE_CATEGORIE')
	elif key_name == 'update_categorie':
		return my_lang.getMsg('OPERATION_UPDATE_CATEGORIE')
	elif key_name == 'delete_categorie':
		return my_lang.getMsg('OPERATION_DELETE_CATEGORIE')
	elif key_name == 'create_workflow_doc':
		return my_lang.getMsg('TXT_CREATE_DOC')
	elif key_name == 'update_workflow_doc':
		return my_lang.getMsg('TXT_UPDATE_DOC')
	elif key_name == 'delete_workflow_doc':
		return my_lang.getMsg('TXT_DELETE_DOC')
	elif key_name == 'import_csv':
		return my_lang.getMsg('OPERATION_IMPORT_CSV')
	elif key_name == 'export_csv':
		return my_lang.getMsg('OPERATION_EXPORT_CSV')
	else:
		return ''

def getNameScreen(key_screen, my_lang):
	if key_screen == 'admin_console':
		return my_lang.getMsg('SCREEN_ADMIN_CONSOLE')
	elif key_screen == 'user_console':
		return my_lang.getMsg('SCREEN_USER_CONSOLE')
	elif key_screen == 'direct_link':
		return my_lang.getMsg('SCREEN_DIRECT_LINK')
	elif key_screen == 'popup_file_upload':
		return my_lang.getMsg('SCREEN_POPUP_FILE_UPLOAD')
	else:
		return ''

class _GetOperationLogListAdmin(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	
	def getRows(self, email, screen, from_date_localtime_raw, to_date_localtime_raw, operation):
		q = sateraito_db.OperationLog.query()
		# from_date
		if from_date_localtime_raw.strip() == '':
			pass
		else:
			from_date_localtime = None
			f_splited = from_date_localtime_raw.split(' ')
			if len(f_splited) == 1:
				# in case YYYY-MM-DD
				from_date_localtime = datetime.datetime.strptime(from_date_localtime_raw + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
			else:
				# in case YYYY-MM-DD HH:MI
				from_date_localtime = datetime.datetime.strptime(from_date_localtime_raw + ':00', '%Y-%m-%d %H:%M:%S')
			from_date_utc = toUtcTime(from_date_localtime)
			q = q.filter(sateraito_db.OperationLog.operation_date >= from_date_utc)
		# to_date
		if to_date_localtime_raw.strip() == '':
			pass
		else:
			to_date_localtime = None
			t_splited = to_date_localtime_raw.split(' ')
			if len(t_splited) == 1:
				# in case YYYY-MM-DD
				to_date_localtime = datetime.datetime.strptime(to_date_localtime_raw + ' 00:00:00', '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=1)
			else:
				# in case YYYY-MM-DD HH:MI
				to_date_localtime = datetime.datetime.strptime(to_date_localtime_raw + ':00', '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=1)
			to_date_utc = toUtcTime(to_date_localtime)
			q = q.filter(sateraito_db.OperationLog.operation_date < to_date_utc)
		# email
		if email != '':
			q = q.filter(sateraito_db.OperationLog.user_email == email)
		# screen
		if screen != '' and screen != '__not_set':
			q = q.filter(sateraito_db.OperationLog.screen == screen)
		# operation
		if operation != '' and operation != '__not_set':
			q = q.filter(sateraito_db.OperationLog.operation == operation)
		# sort order
		q = q.order(-sateraito_db.OperationLog.operation_date)
		NUM_PER_PAGE = 1000
		# fetch page of data
		rows = q.fetch(limit=NUM_PER_PAGE)
		# check if data exists in next page
		have_more_rows = False
		rows2 = q.fetch(limit=1, offset=NUM_PER_PAGE)
		if len(rows2) > 0:
			have_more_rows = True
		return rows, have_more_rows

class __GetOperationLogListAdmin(_GetOperationLogListAdmin):
	""" Get list of all doc types in system
		for admin only
	"""
	
	def process(self, google_apps_domain, app_id):
		# check if user workflow admin
		if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
			return
		
		# get params
		from_date_localtime_raw = self.request.get('from_date')
		to_date_localtime_raw = self.request.get('to_date')
		operation = self.request.get('operation')
		screen = self.request.get('screen')
		email = self.request.get('email')

		# set response header
		self.setResponseHeader('Content-Type', 'application/json')

		# get data
		rows, have_more_rows = self.getRows(email, screen, from_date_localtime_raw, to_date_localtime_raw, operation)
		results = []
		for row in rows:
			results.append({
						'operation_date': str(sateraito_func.toShortLocalTime(row.operation_date)),
						'user_email': row.user_email,
						'operation': row.operation,
						'screen': row.screen,
						'folder_name': row.full_path_folder,
						'file_name': row.file_name,
						'file_id': row.file_id,
						'list_file_id': row.list_file_id,
						'list_file_name': row.list_file_name,
						'workflow_doc_id': row.workflow_doc_id,
						'doc_title': row.workflow_doc_title,
						'detail': row.detail,
						})

		json_data = json.JSONEncoder().encode({
			'results': results,
			'have_more_rows': have_more_rows,
		})
		if sateraito_inc.debug_mode:
			logging.info(json_data)
		return json_data

class GetOperationLogListAdmin(__GetOperationLogListAdmin):
	""" Get list of all doc types in system
		for admin only
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkGadgetRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)

class GetOperationLogListAdminOid(__GetOperationLogListAdmin):
	""" Get list of all doc types in system
		for admin only
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return

		return self.process(google_apps_domain, app_id)


class ExportOperationLogListCsvAdmin(_GetOperationLogListAdmin):
	""" Get list of all doc types in system
		for admin only
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return
		logging.info("namespace_manager=" + namespace_manager.get_namespace())
		# token check
		if not self.checkToken(google_apps_domain):
			return
		# check if user workflow admin
		if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
			return
		logging.info("namespace_manager=" + namespace_manager.get_namespace())
		
		# get params
		from_date_localtime_raw = self.request.get('from_date', '')
		to_date_localtime_raw = self.request.get('to_date', '')
		operation = self.request.get('operation', '')
		screen = self.request.get('screen', '')
		email = self.request.get('email', '')
		lang = self.request.get('lang', sateraito_inc.DEFAULT_LANGUAGE)
		my_lang = sateraito_func.MyLang(lang)

		othersetting_dict = sateraito_db.OtherSetting.getDict(auto_create=True)
		csv_file_encoding = othersetting_dict['csv_file_encoding']

		csv_file_encoding = sateraito_func.getFileEncoding(csv_file_encoding)
		csv_file_encoding = csv_file_encoding.encode(csv_file_encoding)  # Shift_JIS変換

		# set response header
		self.setResponseHeader('Cache-Control', 'public')
		self.setResponseHeader('Content-Type', 'application/x-csv; charset=' + str(csv_file_encoding))
		self.setResponseHeader('Content-Disposition', 'attachment; filename=operation_log.csv')

		# get data
		rows, have_more_rows = self.getRows(email, screen, from_date_localtime_raw, to_date_localtime_raw, operation)

		csv_string = ''
		# csv header
		csv_string += 'operation_date,user_email,operation,screen,folder_name,file_name,workflow_doc_title'
		csv_string += '\r\n'

		# csv body
		for row in rows:
			# operation_date
			operation_date = str(sateraito_func.toShortLocalTime(row.operation_date))
			csv_string += operation_date
			# user_email
			user_email = str(sateraito_func.noneToZeroStr(row.user_email))
			csv_string += ',"' + user_email + '"'
			# operation
			operation = str(sateraito_func.noneToZeroStr(row.operation))
			csv_string += ',"' + operation + '"'
			# screen
			screen = str(sateraito_func.noneToZeroStr(row.screen))
			csv_string += ',"' + screen + '"'
			# full_path_folder
			full_path_folder = str(sateraito_func.escapeForCsv(row.full_path_folder))
			csv_string += ',"' + full_path_folder + '"'
			# file_name
			if len(row.list_file_name) > 0:
				file_name = str(sateraito_func.escapeForCsv('; '.join(row.list_file_name)))
				csv_string += ',"' + file_name + '"'
			elif row.file_name is not None and row.file_name != '':
				file_name = str(sateraito_func.escapeForCsv(row.file_name))
				csv_string += ',"' + file_name + '"'
			else:
				csv_string += ',""'

			# workflow_doc_title
			workflow_doc_title = str(sateraito_func.escapeForCsv(row.workflow_doc_title))
			if row.workflow_doc_title is not None and row.workflow_doc_title != '':
				csv_string += ',"' + workflow_doc_title + '"'
			else:
				csv_string += ',""'
			csv_string += '\r\n'

		logging.info('num_rows=' + str(len(rows)))
		return csv_string


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/operationlog/exportoperationloglistcsvadmin',
									 view_func=ExportOperationLogListCsvAdmin.as_view('OperationLogExportOperationLogListCsvAdmin'))

	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/operationlog/getoperationloglistadmin',
									 view_func=GetOperationLogListAdmin.as_view('OperationLogGetOperationLogListAdmin'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/operationlog/oid/getoperationloglistadmin',
									 view_func=GetOperationLogListAdminOid.as_view('OperationLogGetOperationLogListAdminOid'))
