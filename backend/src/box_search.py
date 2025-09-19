#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
@file: box_search.py
@brief: Box Search Config API

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

import json

import sateraito_func
from sateraito_page import Handler_Basic_Request, _BasePage
from sateraito_logger import logging
from sateraito_db import BoxSearchConfig

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass

from sateraito_inc import BOX_SEARCH_DESIGN_DEFAULT

# CRUD for BoxSearchConfig

# Get method
class _GetBoxSearchConfig(Handler_Basic_Request, _BasePage):

	def process(self, tenant, app_id):
		try:
			# Get params

			box_search_config = BOX_SEARCH_DESIGN_DEFAULT

			# get box search config
			result = BoxSearchConfig.getDict(auto_create=True)
			if result and 'design' in result:
				try:
					box_search_config = result['design']
				except Exception as e:
					logging.exception('Error parsing BoxSearchConfig design JSON: %s', str(e))

			# Str to JSON
			if isinstance(box_search_config, str):
				try:
					box_search_config = json.loads(box_search_config)
				except Exception as e:
					logging.exception('Error loading BoxSearchConfig design JSON: %s', str(e))
					box_search_config = BOX_SEARCH_DESIGN_DEFAULT

			return self.json_response(box_search_config)
		
		except Exception as e:
			logging.exception('Error in GetBoxSearchConfig.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class GetBoxSearchConfig(_GetBoxSearchConfig):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id)

class OidGetBoxSearchConfig(_GetBoxSearchConfig):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)
		
		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id)

class ClientGetBoxSearchConfig(_GetBoxSearchConfig):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		is_check_ok = self.verifyBearerToken(tenant)
		if not is_check_ok:
			return self.json_response({'message': 'forbidden'}, status=403)
		
		return self.process(tenant, app_id)

# Edit method
class _EditBoxSearchConfig(Handler_Basic_Request, _BasePage):

	def validate_params(self):
		# Get params
		config = self.request.json.get('config', {})

		# Validate params config with box search config default
		if not isinstance(config, dict):
			return False, 'box_search_invalid_config', None
		for key, value in BOX_SEARCH_DESIGN_DEFAULT.items():
			if key not in config:
				return False, 'box_search_invalid_config', None
			if not isinstance(config[key], type(value)):
				return False, 'box_search_invalid_config', None
		
		# Encode to JSON text
		try:
			config = json.dumps(config)
		except Exception as e:
			logging.exception('Error encoding config to JSON text: %s', str(e))
			return False, 'box_search_invalid_config', None

		# All params are valid
		return True, None, {
			'config': config
		}

	def process(self, tenant, app_id):
		try:
			is_valid, msg_error, params = self.validate_params()

			if not is_valid:
				return self.json_response({'message': msg_error}, status=400)
			
			# Update box search config
			BoxSearchConfig.updateDesign(params['config'])

			return self.json_response({'message': 'success'})

		except Exception as e:
			logging.exception('Error in EditBoxSearchConfig.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class EditBoxSearchConfig(_EditBoxSearchConfig):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id)

class OidEditBoxSearchConfig(_EditBoxSearchConfig):

	def doAction(self, tenant, app_id):
		if sateraito_func.setNamespace(tenant, app_id) is False:
			return self.json_response({'message': 'namespace_error'}, status=500)

		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id)


def add_url_rules(app):
	app.add_url_rule('/<string:tenant>/<string:app_id>/box_search_config', methods=['GET'],
									view_func=GetBoxSearchConfig.as_view('BoxSearchConfig'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/box_search_config', methods=['GET'],
									view_func=OidGetBoxSearchConfig.as_view('OidBoxSearchConfig'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/client/box_search_config', methods=['GET'],
									view_func=ClientGetBoxSearchConfig.as_view('ClientGetBoxSearchConfig'))

	app.add_url_rule('/<string:tenant>/<string:app_id>/box_search_config', methods=['PUT'],
									view_func=EditBoxSearchConfig.as_view('EditBoxSearchConfig'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/box_search_config', methods=['PUT'],
									view_func=OidEditBoxSearchConfig.as_view('OidEditBoxSearchConfig'))
