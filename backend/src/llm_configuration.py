#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
@file: llm_configuration.py
@brief: LLM Configuration API

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

import sateraito_func
from sateraito_logger import logging
from sateraito_db import LLMConfiguration
from sateraito_page import Handler_Basic_Request, _BasePage

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass

from sateraito_inc import LLM_CONFIGURATION_DEFAULT

# CRUD for LLMConfiguration

# Get method
class _GetLLMConfiguration(Handler_Basic_Request, _BasePage):

	def process(self, tenant, app_id):
		try:
			# Get params

			# get llm configuration
			entity_dict = LLMConfiguration.getDict(auto_create=True)

			llm_config = LLM_CONFIGURATION_DEFAULT

			if entity_dict:
				try:
					enabled_domain_filter = entity_dict.get('enabled_domain_filter', LLM_CONFIGURATION_DEFAULT['enabled_domain_filter'])
					search_domain_filter = entity_dict.get('search_domain_filter', LLM_CONFIGURATION_DEFAULT['search_domain_filter'])
					excluded_domain_filter = entity_dict.get('excluded_domain_filter', LLM_CONFIGURATION_DEFAULT['excluded_domain_filter'])
					
					llm_config = {
						'model_name': entity_dict.get('model_name', LLM_CONFIGURATION_DEFAULT['model_name']),
						'system_prompt': entity_dict.get('system_prompt', LLM_CONFIGURATION_DEFAULT['system_prompt']),
						'response_length_level': entity_dict.get('response_length_level', LLM_CONFIGURATION_DEFAULT['response_length_level']),
						'max_characters': entity_dict.get('max_characters'),
						'enabled_domain_filter': enabled_domain_filter,
						'search_domain_filter': search_domain_filter,
						'excluded_domain_filter': excluded_domain_filter,
					}
				except Exception as e:
					logging.exception('Error parsing LLMConfiguration design JSON: %s', str(e))

			return self.json_response({
				'message': 'success',
				'config': llm_config
			})
		
		except Exception as e:
			logging.exception('Error in GetLLMConfiguration.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class GetLLMConfiguration(_GetLLMConfiguration):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)

class OidGetLLMConfiguration(_GetLLMConfiguration):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)
		
		# check request
		if not self.checkOidRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)

class ClientGetLLMConfiguration(_GetLLMConfiguration):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		if not self.verifyBearerToken(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)
		
		return self.process(tenant, app_id)

# Edit method
class _EditLLMConfiguration(Handler_Basic_Request, _BasePage):

	def validate_params(self):
		# Get params
		config = self.request.json.get('config', {})

		# Validate params config with llm configuration default
		if not isinstance(config, dict):
			return False, 'llm_configuration_invalid_config', None
		for key, value in LLM_CONFIGURATION_DEFAULT.items():
			if key not in config:
				return False, 'llm_configuration_invalid_config', None
			if not isinstance(config[key], type(value)):
				return False, 'llm_configuration_invalid_config', None
		
		# All params are valid
		return True, None, config

	def process(self, tenant, app_id):
		try:
			is_valid, msg_error, config = self.validate_params()

			if not is_valid:
				return self.json_response({'message': msg_error}, status=400)
			
			# Params
			model_name = config.get('model_name', LLM_CONFIGURATION_DEFAULT['model_name'])
			system_prompt = config.get('system_prompt', LLM_CONFIGURATION_DEFAULT['system_prompt'])
			response_length_level = config.get('response_length_level', LLM_CONFIGURATION_DEFAULT['response_length_level'])
			max_characters = config.get('max_characters')
			enabled_domain_filter = config.get('enabled_domain_filter', LLM_CONFIGURATION_DEFAULT['enabled_domain_filter'])
			search_domain_filter = config.get('search_domain_filter', LLM_CONFIGURATION_DEFAULT['search_domain_filter'])
			excluded_domain_filter = config.get('excluded_domain_filter', LLM_CONFIGURATION_DEFAULT['excluded_domain_filter'])
			
			# Update llm configuration
			LLMConfiguration.updateConfig(
				model_name=model_name,
				system_prompt=system_prompt,
				response_length_level=response_length_level,
				max_characters=max_characters,
				enabled_domain_filter=enabled_domain_filter,
				search_domain_filter=search_domain_filter,
				excluded_domain_filter=excluded_domain_filter,
			)

			return self.json_response({'message': 'success'})

		except Exception as e:
			logging.exception('Error in EditLLMConfiguration.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class EditLLMConfiguration(_EditLLMConfiguration):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)

class OidEditLLMConfiguration(_EditLLMConfiguration):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check request
		if not self.checkOidRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)


def add_url_rules(app):
	app.add_url_rule('/<string:tenant>/<string:app_id>/llm-configuration', methods=['GET'],
									view_func=GetLLMConfiguration.as_view('LLMConfiguration'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/llm-configuration', methods=['GET'],
									view_func=OidGetLLMConfiguration.as_view('OidLLMConfiguration'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/client/llm-configuration', methods=['GET'],
									view_func=ClientGetLLMConfiguration.as_view('ClientGetLLMConfiguration'))

	app.add_url_rule('/<string:tenant>/<string:app_id>/llm-configuration', methods=['PUT'],
									view_func=EditLLMConfiguration.as_view('EditLLMConfiguration'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/llm-configuration', methods=['PUT'],
									view_func=OidEditLLMConfiguration.as_view('OidEditLLMConfiguration'))
