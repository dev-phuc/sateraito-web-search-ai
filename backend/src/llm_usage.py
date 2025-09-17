#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
@file: llm_usage.py
@brief: LLM Usage API

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import sateraito_page
import sateraito_func

from sateraito_logger import logging

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass

from sateraito_db import GoogleAppsDomainEntry, LLMUsageLog

# Fetch LLM usage
class _FetchLLMUsage(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	def get_start_of_this_year(self):
		now = datetime.utcnow()
		start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
		return start_of_year, now
	
	def get_start_of_last_year(self):
		now = datetime.utcnow()
		start_of_this_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
		start_of_last_year = start_of_this_year - relativedelta(years=1)
		return start_of_last_year, start_of_this_year
	
	def get_start_of_last_month(self):
		now = datetime.utcnow()
		first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		last_month_end = first_of_this_month - timedelta(seconds=1)
		first_of_last_month = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		return first_of_last_month, first_of_this_month
	
	def get_start_of_this_month(self):
		now = datetime.utcnow()
		start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		return start_of_month, now
	
	def get_start_of_this_week(self):
		now = datetime.utcnow()
		start_of_week = now - timedelta(days=now.weekday())
		start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
		return start_of_week, now
	
	def get_start_of_this_day(self):
		now = datetime.utcnow()
		start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
		return start_of_day, now
	
	def build_query_time_frame(self, time_frame):
		query = LLMUsageLog.query(LLMUsageLog.name_log == 'web-search-ai')

		# get llm usage
		timestamp_start = None
		timestamp_end = None
		if time_frame == 'last_year':
			timestamp_start, timestamp_end = self.get_start_of_last_year()
		elif time_frame == 'year':
			timestamp_start, timestamp_end = self.get_start_of_this_year()
		elif time_frame == 'last_month':
			timestamp_start, timestamp_end = self.get_start_of_last_month()
		elif time_frame == 'month':
			timestamp_start, timestamp_end = self.get_start_of_this_month()
		elif time_frame == 'week':
			timestamp_start, timestamp_end = self.get_start_of_this_week()
		elif time_frame == 'day':
			timestamp_start, timestamp_end = self.get_start_of_this_day()

		# Apply time filter
		if timestamp_start and timestamp_end:
			query = query.filter(LLMUsageLog.timestamp >= timestamp_start, LLMUsageLog.timestamp < timestamp_end)

		return query

	def process(self, tenant, app_id):
		try:
			# Get params from params request
			time_frame = self.request.args.get('time_frame', 'month').lower()

			# Validate time_frame
			if time_frame not in ['all', 'last_year', 'year', 'last_month', 'month', 'week', 'day']:
				time_frame = 'month'

			usage_list = []
			query = self.build_query_time_frame(time_frame)
			for usage in query.order(-LLMUsageLog.timestamp).fetch(1000):
				usage_list.append({
					'timestamp': sateraito_func.toShortLocalTime(usage.timestamp),
					'model_name': usage.model_name,
					'prompt_length': usage.prompt_length,
					'completion_length': usage.completion_length,
					'total_length': usage.total_length,
				})

			# Get google apps domain
			domain_entity = GoogleAppsDomainEntry.getDict(google_apps_domain=tenant)
			if not domain_entity:
				return self.json_response({'message': 'domain_not_found'}, status=404)
			
			llm_quota_monthly = domain_entity.get('llm_quota_monthly', 0)
			llm_quota_used = domain_entity.get('llm_quota_used', 0)
			llm_quota_remaining = max(0, llm_quota_monthly - llm_quota_used)
			llm_quota_last_reset = domain_entity.get('llm_quota_last_reset', '')

			result = {
				'llm_quota_monthly': llm_quota_monthly,
				'llm_quota_used': llm_quota_used,
				'llm_quota_remaining': llm_quota_remaining,
				'llm_quota_last_reset': llm_quota_last_reset,
				'usage_list': usage_list,
			}
			return self.json_response(result)
		except Exception as e:
			logging.exception('Error in FetchLLMUsage.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)
		
class FetchLLMUsage(_FetchLLMUsage):
	def doAction(self, tenant, app_id):
		# set namespace
		if not sateraito_func.setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id)
	
class OidFetchLLMUsage(_FetchLLMUsage):
	def doAction(self, tenant, app_id):
		# set namespace
		if not sateraito_func.setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)
		
		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id)

def add_url_rules(app):
	app.add_url_rule('/<string:tenant>/<string:app_id>/llm-usage', methods=['GET'],
									view_func=FetchLLMUsage.as_view('FetchLLMUsage'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/llm-usage', methods=['GET'],
									view_func=OidFetchLLMUsage.as_view('OidFetchLLMUsage'))
	