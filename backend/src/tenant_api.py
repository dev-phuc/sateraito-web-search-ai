#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
@file: tenant.py
@brief: Tenant API

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

from dateutil.relativedelta import relativedelta

import sateraito_func
from sateraito_logger import logging
from sateraito_page import Handler_Basic_Request, _BasePage
from sateraito_db import GoogleAppsDomainEntry, OtherSetting
from sateraito_inc import DEFAULT_TIMEZONE, DEFAULT_LANGUAGE, DEFAULT_ENCODING

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass


class _GetTenantConfig(Handler_Basic_Request, _BasePage):
	def process(self, tenant, app_id):
		contract_information = {
			'tenant': tenant,
			'app_id': app_id,
			'cancel_date': '',
			'charge_start_date': '',
			'target_link_domains': '',
			'mail_address': '',
			'tel_no': '',
		}
		llm_quota = {
			'quota': 0,
			'used': 0,
			'last_reset': '',
			'next_reset': '',
		}
		
		other_setting = {
			'csv_file_encoding': '',
			'timezone': '',
			'language': '',
		}
		
		# get contract information
		tenant_dict = GoogleAppsDomainEntry.getDict(tenant)
		if tenant_dict:
			contract_information['cancel_date'] = tenant_dict.get('cancel_date', '')
			contract_information['available_start_date'] = tenant_dict.get('available_start_date', '')
			contract_information['charge_start_date'] = tenant_dict.get('charge_start_date', '')
			contract_information['target_link_domains'] = tenant_dict.get('target_link_domains', '')
			contract_information['mail_address'] = tenant_dict.get('contact_mail_address', '')
			contract_information['tel_no'] = tenant_dict.get('contact_tel_no', '')

			# get llm quota
			llm_quota['quota'] = tenant_dict.get('llm_quota_monthly', 0)
			llm_quota['used'] = tenant_dict.get('llm_quota_used', 0)
			llm_quota['last_reset'] = sateraito_func.toShortLocalDate(tenant_dict.get('llm_quota_last_reset'))

			# calculate next reset date
			if tenant_dict.get('llm_quota_last_reset'):
				next_reset = tenant_dict.get('llm_quota_last_reset') + relativedelta(months=1)
				llm_quota['next_reset'] = sateraito_func.toShortLocalDate(next_reset)

		# Other settings
		other_setting_dict = OtherSetting.getDict(tenant)
		if other_setting_dict:
			other_setting['csv_file_encoding'] = other_setting_dict.get('csv_file_encoding', DEFAULT_ENCODING)
			other_setting['timezone'] = other_setting_dict.get('timezone', DEFAULT_TIMEZONE)
			other_setting['language'] = other_setting_dict.get('language', DEFAULT_LANGUAGE)

		return self.json_response({
			'contract_information': contract_information,
			'llm_quota': llm_quota,
			'other_setting': other_setting,
		})

class GetTenantConfig(_GetTenantConfig):
	def doAction(self, tenant, app_id):
		# set namespace
		if not sateraito_func.setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)
	
class OidGetTenantConfig(_GetTenantConfig):
	def doAction(self, tenant, app_id):
		# set namespace
		if not sateraito_func.setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkOidRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)


def add_url_rules(app):
	app.add_url_rule('/<string:tenant>/<string:app_id>/tenant-config', methods=['GET'],
									view_func=GetTenantConfig.as_view('GetTenantConfig'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/tenant-config', methods=['GET'],
									view_func=OidGetTenantConfig.as_view('OidGetTenantConfig'))
