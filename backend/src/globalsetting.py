#!/usr/bin/python
# coding: utf-8

__author__ = 'Tran Minh Phuc <phuc@vnd.sateraito.co.jp>'
'''
globalsetting.py

@since: 2016-08-01
@version: 2023-09-13
@author: Tran Minh Phuc
'''
from flask import render_template, request, make_response
import json
import sateraito_logger as logging

from google.appengine.ext import ndb
from google.appengine.api import namespace_manager

import sateraito_inc
import sateraito_func
import sateraito_db
import sateraito_page


class _GetGlobalSetting(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	
	def process(self, tenant_or_domain):
		# set header
		self.setResponseHeader('Content-Type', 'application/json')

		# get data
		row_d = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)

		# export json data
		return json.JSONEncoder().encode({
											'status': 'ok',

											# LINE WORKS���ڔF�ؑΉ� 2019.06.13
											'ssogadget_app_key': sateraito_func.none2ZeroStr(row_d.ssogadget_app_key),
											'sso_entity_id': sateraito_func.none2ZeroStr(row_d.sso_entity_id),
											'sso_login_endpoint': sateraito_func.none2ZeroStr(row_d.sso_login_endpoint),
											'sso_public_key': sateraito_func.none2ZeroStr(row_d.sso_public_key),

											'doc_save_terms': row_d.doc_save_terms if row_d.doc_save_terms is not None else 1,		# �ۑ����
											'no_auto_logout': row_d.no_auto_logout if row_d.no_auto_logout is not None else False,
											'no_login_cache': row_d.no_login_cache if row_d.no_login_cache is not None else False,
											'new_ui': row_d.new_ui,
											'new_ui_config': json.loads(row_d.new_ui_config) if row_d.new_ui_config is not None else None,
											'new_ui_afu': row_d.new_ui_afu if row_d.new_ui_afu is not None else False,
											# SameSite�Ή��̈�c��������W���Ƃ���Ή��c���O�C�����̃L���b�V�����I�t�ɂ���I�v�V�����i�������I�v�V�����̑���j 2019.12.23
											'is_preview': row_d.is_preview if row_d.is_preview is not None else True,
											'attached_file_viewer_type': row_d.attached_file_viewer_type if row_d.attached_file_viewer_type is not None else 'GOOGLEDRIVEVIEWER',
											})

class GetGlobalSetting(_GetGlobalSetting):

	def doAction(self, tenant_or_domain):
		# set namespace
		namespace_manager.set_namespace(tenant_or_domain)
		# check gadget request
		if not self.checkGadgetRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)

class OidGetGlobalSetting(_GetGlobalSetting):

	def doAction(self, tenant_or_domain):
		# set namespace
		namespace_manager.set_namespace(tenant_or_domain)
		# check request
		if not self.checkOidRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)


