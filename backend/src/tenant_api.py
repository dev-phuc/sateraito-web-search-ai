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
			quota = 0
			used = 0
			remaining = 0

			quota = tenant_dict.get('llm_quota_monthly', 0)
			used = tenant_dict.get('llm_quota_used', 0)
			if quota and used:
				remaining = quota - used

			llm_quota['quota'] = quota
			llm_quota['used'] = used
			llm_quota['remaining'] = remaining
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

		result = {
			'contract_information': contract_information,
			'llm_quota': llm_quota,
			'other_setting': other_setting,
		}

		return self.json_response({
			'message': 'success',
			'tenant_config': result
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


class _UpdateContractInfo(Handler_Basic_Request, _BasePage):
	def validate(self, tenant, app_id):
		# Get parameters
		mail_address = self.request.json.get('mail_address', '').strip()
		tel_no = self.request.json.get('tel_no', '').strip()

		# validate mail address
		if mail_address:
			if not sateraito_func.isValidEmail(mail_address):
				return False, 'invalid_mail_address', None
			
		# validate tel no
		if tel_no:
			if len(tel_no) > 50:
				return False, 'invalid_tel_no', None

		return True, '', {
			'mail_address': mail_address,
			'tel_no': tel_no,
		}
	
	def process(self, tenant, app_id):
		# validate parameters
		is_valid, error_message, params = self.validate(tenant, app_id)
		if not is_valid:
			return self.json_response({'message': error_message}, status=400)

		# update contract information
		tenant_entity = GoogleAppsDomainEntry.getInstance(tenant)
		if tenant_entity:
			tenant_entity.contact_mail_address = params['mail_address']
			tenant_entity.contact_tel_no = params['tel_no']
			tenant_entity.put()
		
		return self.json_response({'message': 'success'})
	
class UpdateContractInfo(_UpdateContractInfo):
	def doAction(self, tenant, app_id):
		# set namespace
		if not sateraito_func.setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)
	
class OidUpdateContractInfo(_UpdateContractInfo):
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

	app.add_url_rule('/<string:tenant>/<string:app_id>/tenant-config/update-contract-info', methods=['PUT'],
									view_func=UpdateContractInfo.as_view('UpdateContractInfo'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/tenant-config/update-contract-info', methods=['PUT'],
									view_func=OidUpdateContractInfo.as_view('OidUpdateContractInfo'))
