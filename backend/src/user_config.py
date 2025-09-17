#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
@file: user_config.py
@brief: User Configuration API

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

import json

import sateraito_page

from sateraito_logger import logging
from sateraito_db import UserInfo, UserConfig
from sateraito_func import setNamespace

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass

from sateraito_inc import DEFAULT_LANGUAGE, THEME_CONFIG_DEFAULT

# CRUD for UserConfig

# Get method
class _GetUserConfiguration(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def process(self, tenant, app_id):
		try:
			# Get params

			# get user configuration
			user_config = UserConfig.getDict(self.viewer_email, auto_create=True)
			if not user_config:
				return self.json_response({'message': 'user_not_found'}, status=404)
			
			# get user info
			language = DEFAULT_LANGUAGE
			user_info = UserInfo.getInstance(self.viewer_email, auto_create=True)
			if user_info:
				language = user_info.language if user_info.language else DEFAULT_LANGUAGE
			
			result = {
				'language': language,
				'config': THEME_CONFIG_DEFAULT
			}

			try:
				theme_config = user_config.get('theme_config')
				if theme_config:
					theme_config_dict = json.loads(theme_config)
					# Merge with default config
					for key, value in THEME_CONFIG_DEFAULT.items():
						if key in theme_config_dict and isinstance(theme_config_dict[key], type(value)):
							result['config'][key] = theme_config_dict[key]
			except Exception as e:
				logging.exception('Error parsing UserConfig theme_config JSON: %s', str(e))

			return self.json_response(result)
		
		except Exception as e:
			logging.exception('Error in GetUserConfiguration.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class GetUserConfiguration(_GetUserConfiguration):

	def doAction(self, tenant, app_id):
		if not setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)
		
		# check openid login
		if not self.checkGadgetRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)

class OidGetUserConfiguration(_GetUserConfiguration):

	def doAction(self, tenant, app_id):
		if not setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)
		
		# check request
		if not self.checkOidRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)

# Update method
class _UpdateUserConfiguration(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def validate_params(self):
		# Get params
		language = self.request.json.get('language')
		config = self.request.json.get('config', {})

		# Validate params config with llm configuration default
		if not isinstance(config, dict):
			return False, 'invalid_config', None
		for key, value in THEME_CONFIG_DEFAULT.items():
			if key not in config:
				return False, 'invalid_config', None
			if not isinstance(config[key], type(value)):
				return False, 'invalid_config', None
		
		# All params are valid
		return True, None, { 'language': language, 'config': config }

	def process(self, tenant, app_id):
		try:
			is_valid, msg_error, params_valid = self.validate_params()

			if not is_valid:
				return self.json_response({'message': msg_error}, status=400)
			
			# Params
			config = params_valid.get('config', {})
			language = params_valid.get('language', 'en')
			
			# Update user configuration
			user_config = UserConfig.getInstance(self.viewer_email, auto_create=True)
			if not user_config:
				return self.json_response({'message': 'user_not_found'}, status=404)
			
			# Save theme config
			user_config.theme_config = json.dumps(config)
			user_config.put()

			# Update user language
			user_info = UserInfo.getInstance(self.viewer_email, auto_create=True)
			if user_info:
				user_info.language = language
				user_info.put()

			return self.json_response({'message': 'success'})

		except Exception as e:
			logging.exception('Error in UpdateUserConfiguration.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class UpdateUserConfiguration(_UpdateUserConfiguration):

	def doAction(self, tenant, app_id):
		if not setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)

class OidUpdateUserConfiguration(_UpdateUserConfiguration):

	def doAction(self, tenant, app_id):
		if not setNamespace(tenant, app_id):
			return self.json_response({'message': 'namespace_error'}, status=500)
		
		# check request
		if not self.checkOidRequest(tenant):
			return self.json_response({'message': 'forbidden'}, status=403)

		return self.process(tenant, app_id)


def add_url_rules(app):
	app.add_url_rule('/<string:tenant>/<string:app_id>/user-config', methods=['GET'],
									view_func=GetUserConfiguration.as_view('GetUserConfiguration'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/user-config', methods=['GET'],
									view_func=OidGetUserConfiguration.as_view('OidGetUserConfiguration'))

	app.add_url_rule('/<string:tenant>/<string:app_id>/user-config', methods=['PUT'],
									view_func=UpdateUserConfiguration.as_view('UpdateUserConfiguration'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/user-config', methods=['PUT'],
									view_func=OidUpdateUserConfiguration.as_view('OidUpdateUserConfiguration'))
