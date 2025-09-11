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

import requests
import json

from google.appengine.api import namespace_manager

import sateraito_inc
import sateraito_func
import sateraito_page

from sateraito_logger import logging
from sateraito_db import LLMConfiguration

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
class _GetLLMConfiguration(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def process(self, tenant, app_id):
		try:
			# Get params

			# get llm configuration
			entity_dict = LLMConfiguration.getDict(auto_create=True)

			result = LLM_CONFIGURATION_DEFAULT

			if entity_dict:
				try:
					result = {
						'model_name': entity_dict.get('model_name', LLM_CONFIGURATION_DEFAULT['model_name']),
						'system_prompt': entity_dict.get('system_prompt', LLM_CONFIGURATION_DEFAULT['system_prompt']),
						'response_length_level': entity_dict.get('response_length_level', LLM_CONFIGURATION_DEFAULT['response_length_level']),
						'max_characters': entity_dict.get('max_characters', LLM_CONFIGURATION_DEFAULT['max_characters']),
					}
				except Exception as e:
					logging.exception('Error parsing LLMConfiguration design JSON: %s', str(e))

			return self.json_response(result)
		
		except Exception as e:
			logging.exception('Error in GetLLMConfiguration.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class GetLLMConfiguration(_GetLLMConfiguration):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id)

class OidGetLLMConfiguration(_GetLLMConfiguration):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)
		
		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id)

class ClientGetLLMConfiguration(_GetLLMConfiguration):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		if not self.verifyBearerToken(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)
		
		if not self.verifyClientWebsite(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)
		
		return self.process(tenant, app_id)

# Edit method
class _EditLLMConfiguration(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

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
			
			# Update llm configuration
			LLMConfiguration.updateConfig(
				model_name=model_name,
				system_prompt=system_prompt,
				response_length_level=response_length_level,
				max_characters=max_characters
			)

			return self.json_response({'message': 'success'})

		except Exception as e:
			logging.exception('Error in EditLLMConfiguration.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class EditLLMConfiguration(_EditLLMConfiguration):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id)

class OidEditLLMConfiguration(_EditLLMConfiguration):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check request
		if not self.checkOidRequest(tenant):
			return

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
