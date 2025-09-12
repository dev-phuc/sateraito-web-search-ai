#!/usr/bin/python
# coding: utf-8

__author__ = 'PhucLeo <phuc@vnd.sateraito.co.jp>'
'''
client_websites.py

@since: 2025-09-03
@version: 1.0.0
@author: PhucLeo
'''

import requests
import json

from firebase_admin import auth, db
from google.appengine.api import namespace_manager

import sateraito_inc
import sateraito_func
import sateraito_page

from sateraito_logger import logging
from sateraito_db import ClientWebsites

from sateraito_inc import flask_docker
if flask_docker:
	# import memcache, taskqueue
	pass
else:
	# from google.appengine.api import memcache, taskqueue
	pass

# CRUD for ClientWebsites

# Fetch method
class _FetchClientWebsites(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def process(self, tenant, app_id):
		try:
			# Get client params
			status_filter = self.request.args.get('status', None)
			ai_enabled_filter = self.request.args.get('ai_enabled', None)

			# get all active client websites
			client_websites_dict_list = ClientWebsites.fetchDictList(ai_enabled=ai_enabled_filter, status=status_filter)
			result = []
			for cw in client_websites_dict_list:
				result.append({
					'id': cw.get('id', ''),
					'domain': cw.get('domain', ''),
					'favicon_url': cw.get('favicon_url', ''),
					'site_name': cw.get('site_name', ''),
					'description': cw.get('description', ''),
					'ai_enabled': cw.get('ai_enabled', True),
					'status': cw.get('status', sateraito_inc.STATUS_CLIENT_WEBSITES_ACTIVE),
					'created_date': sateraito_func.toShortLocalTime(cw.get('created_date')),
					'updated_date': sateraito_func.toShortLocalTime(cw.get('updated_date')),
				})

			return self.json_response(result)
		
		except Exception as e:
			logging.exception('Error in GetClientWebsites.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class FetchClientWebsites(_FetchClientWebsites):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id)

class OidFetchClientWebsites(_FetchClientWebsites):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)
		
		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id)

# Create method
class _CreateClientWebsites(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def validate_params(self):
		# Get params
		domain = self.request.json.get('domain', '').strip()
		favicon_url = self.request.json.get('favicon_url', '').strip()
		site_name = self.request.json.get('site_name', '').strip()
		description = self.request.json.get('description', '')
		ai_enabled = self.request.json.get('ai_enabled', True)
		status = self.request.json.get('status', sateraito_inc.STATUS_CLIENT_WEBSITES_ACTIVE)

		if not domain:
			return False, 'domain_is_required', None

		# check if domain already exists
		if ClientWebsites.isExists(domain):
			return False, 'domain_already_exists', None
		
		if description:
			description = description.strip()
		
		return True, None, {
			'domain': domain,
			'favicon_url': favicon_url,
			'site_name': site_name,
			'description': description,
			'ai_enabled': ai_enabled,
			'status': status,
		}

	def process(self, tenant, app_id):
		try:
			is_valid, msg_error, params = self.validate_params()

			if not is_valid:
				return self.json_response({'message': msg_error}, status=400)
			
			domain = params.get('domain')
			favicon_url = params.get('favicon_url')
			site_name = params.get('site_name')
			description = params.get('description')
			ai_enabled = params.get('ai_enabled')
			status = params.get('status')

			logging.info('Creating ClientWebsites for domain: %s', namespace_manager.get_namespace())

			# create new ClientWebsites entity
			cw = ClientWebsites(
				domain=domain,
				favicon_url=favicon_url,
				site_name=site_name,
				description=description,
				ai_enabled=ai_enabled,
				status=status,
				created_by=self.viewer_email,
			)
			cw.put()

			return self.json_response({
				'id': str(cw.key.id()),
				'domain': cw.domain,
				'favicon_url': cw.favicon_url,
				'site_name': cw.site_name,
				'description': cw.description,
				'ai_enabled': cw.ai_enabled,
				'status': cw.status,
				'created_date': sateraito_func.toShortLocalTime(cw.created_date),
				'updated_date': sateraito_func.toShortLocalTime(cw.updated_date),
			}, status=201)
		
		except Exception as e:
			logging.exception('Error in CreateClientWebsites.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class CreateClientWebsites(_CreateClientWebsites):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id)
	
class OidCreateClientWebsites(_CreateClientWebsites):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)
		
		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id)