class _UpdateGlobalSettingAdmin(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" for workflow admin only
	"""
	
	def process(self, tenant_or_domain):
		# check if user workflow admin
		if not sateraito_func.isWorkflowAdmin(self.viewer_email, tenant_or_domain, do_not_include_additional_admin=True):
			return

		# get params
		no_auto_logout = sateraito_func.strToBool(self.request.get('no_auto_logout', 'False'))
		no_login_cache = sateraito_func.strToBool(self.request.get('no_login_cache', 'False'))  # SameSite�Ή��̈�c��������W���Ƃ���Ή��c���O�C�����̃L���b�V�����I�t�ɂ���I�v�V�����i�������I�v�V�����̑���j 2019.12.23

		is_preview = sateraito_func.strToBool(self.request.get('is_preview'))
		attached_file_viewer_type = self.request.get('attached_file_viewer_type')

		# save setting
		row_d = sateraito_db.GoogleAppsDomainEntry.getInstance(tenant_or_domain)
		if row_d is None:
			logging.error('GoogleAppsDomainEntry not found')
			return

		row_d.no_auto_logout = no_auto_logout
		row_d.no_login_cache = no_login_cache  # SameSite�Ή��̈�c��������W���Ƃ���Ή��c���O�C�����̃L���b�V�����I�t�ɂ���I�v�V�����i�������I�v�V�����̑���j 2019.12.23
		new_ui = None
		if self.request.get('new_ui') != '':
			new_ui = sateraito_func.strToBool(self.request.get('new_ui', 'False'))
		new_ui_config_raw = self.request.get('new_ui_config', None)
		new_ui_afu = sateraito_func.strToBool(self.request.get('new_ui_afu', 'False'))

		row_d.is_preview = is_preview
		row_d.attached_file_viewer_type = attached_file_viewer_type

		# LINE WORKS���ڔF�ؑΉ��cSAML�֘A�����X�V�i��ݒ肪�����Ă��܂�Ȃ��悤�ɓ��ʋ�ȊO�A�Ƃ���j 2019.06.13
		ssogadget_app_key = self.request.get('ssogadget_app_key')
		sso_entity_id = self.request.get('sso_entity_id')
		sso_login_endpoint = self.request.get('sso_login_endpoint')
		sso_public_key = self.request.get('sso_public_key')
		if ssogadget_app_key != '':
			row_d.ssogadget_app_key = ssogadget_app_key
		if sso_entity_id != '':
			row_d.sso_entity_id = sso_entity_id
		if sso_login_endpoint != '':
			row_d.sso_login_endpoint = sso_login_endpoint
		if sso_public_key != '':
			row_d.sso_public_key = sso_public_key

		row_d.new_ui = new_ui
		row_d.new_ui_afu = new_ui_afu

		new_ui_config = json.JSONDecoder().decode(row_d.new_ui_config) if row_d.new_ui_config is not None else None
		logging.info(new_ui_config)
		if new_ui_config is not None:
			new_ui_config_json = json.JSONDecoder().decode(new_ui_config_raw)
			logging.info(new_ui_config_json)
			new_ui_theme = new_ui_config_json['active']
			new_ui_config['active'] = new_ui_theme
			new_ui_config['themes'][new_ui_theme] = new_ui_config_json['themes'][new_ui_theme]
		else:
			new_ui_config = json.JSONDecoder().decode(new_ui_config_raw)

		row_d.new_ui_config = json.JSONEncoder().encode(new_ui_config)

		#row_d.saveInstance()
		row_d.put()
		return json.JSONEncoder().encode({
											'status': 'ok',
											'error_code': '',
											})

class UpdateGlobalSettingAdmin(_UpdateGlobalSettingAdmin):

	def doAction(self, tenant_or_domain):
		# set namespace
		if not self.setNamespace(tenant_or_domain, ''):
			return
		# check gadget request
		if not self.checkGadgetRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)

class OidUpdateGlobalSettingAdmin(_UpdateGlobalSettingAdmin):

	def doAction(self, tenant_or_domain):
		# set namespace
		if not self.setNamespace(tenant_or_domain, ''):
			return
		# check openid request
		if not self.checkOidRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)


class _GetGlobalUserSetting(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):

	def process(self, tenant_or_domain):
		# set header
		self.setResponseHeader('Content-Type', 'application/json')

		# get data
		row_d = sateraito_db.GoogleAppsUserEntry.getDict(tenant_or_domain, self.viewer_email, auto_create=True)
		logging.info(row_d.get('new_ui_config'))

		# export json data
		return json.JSONEncoder().encode({
			'status': 'ok',
			'new_ui': row_d.get('new_ui') if row_d.get('new_ui') is not None else False,
			'new_ui_config': json.JSONDecoder().decode(row_d.get('new_ui_config')) if row_d.get('new_ui_config') is not None else None,
		})

class GetGlobalUserSetting(_GetGlobalUserSetting):

	def doAction(self, tenant_or_domain):
		# set namespace
		namespace_manager.set_namespace(tenant_or_domain)
		# check gadget request
		if not self.checkGadgetRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)

class OidGetGlobalUserSetting(_GetGlobalUserSetting):

	def doAction(self, tenant_or_domain):
		# set namespace
		namespace_manager.set_namespace(tenant_or_domain)
		# check request
		if not self.checkOidRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)


class _UpdateGlobalUserSetting(sateraito_page.Handler_Basic_Request, sateraito_page._BasePage):
	""" for workflow admin only
	"""

	def process(self, tenant_or_domain):

		# get params
		new_ui = sateraito_func.strToBool(self.request.get('new_ui'))
		new_ui_config_raw = self.request.get('new_ui_config', None)

		logging.info('new ui')
		logging.info(new_ui)

		# save setting
		row_d = sateraito_db.GoogleAppsUserEntry.getInstance(tenant_or_domain, self.viewer_email, auto_create=True)

		new_ui_config = json.JSONDecoder().decode(row_d.new_ui_config) if row_d.new_ui_config is not None else None
		logging.info(new_ui_config)
		if new_ui_config is not None:
			new_ui_config_json = json.JSONDecoder().decode(new_ui_config_raw)
			logging.info(new_ui_config_json)
			new_ui_theme = new_ui_config_json['active']
			new_ui_config['active'] = new_ui_theme
			new_ui_config['themes'][new_ui_theme] = new_ui_config_json['themes'][new_ui_theme]
		else:
			new_ui_config = json.JSONDecoder().decode(new_ui_config_raw)

		row_d.new_ui_config = json.JSONEncoder().encode(new_ui_config)
		row_d.new_ui = new_ui
		row_d.put()

		return json.JSONEncoder().encode({
			'status': 'ok',
			'error_code': '',
		})

class UpdateGlobalUserSetting(_UpdateGlobalUserSetting):

	def doAction(self, tenant_or_domain):
		# set namespace
		if not self.setNamespace(tenant_or_domain, ''):
			return
		# check gadget request
		if not self.checkGadgetRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)

class OidUpdateGlobalUserSetting(_UpdateGlobalUserSetting):

	def doAction(self, tenant_or_domain):
		# set namespace
		if not self.setNamespace(tenant_or_domain, ''):
			return

		# check openid request
		if not self.checkOidRequest(tenant_or_domain):
			return

		return self.process(tenant_or_domain)


def add_url_rules(app):
	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/getglobalsetting',
									 view_func=GetGlobalSetting.as_view('GlobalSettingGetGlobalSetting'))
	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/oid/getglobalsetting',
									 view_func=OidGetGlobalSetting.as_view('GlobalSettingOidGetGlobalSetting'))

	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/updateglobalsettingadmin',
									 view_func=UpdateGlobalSettingAdmin.as_view('GlobalSettingUpdateGlobalSettingAdmin'))
	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/oid/updateglobalsettingadmin',
									 view_func=OidUpdateGlobalSettingAdmin.as_view('GlobalSettingOidUpdateGlobalSettingAdmin'))

	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/getglobalusersetting',
									 view_func=GetGlobalUserSetting.as_view('GlobalSettingGetGlobalUserSetting'))
	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/oid/getglobalusersetting',
									 view_func=OidGetGlobalUserSetting.as_view('GlobalSettingOidGetGlobalUserSetting'))

	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/updateglobalusersetting',
									 view_func=UpdateGlobalUserSetting.as_view('GlobalSettingUpdateGlobalUserSetting'))
	app.add_url_rule('/<string:tenant_or_domain>/globalsetting/oid/updateglobalusersetting',
									 view_func=OidUpdateGlobalUserSetting.as_view('GlobalSettingOidUpdateGlobalUserSetting'))

