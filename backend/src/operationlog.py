#!/usr/bin/python
# coding: utf-8
__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
@file: operationlog.py
@brief: Operation Log API

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

import datetime

import sateraito_func
import sateraito_page

from sateraito_db import OperationLog
from sateraito_logger import logging
from sateraito_func import toUtcTime

class __GetOperationLogListAdmin(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	
	def getRows(self, page, limit, client_domain, from_date_localtime_raw, to_date_localtime_raw):
		q = OperationLog.query()
		
		# Get total rows
		total_rows = q.count()
		
		# from_date
		if from_date_localtime_raw and from_date_localtime_raw.strip() != '':
			from_date_localtime = None
			f_split = from_date_localtime_raw.split(' ')
			if len(f_split) == 1:
				# in case YYYY-MM-DD
				from_date_localtime = datetime.datetime.strptime(from_date_localtime_raw + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
			else:
				# in case YYYY-MM-DD HH:MI
				from_date_localtime = datetime.datetime.strptime(from_date_localtime_raw + ':00', '%Y-%m-%d %H:%M:%S')
			from_date_utc = toUtcTime(from_date_localtime)
			q = q.filter(OperationLog.created_date >= from_date_utc)
		# to_date
		if to_date_localtime_raw and to_date_localtime_raw.strip() != '':
			to_date_localtime = None
			t_split = to_date_localtime_raw.split(' ')
			if len(t_split) == 1:
				# in case YYYY-MM-DD
				to_date_localtime = datetime.datetime.strptime(to_date_localtime_raw + ' 00:00:00', '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=1)
			else:
				# in case YYYY-MM-DD HH:MI
				to_date_localtime = datetime.datetime.strptime(to_date_localtime_raw + ':00', '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=1)
			to_date_utc = toUtcTime(to_date_localtime)
			q = q.filter(OperationLog.created_date < to_date_utc)
		# client_domain
		if client_domain != '':
			q = q.filter(OperationLog.client_domain == client_domain)
		
		# sort order
		q = q.order(-OperationLog.created_date)
		
		# paging
		limit = int(limit)
		page = int(page)
		if limit <= 0:
			limit = 50
		if page <= 0:
			page = 1

		row_start = (page - 1) * limit
		row_end = row_start + limit

		# get rows
		rows = q.fetch(limit, offset=row_start)
		row_next = q.fetch(1, offset=row_end)

		have_more_rows = False
		if len(row_next) > 0:
			have_more_rows = True

		return total_rows, rows, have_more_rows

class _GetOperationLogListAdmin(__GetOperationLogListAdmin):
	""" Get list of all doc types in system
		for admin only
	"""
	
	def process(self, google_apps_domain, app_id):
		# check if user workflow admin
		if not sateraito_func.isWorkflowAdmin(self.viewer_email, google_apps_domain, app_id):
			return
		
		# get params
		page = self.request.get('page', 1)
		limit = self.request.get('limit', 50)
		from_date_localtime_raw = self.request.get('from_date')
		to_date_localtime_raw = self.request.get('to_date')
		client_domain = self.request.get('client_domain')

		# get data
		total_rows, rows, have_more_rows = self.getRows(page, limit, client_domain, from_date_localtime_raw, to_date_localtime_raw)
		
		data = []
		for row in rows:
			data.append({
				'tenant': row.tenant,
				'app_id': row.app_id,
				'client_domain': row.client_domain,
				'unique_id': row.unique_id,
				'stream_path': row.stream_path,
				
				'prompt': row.prompt,
				'model_name': row.model_name,
				'system_prompt': row.system_prompt,

				'response': row.response,
				'metadata': row.metadata,
				'response_length': row.response_length,

				'status': row.status,
				'error_message': row.error_message,

				'created_date': sateraito_func.toShortLocalTime(row.created_date),
			})

		return self.json_response({
			'operation_logs': data,
			'total_rows': total_rows,
			'have_more_rows': have_more_rows,
		})

class GetOperationLogListAdmin(_GetOperationLogListAdmin):
	""" Get list of all doc types in system
		for admin only
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return self.json_response({'message': 'app_not_configured'}, status=404)
		# check request
		if not self.checkGadgetRequest(google_apps_domain):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(google_apps_domain, app_id)

class GetOperationLogListAdminOid(_GetOperationLogListAdmin):
	""" Get list of all doc types in system
		for admin only
	"""

	def doAction(self, google_apps_domain, app_id):
		# set namespace
		if not self.setNamespace(google_apps_domain, app_id):
			return self.json_response({'message': 'app_not_configured'}, status=404)
		# check request
		if not self.checkOidRequest(google_apps_domain):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(google_apps_domain, app_id)


def add_url_rules(app):
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/operation-log', methods=['GET'],
									view_func=GetOperationLogListAdmin.as_view('GetOperationLogListAdmin'))
	app.add_url_rule('/<string:google_apps_domain>/<string:app_id>/oid/operation-log', methods=['GET'],
									view_func=GetOperationLogListAdminOid.as_view('GetOperationLogListAdminOid'))