# Edit method
class _EditClientWebsites(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def validate_params(self, id):
		# Get params
		favicon_url = self.request.json.get('favicon_url', '').strip()
		site_name = self.request.json.get('site_name', '').strip()
		description = self.request.json.get('description', '')
		ai_enabled = self.request.json.get('ai_enabled', True)
		status = self.request.json.get('status', sateraito_inc.STATUS_CLIENT_WEBSITES_ACTIVE)

		if not id:
			return False, 'id_is_required', None

		cw = ClientWebsites.get_by_id(id)
		if not cw:
			return False, 'client_website_not_found', None

		if description:
			description = description.strip()

		return True, None, {
			'cw': cw,
			'favicon_url': favicon_url,
			'site_name': site_name,
			'description': description,
			'ai_enabled': ai_enabled,
			'status': status,
		}

	def process(self, tenant, app_id, id):
		try:
			is_valid, msg_error, params = self.validate_params(id)

			if not is_valid:
				return self.json_response({'message': msg_error}, status=400)

			cw = params.get('cw')
			favicon_url = params.get('favicon_url')
			site_name = params.get('site_name')
			description = params.get('description')
			ai_enabled = params.get('ai_enabled')
			status = params.get('status')

			logging.info('Editing ClientWebsites id: %s, tenant: %s', cw.key.id(), namespace_manager.get_namespace())

			# update ClientWebsites entity
			ClientWebsites.updateRow(cw.domain, site_name, description, favicon_url, ai_enabled, status, self.viewer_email)

			return self.json_response({
				'id': str(cw.key.id()),
				'domain': cw.domain,
				'favicon_url': cw.favicon_url,
				'site_name': cw.site_name,
				'description': cw.description,
				'ai_enabled': cw.ai_enabled,
				'status': cw.status,
				'created_date': sateraito_func.toShortLocalTime(cw.created_date),
				'updated_date': sateraito_func.toShortLocalTime(cw.updated_date),
			})

		except Exception as e:
			logging.exception('Error in EditClientWebsites.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class EditClientWebsites(_EditClientWebsites):

	def doAction(self, tenant, app_id, id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id, id)

class OidEditClientWebsites(_EditClientWebsites):

	def doAction(self, tenant, app_id, id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id, id)

# Delete method
class _DeleteClientWebsites(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def process(self, tenant, app_id, id):
		try:
			if not id:
				return self.json_response({'message': 'id_is_required'}, status=400)

			cw = ClientWebsites.get_by_id(id)
			if not cw:
				return self.json_response({'message': 'client_website_not_found'}, status=404)

			logging.info('Deleting ClientWebsites id: %s, tenant: %s', cw.key.id(), namespace_manager.get_namespace())

			cw.key.delete()

			return self.json_response({'message': 'deleted'}, status=200)

		except Exception as e:
			logging.exception('Error in DeleteClientWebsites.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)

class DeleteClientWebsites(_DeleteClientWebsites):

	def doAction(self, tenant, app_id, id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check openid login
		if not self.checkGadgetRequest(tenant):
			return

		return self.process(tenant, app_id, id)

class OidDeleteClientWebsites(_DeleteClientWebsites):

	def doAction(self, tenant, app_id, id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# check request
		if not self.checkOidRequest(tenant):
			return

		return self.process(tenant, app_id, id)


# Get token firebase for client websites
class _ClientGetFirebaseToken(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def process(self, tenant, app_id):
		try:
			
			# Check client website domain
			if not hasattr(self, 'client_website_domain') or not self.client_website_domain:
				return self.json_response({'message': 'unauthorized'}, status=401)

			additional_claims = {
				'tenant': tenant,
				'app_id': app_id,
				'client_website_uid': self.client_website_uid,
				'client_website_domain': self.client_website_domain,
			}
			firebase_custom_token = auth.create_custom_token(self.client_website_domain, additional_claims)
			
			return self.json_response({
				'token': firebase_custom_token.decode('utf-8')
			})

		except Exception as e:
			logging.exception('Error in GetFirebaseTokenForClientWebsites.process: %s', str(e))
			return self.json_response({'message': 'internal_server_error'}, status=500)
		
class ClientGetFirebaseToken(_ClientGetFirebaseToken):

	def doAction(self, tenant, app_id):
		# set namespace
		namespace_manager.set_namespace(tenant)

		# Verify bearer token
		if not self.verifyBearerToken(tenant):
			return

		return self.process(tenant, app_id)


def add_url_rules(app):
	app.add_url_rule('/<string:tenant>/<string:app_id>/client_websites', methods=['GET'],
									view_func=FetchClientWebsites.as_view('ClientWebsites'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/client_websites', methods=['GET'],
									view_func=OidFetchClientWebsites.as_view('OidFetchClientWebsites'))

	app.add_url_rule('/<string:tenant>/<string:app_id>/client_websites', methods=['POST'],
									view_func=CreateClientWebsites.as_view('CreateClientWebsites'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/client_websites', methods=['POST'],
									view_func=OidCreateClientWebsites.as_view('OidCreateClientWebsites'))

	app.add_url_rule('/<string:tenant>/<string:app_id>/client_websites/<int:id>', methods=['PUT'],
									view_func=EditClientWebsites.as_view('EditClientWebsites'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/client_websites/<int:id>', methods=['PUT'],
									view_func=OidEditClientWebsites.as_view('OidEditClientWebsites'))
	
	app.add_url_rule('/<string:tenant>/<string:app_id>/client_websites/<int:id>', methods=['DELETE'],
									view_func=DeleteClientWebsites.as_view('DeleteClientWebsites'))
	app.add_url_rule('/<string:tenant>/<string:app_id>/oid/client_websites/<int:id>', methods=['DELETE'],
									view_func=OidDeleteClientWebsites.as_view('OidDeleteClientWebsites'))
	
	app.add_url_rule('/<string:tenant>/<string:app_id>/client/client_websites/firebase_token', methods=['GET'],
									view_func=ClientGetFirebaseToken.as_view('ClientGetFirebaseToken'))
